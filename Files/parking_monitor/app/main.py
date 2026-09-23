import os
# CPU Optimization: Eliminate OpenMP spin-waiting & limit thread contention
os.environ["OMP_WAIT_POLICY"] = "PASSIVE"
os.environ["KMP_BLOCKTIME"] = "0"
os.environ["OMP_NUM_THREADS"] = "2"
os.environ["MKL_NUM_THREADS"] = "2"

try:
    import torch
    torch.set_num_threads(2)
except Exception:
    pass

try:
    import cv2
    cv2.setNumThreads(2)
except Exception:
    pass

import sys
import time
import shutil
import asyncio
from datetime import datetime
from typing import Dict, Any, List, Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Query, Response, Request
from fastapi.responses import StreamingResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from app.config.settings import SAMPLES_DIR, DATA_DIR, HOST, PORT
from app.db.database import init_db, db_get_sessions
from app.vision.spot_manager import SpotManager
from app.vision.tracker_stats import TrackerStats
from app.vision.vehicle_detector import VehicleDetector
from app.vision.video_stream import VideoStreamManager
from app.utils.device_utils import get_hardware_status
from app.utils.camera_utils import get_real_windows_cameras
from app.utils.report_exporter import generate_csv_report, get_parking_analytics_summary

# Global state instances
spot_manager: Optional[SpotManager] = None
tracker_stats: Optional[TrackerStats] = None
detector: Optional[VehicleDetector] = None
stream_manager: Optional[VideoStreamManager] = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global spot_manager, tracker_stats, detector, stream_manager
    
    # 1. Initialize SQLite Database
    init_db()
    
    # 2. Initialize Vision & Spot Managers
    spot_manager = SpotManager()
    tracker_stats = TrackerStats()
    detector = VehicleDetector(spot_manager=spot_manager, tracker_stats=tracker_stats)

    # 3. Setup VideoStreamManager with background worker thread
    stream_manager = VideoStreamManager(detector=detector)

    sample_files = [
        os.path.join(SAMPLES_DIR, f) for f in os.listdir(SAMPLES_DIR)
        if f.lower().endswith((".mp4", ".avi", ".mkv", ".mov"))
    ] if os.path.exists(SAMPLES_DIR) else []

    if sample_files:
        chosen_sample = sample_files[0]
        for s in sample_files:
            if "camara_fija" in s or "openalpr" in s:
                chosen_sample = s
                break
        stream_manager.set_source(chosen_sample, is_file=True)
    else:
        stream_manager.set_source(0, is_file=False)

    stream_manager.start()

    yield

    if stream_manager:
        stream_manager.stop()

app = FastAPI(title="Smart Parking Vision Monitor", lifespan=lifespan)

# Anti-cache middleware
@app.middleware("http")
async def add_no_cache_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, max-age=0"
    return response

# Pydantic schemas
class SpotCreatePayload(BaseModel):
    id: str
    label: str
    spot_type: str = "car"
    points: List[List[int]]

class SpotUpdatePayload(BaseModel):
    new_id: Optional[str] = None
    label: str
    spot_type: str = "car"

class ExclusionCreatePayload(BaseModel):
    id: str
    label: str
    points: List[List[int]]

class DeviceSelectPayload(BaseModel):
    mode: str

class SourceSelectPayload(BaseModel):
    source_type: str  # "sample", "webcam", "ip"
    source_value: str

# ----------------- VIDEO STREAMING (NON-BLOCKING ASYNC) -----------------
@app.get("/video_feed")
async def video_feed():
    if not stream_manager:
        raise HTTPException(status_code=503, detail="Stream service not ready")
    return StreamingResponse(
        stream_manager.generate_frames(),
        media_type="multipart/x-mixed-replace; boundary=frame"
    )

# ----------------- SPOTS MANAGEMENT -----------------
@app.get("/api/spots")
def get_spots():
    if not spot_manager:
        return []
    return spot_manager.get_all_spots()

@app.post("/api/spots")
def create_or_update_spot(payload: SpotCreatePayload):
    if not spot_manager:
        raise HTTPException(status_code=500, detail="Spot manager not initialized")
    
    spot = spot_manager.add_or_update_spot(
        spot_id=payload.id,
        label=payload.label,
        points=payload.points,
        spot_type=payload.spot_type
    )
    return {"status": "ok", "spot": spot.to_dict()}

@app.delete("/api/spots/{spot_id}")
def delete_spot(spot_id: str):
    if not spot_manager:
        raise HTTPException(status_code=500, detail="Spot manager not initialized")
    deleted = spot_manager.delete_spot(spot_id)
    return {"status": "ok", "deleted": deleted}

@app.put("/api/spots/{spot_id}")
def update_spot(spot_id: str, payload: SpotUpdatePayload):
    if not spot_manager:
        raise HTTPException(status_code=500, detail="Spot manager not initialized")
    target_id = payload.new_id.strip() if payload.new_id else spot_id
    updated = spot_manager.update_spot_metadata(
        old_id=spot_id,
        new_id=target_id,
        new_label=payload.label.strip(),
        new_spot_type=payload.spot_type
    )
    if not updated:
        raise HTTPException(status_code=404, detail="Spot not found")
    return {"status": "ok", "spot": updated.to_dict()}

@app.post("/api/spots/clear")
def clear_all_spots():
    if not spot_manager:
        raise HTTPException(status_code=500, detail="Spot manager not initialized")
    spot_manager.clear_all()
    return {"status": "ok", "message": "All spots cleared"}

@app.post("/api/spots/presets")
def load_preset_spots():
    """Generates 6 starter bays adapted to frame dimensions."""
    if not spot_manager or not stream_manager:
        raise HTTPException(status_code=500, detail="Services not ready")

    w = stream_manager.frame_width or 960
    h = stream_manager.frame_height or 540

    spot_manager.clear_all()

    bay_w = int(w * 0.13)
    bay_h = int(h * 0.35)
    start_x = int(w * 0.08)
    gap = int(w * 0.02)
    y1 = int(h * 0.55)
    y2 = y1 + bay_h

    for i in range(6):
        x1 = start_x + i * (bay_w + gap)
        x2 = x1 + bay_w
        spot_id = f"P-0{i+1}"
        label = f"Bay {i+1}"
        pts = [[x1, y1], [x2, y1], [x2, y2], [x1, y2]]
        spot_manager.add_or_update_spot(spot_id, label, pts, "car")

    return {"status": "ok", "spots": spot_manager.get_all_spots()}

# ----------------- EXCLUSION / MASK ZONES -----------------
@app.get("/api/exclusions")
def get_exclusions():
    if not spot_manager:
        return []
    return spot_manager.get_all_exclusion_zones()

@app.post("/api/exclusions")
def create_or_update_exclusion(payload: ExclusionCreatePayload):
    if not spot_manager:
        raise HTTPException(status_code=500, detail="Spot manager not ready")
    zone = spot_manager.add_or_update_exclusion_zone(
        zone_id=payload.id,
        label=payload.label,
        points=payload.points
    )
    return {"status": "ok", "exclusion": zone.to_dict()}

@app.delete("/api/exclusions/{zone_id}")
def delete_exclusion(zone_id: str):
    if not spot_manager:
        raise HTTPException(status_code=500, detail="Spot manager not ready")
    deleted = spot_manager.delete_exclusion_zone(zone_id)
    return {"status": "ok", "deleted": deleted}

@app.post("/api/exclusions/clear")
def clear_all_exclusions():
    if not spot_manager:
        raise HTTPException(status_code=500, detail="Spot manager not ready")
    spot_manager.clear_all_exclusion_zones()
    return {"status": "ok", "message": "All exclusion zones cleared"}

# ----------------- VIDEO SOURCES -----------------
@app.get("/api/sources")
def list_sources():
    sample_files = []
    if os.path.exists(SAMPLES_DIR):
        for f in os.listdir(SAMPLES_DIR):
            if f.lower().endswith((".mp4", ".avi", ".mkv", ".mov")):
                sample_files.append({"name": f, "path": os.path.join(SAMPLES_DIR, f)})

    webcams = get_real_windows_cameras()
    active_info = stream_manager.get_info() if stream_manager else {}

    return {
        "samples": sample_files,
        "webcams": webcams,
        "active": active_info
    }

@app.post("/api/sources/select")
def select_source(payload: SourceSelectPayload):
    global stream_manager
    if not stream_manager:
        raise HTTPException(status_code=500, detail="Stream service unavailable")

    stype = payload.source_type
    sval = payload.source_value

    if stype == "sample":
        file_path = os.path.join(SAMPLES_DIR, sval) if not os.path.isabs(sval) else sval
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="File not found")
        stream_manager.set_source(file_path, is_file=True)
    elif stype == "webcam":
        try:
            cam_idx = int(sval)
            stream_manager.set_source(cam_idx, is_file=False)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid webcam ID")
    elif stype == "ip":
        if not (sval.startswith("rtsp://") or sval.startswith("http://") or sval.startswith("https://")):
            raise HTTPException(status_code=400, detail="Invalid stream URL")
        stream_manager.set_source(sval, is_file=False)
    else:
        raise HTTPException(status_code=400, detail="Unknown source type")

    return {"status": "ok", "active": stream_manager.get_info()}

@app.post("/api/sources/upload")
async def upload_video(file: UploadFile = File(...)):
    global stream_manager
    os.makedirs(SAMPLES_DIR, exist_ok=True)
    target_path = os.path.join(SAMPLES_DIR, file.filename)
    
    with open(target_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    if stream_manager:
        stream_manager.set_source(target_path, is_file=True)

    return {"status": "ok", "filename": file.filename, "path": target_path}

# ----------------- HARDWARE ACCELERATION -----------------
@app.get("/api/device")
def get_device():
    active_mode = detector.device_preference if detector else "auto"
    status = get_hardware_status(active_mode=active_mode)
    if detector:
        status["effective_mode"] = detector.effective_mode
        status["device_message"] = detector.device_message
    return status

@app.post("/api/device/select")
def set_device(payload: DeviceSelectPayload):
    if not detector:
        raise HTTPException(status_code=500, detail="Detector not ready")
    result = detector.set_device(payload.mode)
    return {"status": "ok", "device": result}

# ----------------- STATS & REPORTS -----------------
@app.get("/api/stats/live")
def get_live_stats():
    if not tracker_stats or not spot_manager:
        return {}
    return tracker_stats.get_kpis(spot_manager)

@app.get("/api/reports/history")
def get_history(limit: int = Query(100, ge=1, le=1000), spot_id: Optional[str] = None):
    return db_get_sessions(limit=limit, spot_id=spot_id)

@app.get("/api/reports/summary")
def get_summary():
    return get_parking_analytics_summary()

@app.get("/api/reports/download-csv")
def download_csv_report():
    csv_content = generate_csv_report()
    filename = f"parking_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )

# ----------------- STATIC FILES & FRONTEND -----------------
STATIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
if os.path.exists(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

@app.get("/")
def index():
    index_file = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return {"message": "Smart Parking Monitor API is running."}
