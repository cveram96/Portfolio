import time
from datetime import datetime
from typing import Dict, List, Any, Optional

class TrackerStats:
    def __init__(self):
        self.active_tracks: Dict[int, Dict[str, Any]] = {}
        self.total_unique_vehicles_seen: set = set()
        self.fps_counter: float = 0.0
        self.last_time = time.time()
        self.frame_count: int = 0

    def update_fps(self):
        self.frame_count += 1
        now = time.time()
        elapsed = now - self.last_time
        if elapsed >= 1.0:
            self.fps_counter = round(self.frame_count / elapsed, 1)
            self.frame_count = 0
            self.last_time = now

    def register_frame_tracks(self, detected_vehicles: List[Dict[str, Any]]):
        now_dt = datetime.now()
        current_ids = set()

        for v in detected_vehicles:
            tid = v["track_id"]
            if tid is None:
                continue
            current_ids.add(tid)
            self.total_unique_vehicles_seen.add(tid)

            if tid not in self.active_tracks:
                self.active_tracks[tid] = {
                    "id": tid,
                    "class_name": v["class_name"],
                    "first_seen": now_dt,
                    "last_seen": now_dt,
                    "bbox": v["bbox"],
                    "center": v["center"]
                }
            else:
                self.active_tracks[tid]["last_seen"] = now_dt
                self.active_tracks[tid]["bbox"] = v["bbox"]
                self.active_tracks[tid]["center"] = v["center"]

        # Clean tracks not seen for over 10 seconds
        for tid in list(self.active_tracks.keys()):
            if tid not in current_ids:
                age = (now_dt - self.active_tracks[tid]["last_seen"]).total_seconds()
                if age > 10.0:
                    del self.active_tracks[tid]

    def get_kpis(self, spot_manager) -> Dict[str, Any]:
        total_spots = len(spot_manager.spots)
        occupied_spots = sum(1 for s in spot_manager.spots.values() if s.is_occupied)
        available_spots = max(0, total_spots - occupied_spots)
        occupancy_rate = round((occupied_spots / total_spots * 100), 1) if total_spots > 0 else 0.0

        # Calculate average duration of currently occupied spots
        now = datetime.now()
        active_durations = [
            int((now - s.entry_time).total_seconds())
            for s in spot_manager.spots.values()
            if s.is_occupied and s.entry_time
        ]
        avg_active_sec = int(sum(active_durations) / len(active_durations)) if active_durations else 0
        avg_min, avg_sec = divmod(avg_active_sec, 60)
        avg_formatted = f"{avg_min}m {avg_sec:02d}s"

        # List of currently parked vehicles
        parked_vehicles = []
        for s in spot_manager.spots.values():
            if s.is_occupied:
                dur = int((now - s.entry_time).total_seconds()) if s.entry_time else 0
                m, sec = divmod(dur, 60)
                h, m = divmod(m, 60)
                dur_str = f"{h:02d}:{m:02d}:{sec:02d}" if h > 0 else f"{m:02d}:{sec:02d}"
                parked_vehicles.append({
                    "spot_id": s.id,
                    "spot_label": s.label,
                    "vehicle_id": s.current_vehicle_id,
                    "vehicle_type": s.current_vehicle_type or "Automóvil",
                    "entry_time": s.entry_time.strftime("%H:%M:%S") if s.entry_time else "",
                    "duration_seconds": dur,
                    "duration_formatted": dur_str
                })

        return {
            "total_spots": total_spots,
            "occupied_spots": occupied_spots,
            "available_spots": available_spots,
            "occupancy_rate": occupancy_rate,
            "total_vehicles_seen": len(self.total_unique_vehicles_seen),
            "in_frame_vehicles": len(self.active_tracks),
            "avg_stay_formatted": avg_formatted,
            "parked_vehicles": parked_vehicles,
            "fps": self.fps_counter
        }
