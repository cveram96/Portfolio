import cv2
import time
import threading
import os
import asyncio
from typing import Optional, Union, Dict, Any, Tuple
import numpy as np

class VideoStreamManager:
    def __init__(self, detector):
        self.detector = detector
        self.source: Union[int, str] = 0
        self.is_file: bool = False
        self.cap: Optional[cv2.VideoCapture] = None
        self.is_running = False
        self.lock = threading.Lock()

        self.latest_frame_bytes: Optional[bytes] = None
        self.latest_frame: Optional[np.ndarray] = None
        self.fps: float = 0.0
        self.frame_width: int = 960
        self.frame_height: int = 540
        self.worker_thread: Optional[threading.Thread] = None

    def set_source(self, source: Union[int, str], is_file: bool = False):
        """Switches video capture source instantly without blocking locks."""
        old_cap = None
        with self.lock:
            self.source = source
            self.is_file = is_file
            old_cap = self.cap
            self.cap = None

            # Generate connecting placeholder frame
            ph = np.zeros((540, 960, 3), dtype=np.uint8)
            cv2.putText(ph, "Conectando fuente de video...", (240, 270),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 242, 254), 2, cv2.LINE_AA)
            _, buf = cv2.imencode('.jpg', ph, [cv2.IMWRITE_JPEG_QUALITY, 70])
            self.latest_frame_bytes = buf.tobytes()

        if old_cap is not None:
            try:
                old_cap.release()
            except Exception:
                pass

        print(f"[VideoStream] Nueva fuente configurada: {source}")

    def start(self):
        if self.is_running:
            return
        self.is_running = True
        self.worker_thread = threading.Thread(target=self._run_loop, daemon=True)
        self.worker_thread.start()

    def stop(self):
        self.is_running = False
        if self.worker_thread and self.worker_thread.is_alive():
            self.worker_thread.join(timeout=2.0)
        with self.lock:
            if self.cap is not None:
                try:
                    self.cap.release()
                except Exception:
                    pass
                self.cap = None

    def _open_capture_for_src(self, src: Union[int, str]) -> Optional[cv2.VideoCapture]:
        if isinstance(src, str) and src.isdigit():
            src = int(src)

        print(f"[VideoStream] Abriendo origen de video: {src}")
        try:
            if isinstance(src, int):
                cap = cv2.VideoCapture(src, cv2.CAP_DSHOW)
                if not cap.isOpened():
                    cap = cv2.VideoCapture(src)
            else:
                norm_src = os.path.normpath(str(src))
                cap = cv2.VideoCapture(norm_src)

            if not cap.isOpened():
                print(f"[VideoStream] No se pudo abrir la fuente: {src}")
                return None
            return cap
        except Exception as e:
            print(f"[VideoStream] Excepcion abriendo {src}: {e}")
            return None

    def _run_loop(self):
        frame_time = time.time()
        while self.is_running:
            try:
                with self.lock:
                    needs_open = (self.cap is None or not self.cap.isOpened())
                    curr_source = self.source

                if needs_open:
                    new_cap = self._open_capture_for_src(curr_source)
                    if new_cap is None:
                        time.sleep(0.5)
                        continue
                    with self.lock:
                        if self.cap is not None:
                            try:
                                self.cap.release()
                            except Exception:
                                pass
                        self.cap = new_cap
                        w = int(new_cap.get(cv2.CAP_PROP_FRAME_WIDTH)) or 1280
                        h = int(new_cap.get(cv2.CAP_PROP_FRAME_HEIGHT)) or 720
                        if w > 1280:
                            scale = 1280.0 / w
                            self.frame_width = 1280
                            self.frame_height = int(h * scale)
                        else:
                            self.frame_width = w
                            self.frame_height = h

                # Read frame safely
                with self.lock:
                    active_cap = self.cap
                    active_source = self.source

                if active_cap is None:
                    time.sleep(0.05)
                    continue

                ret, frame = active_cap.read()
                if not ret:
                    if isinstance(active_source, str) and os.path.exists(str(active_source)):
                        with self.lock:
                            if self.cap is not None:
                                self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                        time.sleep(0.03)
                        continue
                    else:
                        time.sleep(0.05)
                        continue

                loop_start = time.time()

                # Scale frame using sharp INTER_AREA downscaling to HD 720p (crisp and detailed)
                h, w = frame.shape[:2]
                if w > 1280:
                    scale = 1280.0 / w
                    frame = cv2.resize(frame, (1280, int(h * scale)), interpolation=cv2.INTER_AREA)

                with self.lock:
                    self.latest_frame = frame

                # Run vehicle detection, ByteTrack and spot occupancy overlay
                annotated_frame, kpis = self.detector.process_frame(frame)

                now = time.time()
                dt = now - frame_time
                frame_time = now
                if dt > 0:
                    self.fps = round(0.9 * self.fps + 0.1 * (1.0 / dt), 1)

                # High-fidelity JPEG encoding (Quality 82, crystal clear)
                encode_params = [
                    cv2.IMWRITE_JPEG_QUALITY, 82,
                    cv2.IMWRITE_JPEG_OPTIMIZE, 0
                ]
                success, buffer = cv2.imencode('.jpg', annotated_frame, encode_params)
                if success:
                    self.latest_frame_bytes = buffer.tobytes()

                # Frame pacing: Target ~25 FPS so CPU and GPU rest between frames
                elapsed = time.time() - loop_start
                sleep_needed = max(0.005, 0.040 - elapsed)
                time.sleep(sleep_needed)

            except Exception as e:
                print(f"[VideoStream] Error en bucle de captura: {e}")
                time.sleep(0.1)

    async def generate_frames(self):
        """Asynchronous frame generator that never blocks FastAPI's event loop."""
        while self.is_running:
            if self.latest_frame_bytes is not None:
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + self.latest_frame_bytes + b'\r\n')
            await asyncio.sleep(0.035)

    def get_frame(self) -> Optional[np.ndarray]:
        with self.lock:
            if self.latest_frame is not None:
                return self.latest_frame.copy()
            return None

    def get_info(self) -> Dict[str, Any]:
        return {
            "source": self.source,
            "is_file": self.is_file,
            "width": self.frame_width,
            "height": self.frame_height,
            "fps": round(self.fps, 1),
            "is_active": self.is_running and self.cap is not None and self.cap.isOpened()
        }
