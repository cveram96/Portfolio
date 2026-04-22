import cv2
import os
import numpy as np
import json
import time
from ultralytics import YOLO
from PySide6.QtCore import QThread, Signal
from PySide6.QtGui import QImage
from db.crud import log_occupancy_change, create_alert
from services.analytics import calculate_analytics

# ── Temporal consistency parameters ─────────────────────────────────────────
OCCUPY_CONFIRM_SECS = 1.0
FREE_CONFIRM_SECS   = 3.0
MIN_DWELL_SECS      = 6.0
TRANSITION_COOLDOWN = 1.0

# ── Detection strategy labels ────────────────────────────────────────────────
STRATEGY_YOLO   = 'yolo'      # Only YOLOv8 bounding boxes
STRATEGY_BGSUB  = 'bgsub'     # Background subtraction vs reference frame
STRATEGY_HYBRID = 'hybrid'    # Both must agree → fewest false positives


class VisionThread(QThread):
    frame_ready     = Signal(QImage)
    stats_updated   = Signal(dict)
    alert_triggered = Signal(str)
    fps_updated     = Signal(float)
    strategy_status = Signal(str)   # live feedback string shown in UI

    def __init__(self, video_path='parking_video.mp4'):
        super().__init__()
        self.video_path   = video_path
        self.config_path  = self.get_config_path(video_path)
        self.running      = True
        self.paused       = False
        self.reload_video = False

        # ── Detection model ──────────────────────────────────────────────────
        self.model_name    = 'yolov8n.pt'   # can be swapped live
        self.model         = YOLO(self.model_name)

        # ── State ────────────────────────────────────────────────────────────
        self.spaces       = []
        self.space_states = {}

        # Temporal trackers
        self._detect_since   = {}
        self._clear_since    = {}
        self._occupied_since = {}
        self._last_transition= {}

        self.load_config()

        self.last_raw_frame      = None
        self.last_analytics_time = time.time()
        self.last_alert_time     = time.time()
        self.detection_mode      = 'auto'      # aerial / normal / auto
        # Sensitivity for per-tile YOLO inference (configurable via env, default 0.25)
        
        # Tunable per-tile YOLO confidence for recall vs precision (can be adjusted at runtime or via env)
        self.yolo_tile_conf = float(os.environ.get("YOLO_TILE_CONF", "0.25"))
        self.detect_strategy     = STRATEGY_YOLO

        # Background subtraction
        self._ref_frame      = None   # user-captured empty-lot reference
        self._bgsub          = cv2.createBackgroundSubtractorMOG2(
                                   history=500, varThreshold=40, detectShadows=False)
        self._bgsub_warmup   = 0     # frames fed to warm up MOG2

        # Snapshot
        self._snapshot_requested = False
        self._snapshot_path      = ''

    # ── Helpers ───────────────────────────────────────────────────────────────
    def get_imgsz(self):
        if self.detection_mode == 'aerial':
            return 1280
        if self.detection_mode == 'normal':
            return 640
        if self.last_raw_frame is not None:
            _, w = self.last_raw_frame.shape[:2]
            return 1280 if w >= 960 else 640
        return 1280

    def get_config_path(self, v_path):
        import os
        base = os.path.basename(v_path)
        name, _ = os.path.splitext(base)
        if not os.path.exists('config'):
            os.makedirs('config')
        return f'config/spaces_{name}.json'

    def set_video(self, new_path):
        self.video_path  = new_path
        self.config_path = self.get_config_path(new_path)
        self.load_config()
        self._ref_frame    = None   # reference invalidated for new video
        self._bgsub_warmup = 0
        self.reload_video  = True
        self._emit_stats()

    def set_model(self, model_name: str):
        """Hot-swap the YOLO model (e.g. yolov8m.pt)."""
        if model_name != self.model_name:
            self.model_name = model_name
            self.model = YOLO(model_name)

    def capture_reference(self):
        """Capture current frame as the 'empty lot' background reference."""
        if self.last_raw_frame is not None:
            self._ref_frame = self.last_raw_frame.copy()
            self._bgsub_warmup = 0
            return True
        return False

    def load_config(self):
        self.space_states.clear()
        self._detect_since.clear()
        self._clear_since.clear()
        self._occupied_since.clear()
        self._last_transition.clear()
        try:
            with open(self.config_path, 'r') as f:
                self.spaces = json.load(f)
                for i in range(len(self.spaces)):
                    self.space_states[i] = False
        except (FileNotFoundError, json.JSONDecodeError):
            self.spaces = []

    def update_spaces(self, new_spaces):
        with open(self.config_path, 'w') as f:
            json.dump(new_spaces, f, indent=4)
        self.load_config()

    def request_snapshot(self, path: str):
        self._snapshot_path      = path
        self._snapshot_requested = True

    def _emit_stats(self):
        total    = len(self.spaces)
        occupied = sum(self.space_states.values())
        self.stats_updated.emit({'total': total, 'occupied': occupied, 'free': total - occupied})

    # ── Detection strategies ──────────────────────────────────────────────────
    def _detect_yolo(self, frame) -> set:
        """Tiled sliced inference for accurate detection of small/aerial cars.
        Returns set of space indices whose centroid lands inside a detected car box."""
        fh, fw  = frame.shape[:2]
        tile_sz  = 480
        overlap  = 120
        step     = tile_sz - overlap
        # Model confidence threshold for tile predictions (tune to improve recall)
        conf_thr_model = getattr(self, 'yolo_tile_conf', 0.25)
        nms_iou  = 0.35

        all_boxes = []
        for y in range(0, fh, step):
            for x in range(0, fw, step):
                x2t = min(x + tile_sz, fw)
                y2t = min(y + tile_sz, fh)
                tile = frame[y:y2t, x:x2t]
                r = self.model.predict(tile, classes=[2, 3, 5, 7],
                                       conf=conf_thr_model, verbose=False)
                for box in r[0].boxes.xyxy.cpu().numpy():
                    bx1, by1, bx2, by2 = box
                    all_boxes.append([x + bx1, y + by1, x + bx2, y + by2])

        if not all_boxes:
            return set()

        boxes_np = np.array(all_boxes, dtype=np.float32)

        # Filter out noise and false positives by bounding box dimensions
        widths  = boxes_np[:, 2] - boxes_np[:, 0]
        heights = boxes_np[:, 3] - boxes_np[:, 1]
        # Relaxed bounds to accommodate cars at varying distances/sizes
        valid   = (widths > 12) & (widths < 600) & (heights > 12) & (heights < 420)
        boxes_np = boxes_np[valid]
        if len(boxes_np) == 0:
            return set()

        # Global NMS to deduplicate overlapping tile detections
        xywh = boxes_np.copy()
        xywh[:, 2] -= xywh[:, 0]
        xywh[:, 3] -= xywh[:, 1]
        # Use a conservative per-box score; actual confidences from the model are not
        # reliably aligned with the aggregated boxes, so we supply a uniform score.
        scores = [0.25] * len(boxes_np)
        idx = cv2.dnn.NMSBoxes(
            xywh.astype(int).tolist(), scores, conf_thr_model, nms_iou)
        if len(idx) == 0:
            return set()

        occupied = set()
        for i in idx.flatten():
            x1, y1, x2, y2 = boxes_np[i]
            cx = int(x1 + (x2 - x1) / 2)
            cy = int(y1 + (y2 - y1) / 2)
            cv2.circle(frame, (cx, cy), 5, (255, 100, 0), -1)
            for si, space_data in enumerate(self.spaces):
                pts = space_data['points'] if isinstance(space_data, dict) else space_data
                if cv2.pointPolygonTest(np.array(pts, np.int32), (cx, cy), False) >= 0:
                    occupied.add(si)
                    break
        return occupied

    def _detect_bgsub(self, frame) -> set:
        """Return set of space indices with significant foreground coverage vs reference."""
        occupied = set()

        if self._ref_frame is not None:
            # Static diff against user-provided reference frame
            gray_ref = cv2.GaussianBlur(cv2.cvtColor(self._ref_frame, cv2.COLOR_BGR2GRAY), (21, 21), 0)
            gray_cur = cv2.GaussianBlur(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY),            (21, 21), 0)
            diff     = cv2.absdiff(gray_ref, gray_cur)
            _, mask  = cv2.threshold(diff, 30, 255, cv2.THRESH_BINARY)
            kernel   = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9))
            mask     = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
            mask     = cv2.morphologyEx(mask, cv2.MORPH_OPEN,  kernel)
        else:
            # Fall back to adaptive MOG2 (warm-up needed)
            mask = self._bgsub.apply(frame)
            self._bgsub_warmup += 1
            if self._bgsub_warmup < 30:
                return occupied  # not warmed up yet

        for i, space_data in enumerate(self.spaces):
            pts = space_data['points'] if isinstance(space_data, dict) else space_data
            poly = np.array(pts, np.int32)

            # Create a mask for this polygon and compute foreground coverage
            space_mask = np.zeros(frame.shape[:2], dtype=np.uint8)
            cv2.fillPoly(space_mask, [poly], 255)

            area      = cv2.countNonZero(space_mask)
            fg_pixels = cv2.countNonZero(cv2.bitwise_and(mask, mask, mask=space_mask))

            if area > 0 and (fg_pixels / area) > 0.20:   # >20% of space covered = occupied
                occupied.add(i)

        return occupied

    # ── Main run loop ─────────────────────────────────────────────────────────
    def run(self):
        cap         = cv2.VideoCapture(self.video_path)
        frame_skip  = 2
        frame_count = 0
        fps_t       = time.time()
        fps_count   = 0

        while self.running:
            # reload video
            if self.reload_video:
                cap.release()
                cap = cv2.VideoCapture(self.video_path)
                self.reload_video = False
                ret, frame = cap.read()
                if ret:
                    h, w = frame.shape[:2]
                    if w > 1280:
                        frame = cv2.resize(frame, (1280, int(h * 1280 / w)))
                    self.last_raw_frame = frame.copy()

            if self.paused:
                time.sleep(0.05)
                continue

            ret, frame = cap.read()
            if not ret:
                cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                continue

            frame_count += 1
            fps_count   += 1

            # FPS
            elapsed = time.time() - fps_t
            if elapsed >= 1.0:
                self.fps_updated.emit(fps_count / elapsed)
                fps_count = 0
                fps_t     = time.time()

            # resize
            h, w = frame.shape[:2]
            if w > 1280:
                frame = cv2.resize(frame, (1280, int(h * 1280 / w)))
            self.last_raw_frame = frame.copy()

            if frame_count % frame_skip == 0 and len(self.spaces) > 0:
                # ── Run chosen strategy ──────────────────────────────────────
                if self.detect_strategy == STRATEGY_YOLO:
                    raw_occupied = self._detect_yolo(frame)
                    status_txt   = f'YOLO [{self.model_name}]'

                elif self.detect_strategy == STRATEGY_BGSUB:
                    raw_occupied = self._detect_bgsub(frame)
                    ref_info     = 'ref fijo' if self._ref_frame is not None else f'MOG2 ({self._bgsub_warmup}/30 frames)'
                    status_txt   = f'BgSub [{ref_info}]'

                else:  # HYBRID
                    yolo_occ  = self._detect_yolo(frame)
                    bgsub_occ = self._detect_bgsub(frame)
                    # Union with confidence levels: agree → definitely occupied
                    # YOLO only → probably occupied, BgSub only → noise/shadow
                    raw_occupied = yolo_occ | bgsub_occ   # union: either method is enough
                    # To be even stricter (fewest false pos): use intersection:
                    # raw_occupied = yolo_occ & bgsub_occ
                    ref_info = 'ref' if self._ref_frame is not None else 'MOG2'
                    status_txt = f'Híbrido YOLO+BgSub [{ref_info}]'

                self.strategy_status.emit(status_txt)

                # convert to raw_detected dict for temporal consistency
                raw_detected = {i: (i in raw_occupied) for i in range(len(self.spaces))}

                # ── Temporal consistency ─────────────────────────────────────
                now = time.time()
                for i in raw_detected:
                    car_here     = raw_detected[i]
                    was_occupied = self.space_states.get(i, False)
                    in_cooldown  = (now - self._last_transition.get(i, 0.0)) < TRANSITION_COOLDOWN

                    if car_here:
                        self._clear_since[i] = None
                        if self._detect_since.get(i) is None:
                            self._detect_since[i] = now
                        if (not was_occupied and not in_cooldown
                                and (now - self._detect_since[i]) >= OCCUPY_CONFIRM_SECS):
                            self.space_states[i]    = True
                            self._occupied_since[i] = now
                            self._last_transition[i]= now
                            log_occupancy_change(i, True)
                    else:
                        self._detect_since[i] = None
                        if self._clear_since.get(i) is None:
                            self._clear_since[i] = now
                        dwell_ok = (now - self._occupied_since.get(i, now)) >= MIN_DWELL_SECS
                        if (was_occupied and not in_cooldown and dwell_ok
                                and (now - self._clear_since[i]) >= FREE_CONFIRM_SECS):
                            self.space_states[i]    = False
                            self._last_transition[i]= now
                            log_occupancy_change(i, False)

                # stats & alerts
                total    = len(self.spaces)
                occupied = sum(self.space_states.values())
                self._emit_stats()

                now = time.time()
                if now - self.last_analytics_time > 10:
                    calculate_analytics(occupied, total)
                    self.last_analytics_time = now
                if now - self.last_alert_time > 30:
                    pct = occupied / total * 100 if total else 0
                    if pct == 100:
                        msg = 'Parqueadero LLENO (100% ocupado).'
                        create_alert(msg); self.alert_triggered.emit(msg)
                        self.last_alert_time = now
                    elif pct >= 80:
                        self.alert_triggered.emit(f'ADVERTENCIA: {int(pct)}% de ocupación.')
                        self.last_alert_time = now

            # ── Draw overlays ────────────────────────────────────────────────
            for i, space_data in enumerate(self.spaces):
                pts   = space_data['points'] if isinstance(space_data, dict) else space_data
                stype = space_data.get('type', 'Estándar') if isinstance(space_data, dict) else 'Estándar'
                poly  = np.array(pts, np.int32)
                is_occ= self.space_states.get(i, False)
                type_colors = {'Discapacitados': (255,144,30), 'VIP': (180,0,200), 'Motos': (255,165,0)}
                base_color = type_colors.get(stype, (30, 200, 30))
                color = (0, 0, 230) if is_occ else base_color
                overlay = frame.copy()
                cv2.fillPoly(overlay, [poly], color)
                cv2.addWeighted(overlay, 0.38, frame, 0.62, 0, frame)
                cv2.polylines(frame, [poly], True, color, 2)
                M = cv2.moments(poly)
                if M['m00'] != 0:
                    cX = int(M['m10'] / M['m00'])
                    cY = int(M['m01'] / M['m00'])
                    cv2.putText(frame, str(i+1), (cX-6, cY+5),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 2)

            # snapshot
            if self._snapshot_requested:
                cv2.imwrite(self._snapshot_path, frame)
                self._snapshot_requested = False

            # emit
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb.shape
            qt_img = QImage(rgb.data, w, h, ch * w, QImage.Format_RGB888)
            self.frame_ready.emit(qt_img)

    def stop(self):
        self.running = False
        self.wait()
