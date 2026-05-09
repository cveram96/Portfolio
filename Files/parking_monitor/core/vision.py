import cv2
import os
import numpy as np
import json
import time
from ultralytics import YOLO
from PySide6.QtCore import QThread, Signal
from PySide6.QtGui import QImage
from db.crud import log_occupancy_change, create_alert, log_periodic_state
from services.analytics import calculate_analytics

OCCUPY_CONFIRM_SECS = 1.0
FREE_CONFIRM_SECS   = 3.0
MIN_DWELL_SECS      = 6.0
TRANSITION_COOLDOWN = 1.0

STRATEGY_YOLO   = 'yolo'
STRATEGY_BGSUB  = 'bgsub'
STRATEGY_HYBRID = 'hybrid'


class VisionThread(QThread):
    frame_ready     = Signal(QImage)
    stats_updated   = Signal(dict)
    alert_triggered = Signal(str)
    fps_updated     = Signal(float)
    strategy_status = Signal(str)
    position_updated= Signal(float, float)
    error_occurred  = Signal(str)

    def __init__(self, video_path='parking_video.mp4'):
        super().__init__()
        self.video_path   = video_path
        self.config_path  = self.get_config_path(video_path)
        self.running      = True
        self.paused       = False
        self.reload_video = False

        self.source_type  = 'video'
        self.camera_idx   = 0
        self.rtsp_url     = ''
        self._current_cap = None
        self._video_fps   = 30.0
        self._seek_requested = -1

        self._seg_model = None
        self._det_model = None
        self._precise_model = None
        self._models_loaded = False

        self.spaces       = []
        self.space_states = {}
        self.space_vehicle_types = {}  # Track vehicle type per space: {space_idx: class_id}

        self._detect_since   = {}
        self._clear_since    = {}
        self._occupied_since = {}
        self._last_transition= {}

        self.load_config()

        self.last_raw_frame       = None
        self.last_analytics_time  = time.time()
        self.last_alert_time      = time.time()
        self._detection_mode      = 'aerial'
        self.playback_speed       = 1.0
        
        self.yolo_tile_conf = float(os.environ.get("YOLO_TILE_CONF", "0.15"))
        self.detect_strategy = STRATEGY_YOLO

        self._ref_frame    = None
        self._bgsub        = cv2.createBackgroundSubtractorMOG2(
                                   history=500, varThreshold=40, detectShadows=False)
        self._bgsub_warmup = 0

        self._snapshot_requested = False
        self._snapshot_path      = ''

        self._last_detection_time = 0
        self._last_periodic_log_time = time.time()
        self._detection_interval = 1.0

    @property
    def detection_mode(self):
        return self._detection_mode
    
    @detection_mode.setter
    def detection_mode(self, value):
        if self._detection_mode != value:
            self._detection_mode = value
            if self._seg_model is not None:
                del self._seg_model
                self._seg_model = None
            model_name = 'yolo26m-seg.pt' if value == 'aerial' else 'yolo26n-seg.pt'
            self.strategy_status.emit(f'Modo: {"Aérea" if value == "aerial" else "Normal"} | Modelo: {model_name}')

    @property
    def model(self):
        expected_model = 'yolo26m-seg.pt' if self.detection_mode == 'aerial' else 'yolo26n-seg.pt'
        if self._seg_model is None or getattr(self, '_seg_model_name', '') != expected_model:
            if self._seg_model is not None:
                del self._seg_model
            self._seg_model = YOLO(expected_model)
            self._seg_model_name = expected_model
        return self._seg_model

    @property
    def fast_model(self):
        if self._det_model is None:
            self._det_model = YOLO('yolo26n.pt')
        return self._det_model

    def get_precise_model(self):
        if self._precise_model is None:
            self._precise_model = YOLO('yolo26m-seg.pt')
        return self._precise_model

    def get_imgsz(self):
        return 800 if self.detection_mode == 'aerial' else 640

    def get_config_path(self, v_path):
        base = os.path.basename(v_path)
        name, _ = os.path.splitext(base)
        if not os.path.exists('config'):
            os.makedirs('config')
        return f'config/spaces_{name}.json'

    def set_video(self, new_path):
        self.video_path  = new_path
        self.source_type = 'video'
        self.config_path = self.get_config_path(new_path)
        self.load_config()
        self._ref_frame     = None
        self._bgsub_warmup = 0
        self.reload_video  = True
        self._emit_stats()

    def capture_reference(self):
        if self.last_raw_frame is not None:
            self._ref_frame = self.last_raw_frame.copy()
            self._bgsub_warmup = 0
            return True
        return False

    def load_config(self):
        self.space_states.clear()
        self.space_vehicle_types.clear()
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

    def set_camera(self, camera_idx: int):
        print(f"set_camera called with index {camera_idx}")
        self.source_type = 'webcam'
        self.camera_idx = camera_idx
        self._ref_frame = None
        self._bgsub_warmup = 0
        self._cap = None
        self._current_cap = None
        self.strategy_status.emit(f'Webcam {camera_idx}')
        print(f"source_type={self.source_type}, camera_idx={self.camera_idx}")

    def set_rtsp(self, url: str):
        self.source_type = 'rtsp'
        self.rtsp_url = url
        self._ref_frame = None
        self._bgsub_warmup = 0
        self._cap = None
        self._current_cap = None
        self.strategy_status.emit(f'RTSP: {url[:30]}...')

    def seek_to(self, frame_pos):
        if self.source_type == 'video':
            self._seek_requested = int(frame_pos)

    def get_video_info(self):
        if self.source_type == 'video' and hasattr(self, '_current_cap') and self._current_cap:
            curr = int(self._current_cap.get(cv2.CAP_PROP_POS_FRAMES))
            total = int(self._current_cap.get(cv2.CAP_PROP_FRAME_COUNT))
            return curr, total
        return 0, 0

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

    def _detect_yolo(self, frame) -> dict:
        """Returns dict {space_idx: vehicle_class_id}"""
        if not self.spaces:
            return {}
        
        fh, fw = frame.shape[:2]
        conf_thr = self.yolo_tile_conf
        use_segmentation = (self.detection_mode == 'aerial')
        
        occupied = {}  # dict: {space_idx: class_id}
        current_model = self.model if use_segmentation else self.fast_model
        
        max_detect_dim = 640
        scale = 1.0
        if max(fh, fw) > max_detect_dim:
            scale = max_detect_dim / max(fh, fw)
            small_frame = cv2.resize(frame, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA)
        else:
            small_frame = frame
        
        imgsz = 640
        results = current_model.predict(small_frame, classes=[2, 3, 5, 7], conf=conf_thr, verbose=False, imgsz=imgsz)
        
        if not results or len(results) == 0:
            return occupied
        
        result = results[0]
        
        space_polys_scaled = []
        space_bounds_scaled = []
        space_polys = []
        for space_data in self.spaces:
            pts = space_data['points'] if isinstance(space_data, dict) else space_data
            poly = np.array(pts, np.int32)
            space_polys.append(poly)
            if scale < 1.0:
                poly_scaled = (poly * scale).astype(np.int32)
            else:
                poly_scaled = poly
            space_polys_scaled.append(poly_scaled)
            x, y, w, h = cv2.boundingRect(poly_scaled)
            space_bounds_scaled.append((x, y, x + w, y + h))
        
        fh_small, fw_small = small_frame.shape[:2]
        
        if use_segmentation and result.masks is not None:
            masks_data = result.masks.xy
            confs = result.boxes.conf.cpu().numpy() if result.boxes else []
            clss = result.boxes.cls.cpu().numpy() if result.boxes else []
            
            for mask_pts, conf, cls in zip(masks_data, confs, clss):
                mask_pts = np.array(mask_pts, dtype=np.int32)
                if len(mask_pts) < 3:
                    continue
                
                if scale < 1.0:
                    mask_pts_original = (mask_pts / scale).astype(np.int32)
                else:
                    mask_pts_original = mask_pts
                
                mx, my, mw, mh = cv2.boundingRect(mask_pts)
                mask_x2, mask_y2 = mx + mw, my + mh
                
                for si, (sx1, sy1, sx2, sy2) in enumerate(space_bounds_scaled):
                    if mx > sx2 or mask_x2 < sx1 or my > sy2 or mask_y2 < sy1:
                        continue
                    
                    poly_scaled = space_polys_scaled[si]
                    space_mask = np.zeros((fh_small, fw_small), dtype=np.uint8)
                    cv2.fillPoly(space_mask, [poly_scaled], 255)
                    space_area = cv2.countNonZero(space_mask)
                    
                    if space_area == 0:
                        continue
                    
                    vehicle_mask = np.zeros((fh_small, fw_small), dtype=np.uint8)
                    cv2.fillPoly(vehicle_mask, [mask_pts], 255)
                    
                    intersection = cv2.countNonZero(cv2.bitwise_and(space_mask, vehicle_mask))
                    overlap_ratio = intersection / space_area
                    
                    if overlap_ratio > 0.35:
                        cv2.polylines(frame, [mask_pts_original], True, (0, 200, 255), 2)
                        cv2.fillPoly(frame, [mask_pts_original], (0, 100, 150))
                        occupied[si] = int(cls)
                        break
        else:
            if result.boxes is not None:
                boxes_xyxy = result.boxes.xyxy.cpu().numpy()
                clss = result.boxes.cls.cpu().numpy()
                
                for idx, box in enumerate(boxes_xyxy):
                    bx1, by1, bx2, by2 = box
                    cls = int(clss[idx])
                    
                    if scale < 1.0:
                        cx = int((bx1 + bx2) / (2 * scale))
                        cy = int((by1 + by2) / (2 * scale))
                    else:
                        cx = int((bx1 + bx2) / 2)
                        cy = int((by1 + by2) / 2)
                    
                    for si, poly in enumerate(space_polys):
                        if cv2.pointPolygonTest(poly, (cx, cy), False) >= 0:
                            cv2.rectangle(frame, (cx - 20, cy - 20), (cx + 20, cy + 20), (0, 200, 255), 2)
                            cv2.circle(frame, (cx, cy), 4, (0, 255, 255), -1)
                            occupied[si] = cls
                            break
        
        return occupied
        
        result = results[0]
        
        space_polys_scaled = []
        space_bounds_scaled = []
        space_polys = []
        for space_data in self.spaces:
            pts = space_data['points'] if isinstance(space_data, dict) else space_data
            poly = np.array(pts, np.int32)
            space_polys.append(poly)
            if scale < 1.0:
                poly_scaled = (poly * scale).astype(np.int32)
            else:
                poly_scaled = poly
            space_polys_scaled.append(poly_scaled)
            x, y, w, h = cv2.boundingRect(poly_scaled)
            space_bounds_scaled.append((x, y, x + w, y + h))
        
        fh_small, fw_small = small_frame.shape[:2]
        
        if use_segmentation and result.masks is not None:
            masks_data = result.masks.xy
            confs = result.boxes.conf.cpu().numpy() if result.boxes else []
            
            for mask_pts, conf in zip(masks_data, confs):
                mask_pts = np.array(mask_pts, dtype=np.int32)
                if len(mask_pts) < 3:
                    continue
                
                if scale < 1.0:
                    mask_pts_original = (mask_pts / scale).astype(np.int32)
                else:
                    mask_pts_original = mask_pts
                
                mx, my, mw, mh = cv2.boundingRect(mask_pts)
                mask_x2, mask_y2 = mx + mw, my + mh
                
                for si, (sx1, sy1, sx2, sy2) in enumerate(space_bounds_scaled):
                    if mx > sx2 or mask_x2 < sx1 or my > sy2 or mask_y2 < sy1:
                        continue
                    
                    poly_scaled = space_polys_scaled[si]
                    space_mask = np.zeros((fh_small, fw_small), dtype=np.uint8)
                    cv2.fillPoly(space_mask, [poly_scaled], 255)
                    space_area = cv2.countNonZero(space_mask)
                    
                    if space_area == 0:
                        continue
                    
                    vehicle_mask = np.zeros((fh_small, fw_small), dtype=np.uint8)
                    cv2.fillPoly(vehicle_mask, [mask_pts], 255)
                    
                    intersection = cv2.countNonZero(cv2.bitwise_and(space_mask, vehicle_mask))
                    overlap_ratio = intersection / space_area
                    
                    if overlap_ratio > 0.35:
                        cv2.polylines(frame, [mask_pts_original], True, (0, 200, 255), 2)
                        cv2.fillPoly(frame, [mask_pts_original], (0, 100, 150))
                        occupied.add(si)
                        break
        else:
            if result.boxes is not None:
                boxes_xyxy = result.boxes.xyxy.cpu().numpy()
                
                for box in boxes_xyxy:
                    bx1, by1, bx2, by2 = box
                    if scale < 1.0:
                        cx = int((bx1 + bx2) / (2 * scale))
                        cy = int((by1 + by2) / (2 * scale))
                    else:
                        cx = int((bx1 + bx2) / 2)
                        cy = int((by1 + by2) / 2)
                    
                    for si, poly in enumerate(space_polys):
                        if cv2.pointPolygonTest(poly, (cx, cy), False) >= 0:
                            cv2.rectangle(frame, (cx - 20, cy - 20), (cx + 20, cy + 20), (0, 200, 255), 2)
                            cv2.circle(frame, (cx, cy), 4, (0, 255, 255), -1)
                            occupied.add(si)
                            break
        
        return occupied
        
    def _detect_bgsub(self, frame) -> dict:
        """Returns dict {space_idx: vehicle_class_id}"""
        occupied = {}  # dict instead of set
        
        if self._ref_frame is not None:
            gray_ref = cv2.cvtColor(self._ref_frame, cv2.COLOR_BGR2GRAY)
            gray_cur = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            diff = cv2.absdiff(gray_ref, gray_cur)
            _, mask = cv2.threshold(diff, 30, 255, cv2.THRESH_BINARY)
        else:
            mask = self._bgsub.apply(frame)
            self._bgsub_warmup += 1
            if self._bgsub_warmup < 30:
                return occupied

        fh_mask, fw_mask = mask.shape[:2]

        for i, space_data in enumerate(self.spaces):
            pts = space_data['points'] if isinstance(space_data, dict) else space_data
            poly = np.array(pts, dtype=np.int32)
            
            x, y, w, h = cv2.boundingRect(poly)
            
            if w <= 0 or h <= 0:
                continue
            
            x1 = max(0, x)
            y1 = max(0, y)
            x2 = min(fw_mask, x + w)
            y2 = min(fh_mask, y + h)
            
            if x2 <= x1 or y2 <= y1:
                continue
            
            roi = mask[y1:y2, x1:x2]
            if roi.size == 0:
                continue
            
            roi_h, roi_w = roi.shape[:2]
            roi_poly = np.zeros((roi_h, roi_w), dtype=np.uint8)
            shifted_pts = poly - np.array([x1, y1])
            cv2.fillPoly(roi_poly, [shifted_pts.astype(np.int32)], 255)
            
            if roi.shape == roi_poly.shape:
                fg_pixels = cv2.countNonZero(cv2.bitwise_and(roi, roi_poly))
                area = cv2.countNonZero(roi_poly)
                
                if area > 0 and (fg_pixels / area) > 0.25:
                    occupied[i] = 2  # Default to car (class 2)
        
        return occupied

    def run(self):
        print("VisionThread: run() started")
        fps_t       = time.time()
        fps_count   = 0
        last_ui_emit = 0
        ui_interval  = 1.0 / 25.0
        cap = None
        source_key = None
        video_fps = 30.0
        frame_count = 0
        video_frame_skip = max(1, int(self.playback_speed)) if self.playback_speed > 1 else 1
        frame_start = time.time()
        
        while self.running:
            if cap is None:
                print(f"VisionThread: cap is None, source_type={self.source_type}")
            
            if self.paused:
                print(f"VisionThread: PAUSED=True, skipping frame read")
            
            curr_key = (self.source_type, self.video_path, self.camera_idx, self.rtsp_url)
            if curr_key != source_key:
                print(f"VisionThread: Source changed! curr_key={curr_key}, source_key={source_key}")
                if cap is not None:
                    cap.release()
                if self.source_type == 'webcam':
                    print(f"Opening webcam with index {self.camera_idx}...")
                    cap = cv2.VideoCapture(self.camera_idx, cv2.CAP_DSHOW)
                    if not cap.isOpened():
                        print(f"DirectShow failed, trying without backend...")
                        cap = cv2.VideoCapture(self.camera_idx)
                    if not cap.isOpened():
                        print(f"ERROR: Webcam {self.camera_idx} could not be opened!")
                        self.error_occurred.emit(f"No se pudo abrir webcam {self.camera_idx}")
                        time.sleep(0.5)
                        continue
                    print(f"Webcam opened successfully: {cap.isOpened()}")
                    w = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
                    h = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
                    print(f"Webcam resolution: {w}x{h}")
                    self._video_fps = 30.0
                elif self.source_type == 'rtsp':
                    cap = cv2.VideoCapture(self.rtsp_url)
                    self._video_fps = 30.0
                else:
                    cap = cv2.VideoCapture(self.video_path)
                    self._video_fps = cap.get(cv2.CAP_PROP_FPS)
                    if self._video_fps <= 0:
                        self._video_fps = 30.0
                video_fps = self._video_fps
                self._current_cap = cap
                source_key = curr_key
                frame_count = 0
            
            if self.paused:
                print("VisionThread: paused=True, skipping frame")
                time.sleep(0.1)
                continue
            
            frame_start = time.time()
            ret, frame = cap.read()
            if not ret:
                if self.source_type == 'webcam':
                    print(f"Webcam: failed to read frame, reinitializing...")
                    self.error_occurred.emit(f"Webcam {self.camera_idx}: fallo al leer frame")
                    cap.release()
                    cap = cv2.VideoCapture(self.camera_idx, cv2.CAP_DSHOW)
                    if not cap.isOpened():
                        cap = cv2.VideoCapture(self.camera_idx)
                    if cap.isOpened():
                        self._current_cap = cap
                        source_key = None  # Force recheck on next loop
                        print(f"Webcam reinitialized successfully")
                    else:
                        print(f"ERROR: Could not reopen webcam {self.camera_idx}")
                        time.sleep(1.0)
                    continue
                elif self.source_type == 'video':
                    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                    self._seek_requested = -1
                    frame_count = 0
                time.sleep(0.1)
                continue

            if self._seek_requested >= 0:
                cap.set(cv2.CAP_PROP_POS_FRAMES, self._seek_requested)
                self._seek_requested = -1
                ret, frame = cap.read()
                if not ret:
                    time.sleep(0.1)
                    continue
                frame_count = 0

            frame_count += 1
            
            if self.source_type == 'video' and self.playback_speed > 1:
                if frame_count % video_frame_skip != 0:
                    continue

            fps_count += 1
            elapsed = time.time() - fps_t
            if elapsed >= 1.0:
                self.fps_updated.emit(fps_count / elapsed)
                fps_count = 0
                fps_t = time.time()

            speed = self.playback_speed if self.source_type == 'video' else 1.0
            curr_frame = int(cap.get(cv2.CAP_PROP_POS_FRAMES))
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            self.position_updated.emit(curr_frame, total_frames if total_frames > 0 else 1)

            h, w = frame.shape[:2]
            if w > 800:
                scale = 800 / w
                frame = cv2.resize(frame, (800, int(h * scale)))
            
            self.last_raw_frame = frame.copy()

            now = time.time()
            should_detect = (now - self._last_detection_time) >= self._detection_interval
            
            if should_detect and self.spaces:
                if self.source_type == 'video' and speed > 1:
                    self._detection_interval = 0.5
                elif self.detection_mode == 'aerial':
                    self._detection_interval = 2.0
                else:
                    self._detection_interval = 1.0
                
                if self.detect_strategy == STRATEGY_YOLO:
                    raw_occupied = self._detect_yolo(frame)
                    mode_label = 'SEG' if self.detection_mode == 'aerial' else 'DET'
                    self.strategy_status.emit(f'YOLO26-{mode_label} | {len(raw_occupied)}/{len(self.spaces)}')
                elif self.detect_strategy == STRATEGY_BGSUB:
                    raw_occupied = self._detect_bgsub(frame)
                    self.strategy_status.emit('BgSub')
                else:
                    if self.spaces:
                        yolo_occ = self._detect_yolo(frame)
                        bgsub_occ = self._detect_bgsub(frame)
                        raw_occupied = bgsub_occ.copy()
                        raw_occupied.update(yolo_occ)  # yolo takes precedence
                    else:
                        raw_occupied = {}
                    self.strategy_status.emit('Hybrid')

                self._last_detection_time = now
                
                for i in range(len(self.spaces)):
                    car_here = i in raw_occupied
                    was_occupied = self.space_states.get(i, False)
                    in_cooldown = (now - self._last_transition.get(i, 0.0)) < TRANSITION_COOLDOWN
                    
                    if car_here:
                        self._clear_since[i] = None
                        if self._detect_since.get(i) is None:
                            self._detect_since[i] = now
                        if not was_occupied and not in_cooldown and (now - self._detect_since[i]) >= OCCUPY_CONFIRM_SECS:
                            self.space_states[i] = True
                            self._occupied_since[i] = now
                            self._last_transition[i] = now
                            self.space_vehicle_types[i] = raw_occupied[i]  # Track vehicle type
                            log_occupancy_change(i, True)
                    else:
                        self._detect_since[i] = None
                        if self._clear_since.get(i) is None:
                            self._clear_since[i] = now
                        dwell_ok = (now - self._occupied_since.get(i, now)) >= MIN_DWELL_SECS
                        if was_occupied and not in_cooldown and dwell_ok and (now - self._clear_since[i]) >= FREE_CONFIRM_SECS:
                            self.space_states[i] = False
                            self._last_transition[i] = now
                            self.space_vehicle_types.pop(i, None)  # Clear vehicle type
                            log_occupancy_change(i, False)

                total = len(self.spaces)
                occupied = sum(self.space_states.values())
                self._emit_stats()
                
                if now - self.last_analytics_time > 10:
                    calculate_analytics(occupied, total)
                    self.last_analytics_time = now
                if now - self.last_alert_time > 30:
                    pct = occupied / total * 100 if total else 0
                    if pct == 100:
                        create_alert('Parqueadero LLENO')
                        self.alert_triggered.emit('LLENO')
                        self.last_alert_time = now

                # Periodic state logging (every 30 seconds)
                if now - self._last_periodic_log_time >= 30:
                    log_periodic_state(self.space_states)
                    self._last_periodic_log_time = now

            for i, space_data in enumerate(self.spaces):
                pts = space_data['points'] if isinstance(space_data, dict) else space_data
                stype = space_data.get('type', 'Estándar') if isinstance(space_data, dict) else 'Estándar'
                name = space_data.get('name', f'Espacio {i+1}') if isinstance(space_data, dict) else f'Espacio {i+1}'
                poly = np.array(pts, np.int32)
                type_colors = {'Discapacitados': (255,144,30), 'VIP': (180,0,200), 'Motos': (255,165,0)}
                base_color = type_colors.get(stype, (30, 200, 30))
                color = (0, 0, 230) if self.space_states.get(i, False) else base_color
                overlay = frame.copy()
                cv2.fillPoly(overlay, [poly], color)
                cv2.addWeighted(overlay, 0.35, frame, 0.65, 0, frame)
                cv2.polylines(frame, [poly], True, color, 2)
                
                # Show space name and vehicle type if occupied
                M = cv2.moments(poly)
                if M['m00'] != 0:
                    cx = int(M['m10']/M['m00'])
                    cy = int(M['m01']/M['m00'])
                    # Draw space name
                    cv2.putText(frame, name, (cx - len(name)*4, cy - 5), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255,255,255), 1)
                    # Draw vehicle type if occupied
                    if self.space_states.get(i, False) and i in self.space_vehicle_types:
                        vclass = self.space_vehicle_types[i]
                        class_names = {2: 'AUTO', 3: 'MOTO', 5: 'BUS', 7: 'CAMION'}
                        vname = class_names.get(vclass, 'VEHIC')
                        cv2.putText(frame, vname, (cx - len(vname)*4, cy + 10), 
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255,255,255), 1)

            if self._snapshot_requested:
                cv2.imwrite(self._snapshot_path, frame)
                self._snapshot_requested = False

            now = time.time()
            if (now - last_ui_emit) >= ui_interval:
                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h_ui, w_ui, ch = rgb.shape
                qt_img = QImage(rgb.data, w_ui, h_ui, ch * w_ui, QImage.Format_RGB888)
                self.frame_ready.emit(qt_img)
                last_ui_emit = now

            if self.source_type == 'video':
                frame_duration = 1.0 / (video_fps * speed)
                elapsed = time.time() - frame_start
                if elapsed < frame_duration:
                    time.sleep(max(0, frame_duration - elapsed))
            else:
                time.sleep(0.01)

    def stop(self):
        self.running = False
        self._seg_model = None
        self._det_model = None
        self._precise_model = None
        self.wait()
