import os
import cv2
import numpy as np
from typing import Dict, List, Tuple, Any, Optional
from ultralytics import YOLO

from app.config.settings import VEHICLE_CLASSES, CLASS_NAMES, DEFAULT_CONF_THRESHOLD
from app.vision.spot_manager import SpotManager
from app.vision.tracker_stats import TrackerStats
from app.utils.device_utils import resolve_device_config

class VehicleDetector:
    def __init__(self, spot_manager: Optional[SpotManager] = None,
                 tracker_stats: Optional[TrackerStats] = None,
                 conf_threshold: float = DEFAULT_CONF_THRESHOLD,
                 device_pref: str = "auto"):
        self.conf_threshold = conf_threshold
        self.spot_manager = spot_manager or SpotManager()
        self.tracker_stats = tracker_stats or TrackerStats()
        
        # Fast ByteTrack config (uses Ultralytics internal cached tracker instance)
        self.tracker_yaml = "bytetrack.yaml"

        # Optimize inference frequency and threading
        self.frame_index: int = 0
        self.infer_interval: int = 2  # Run neural net inference every 2 frames
        self.cached_vehicles: List[Dict[str, Any]] = []

        # Hardware initialization
        self.device_preference = device_pref
        self.effective_mode = "cpu"
        self.model_path = ""
        self.device_message = ""
        self.model = None
        self.set_device(device_pref)

    def set_device(self, preference: str = "auto") -> Dict[str, Any]:
        """Switches inference compute device between AMD GPU (DirectML), NVIDIA GPU (CUDA), and CPU."""
        import torch
        torch.set_num_threads(2)  # Prevent PyTorch CPU thread saturation

        self.device_preference = preference
        self.effective_mode, self.model_path, self.device_message = resolve_device_config(preference)
        print(f"[Detector] Cargando modelo: '{os.path.basename(self.model_path)}' ({self.effective_mode}) - {self.device_message}")
        
        try:
            self.model = YOLO(self.model_path)
        except Exception as e:
            print(f"[Detector] Error cargando modelo {self.model_path}: {e}. Probando fallback a PT...")
            from app.config.settings import DEFAULT_PT_MODEL
            self.model = YOLO(DEFAULT_PT_MODEL)
            self.effective_mode = "cpu"
            self.device_message = f"Fallback a CPU por error: {e}"

        return {
            "preference": self.device_preference,
            "effective_mode": self.effective_mode,
            "message": self.device_message,
            "is_gpu": self.effective_mode.startswith("gpu")
        }

    def process_frame(self, frame: np.ndarray, draw_vehicles: bool = True) -> Tuple[np.ndarray, Dict[str, Any]]:
        self.tracker_stats.update_fps()
        self.frame_index += 1

        # Only run heavy neural net detection every Nth frame
        should_run_inference = (self.frame_index % self.infer_interval == 0) or (len(self.cached_vehicles) == 0)

        if should_run_inference:
            detected_vehicles = []
            try:
                # Pre-inference Exclusion Masking:
                # If exclusion zones exist, mask them out (pixel value = 0) on the input tensor passed to YOLO.
                # This prevents YOLO from proposing candidate anchors in those areas and prevents ByteTrack
                # from computing Kalman filters / Hungarian matching for irrelevant vehicles (street, sidewalks).
                # The display 'frame' remains completely natural and untouched.
                infer_frame = frame
                if self.spot_manager and self.spot_manager.exclusion_zones:
                    infer_frame = frame.copy()
                    fh, fw = frame.shape[:2]
                    for zone in self.spot_manager.exclusion_zones.values():
                        pts_list = zone.get_points_for_frame(fw, fh)
                        if len(pts_list) >= 3:
                            pts_arr = np.array(pts_list, np.int32).reshape((-1, 1, 2))
                            cv2.fillPoly(infer_frame, [pts_arr], (0, 0, 0))

                if self.effective_mode == "gpu_cuda":
                    results = self.model.track(
                        infer_frame, persist=True, classes=VEHICLE_CLASSES, conf=self.conf_threshold,
                        imgsz=640, tracker=self.tracker_yaml, verbose=False, device="cuda"
                    )
                elif self.effective_mode == "cpu":
                    results = self.model.track(
                        infer_frame, persist=True, classes=VEHICLE_CLASSES, conf=self.conf_threshold,
                        imgsz=640, tracker=self.tracker_yaml, verbose=False, device="cpu"
                    )
                else:  # gpu_dml (AMD Radeon via DirectML)
                    results = self.model.track(
                        infer_frame, persist=True, classes=VEHICLE_CLASSES, conf=self.conf_threshold,
                        imgsz=640, tracker=self.tracker_yaml, verbose=False
                    )

                if results and len(results) > 0 and results[0].boxes is not None:
                    boxes = results[0].boxes
                    for box in boxes:
                        cls_id = int(box.cls[0].item())
                        conf = float(box.conf[0].item())
                        track_id = int(box.id[0].item()) if box.id is not None else None
                        
                        x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
                        cx = (x1 + x2) // 2
                        cy = (y1 + y2) // 2

                        # Exclusion / Mask Zone check: Ignore vehicles inside ignored zones
                        fh, fw = frame.shape[:2]
                        from shapely.geometry import Point
                        if self.spot_manager.is_in_exclusion_zone(Point(cx, cy), fw, fh):
                            continue

                        detected_vehicles.append({
                            "track_id": track_id,
                            "class_id": cls_id,
                            "class_name": CLASS_NAMES.get(cls_id, "Vehículo"),
                            "conf": conf,
                            "bbox": [x1, y1, x2, y2],
                            "center": (cx, cy)
                        })

                self.cached_vehicles = detected_vehicles
            except Exception as e:
                print(f"[Detector] Tracking error ({self.effective_mode}): {e}")
        else:
            detected_vehicles = self.cached_vehicles


        # Update spot occupancy states and history
        fh, fw = frame.shape[:2]
        self.spot_manager.update_occupancy(detected_vehicles, frame_w=fw, frame_h=fh)
        self.tracker_stats.register_frame_tracks(detected_vehicles)

        # 1. Render parking spots overlay first (so vehicle boxes render cleanly on top)
        frame = self.spot_manager.draw_spots(frame)

        # 2. Render vehicle bounding boxes if enabled
        if draw_vehicles:
            for v in detected_vehicles:
                x1, y1, x2, y2 = v["bbox"]
                tid = v["track_id"]
                cname = v["class_name"]
                
                # Tech Cyan / Yellow styling for vehicles
                cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 200, 0), 2, cv2.LINE_AA)
                
                label = f"#{tid} {cname}" if tid else cname
                font = cv2.FONT_HERSHEY_SIMPLEX
                (tw, th), _ = cv2.getTextSize(label, font, 0.45, 1)
                
                cv2.rectangle(frame, (x1, y1 - th - 6), (x1 + tw + 6, y1), (255, 200, 0), -1)
                cv2.putText(frame, label, (x1 + 3, y1 - 4), font, 0.45, (0, 0, 0), 1, cv2.LINE_AA)

        kpis = self.tracker_stats.get_kpis(self.spot_manager)
        return frame, kpis
