import json
import os
import cv2
import numpy as np
from datetime import datetime
from typing import Dict, List, Tuple, Any, Optional
from shapely.geometry import Polygon, Point

from app.config.settings import SPOTS_FILE, EXCLUSION_ZONES_FILE, SPOT_OCCUPANCY_IOU_THRESHOLD, SPOT_DEBOUNCE_FRAMES
from app.db.database import (
    db_save_spot, db_get_all_spots, db_delete_spot, db_clear_spots,
    db_record_entry, db_record_exit,
    db_save_exclusion_zone, db_get_all_exclusion_zones, db_delete_exclusion_zone, db_clear_exclusion_zones
)

class ExclusionZone:
    """Mask / exclusion zone where vehicle detection and tracking are completely ignored."""
    def __init__(self, zone_id: str, label: str, points: List[List[int]]):
        self.id = zone_id
        self.label = label
        self.points = [list(pt) for pt in points]

    def get_points_for_frame(self, frame_w: int, frame_h: int) -> List[List[int]]:
        if not self.points:
            return []
        if all(0.0 <= pt[0] <= 1.0 and 0.0 <= pt[1] <= 1.0 for pt in self.points):
            return [[int(round(pt[0] * frame_w)), int(round(pt[1] * frame_h))] for pt in self.points]
            
        max_x = max(pt[0] for pt in self.points)
        max_y = max(pt[1] for pt in self.points)
        
        if max_x > frame_w or max_y > frame_h:
            if max_x > 1280 or max_y > 720:
                ref_w, ref_h = 1920, 1080
            elif max_x > 960 or max_y > 540:
                ref_w, ref_h = 1280, 720
            else:
                ref_w, ref_h = max(max_x, frame_w), max(max_y, frame_h)
                
            scale_x = frame_w / float(ref_w)
            scale_y = frame_h / float(ref_h)
            return [[int(round(pt[0] * scale_x)), int(round(pt[1] * scale_y))] for pt in self.points]
            
        return [[int(round(pt[0])), int(round(pt[1]))] for pt in self.points]

    def get_shapely_polygon(self, frame_w: int, frame_h: int) -> Optional[Polygon]:
        pts = self.get_points_for_frame(frame_w, frame_h)
        if len(pts) >= 3:
            try:
                poly = Polygon(pts)
                if poly.is_valid:
                    return poly
                return poly.buffer(0)
            except Exception:
                return None
        return None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "label": self.label,
            "points": self.points
        }

class ParkingSpot:
    def __init__(self, spot_id: str, label: str, points: List[List[int]], spot_type: str = "car"):
        self.id = spot_id
        self.label = label
        self.spot_type = spot_type
        self.points = [list(pt) for pt in points]
        
        # Live state
        self.is_occupied: bool = False
        self.current_vehicle_id: Optional[int] = None
        self.current_vehicle_type: Optional[str] = None
        self.entry_time: Optional[datetime] = None
        self.session_id: Optional[int] = None
        
        # Debouncing counters to prevent flickering
        self.occupied_counter: int = 0
        self.vacant_counter: int = 0

    def get_points_for_frame(self, frame_w: int, frame_h: int) -> List[List[int]]:
        """
        Dynamically scales stored polygon coordinates to fit the current frame resolution (frame_w, frame_h).
        Handles points saved in:
        1. Original 1920x1080 (1080p)
        2. Original 1280x720 (720p)
        3. Normalized coordinates (0.0 to 1.0)
        4. Current frame resolution
        """
        if not self.points:
            return []
        
        # Normalized coordinates (0.0 to 1.0)
        if all(0.0 <= pt[0] <= 1.0 and 0.0 <= pt[1] <= 1.0 for pt in self.points):
            return [[int(round(pt[0] * frame_w)), int(round(pt[1] * frame_h))] for pt in self.points]
            
        max_x = max(pt[0] for pt in self.points)
        max_y = max(pt[1] for pt in self.points)
        
        # If coordinates are beyond frame boundaries, detect original reference resolution
        if max_x > frame_w or max_y > frame_h:
            if max_x > 1280 or max_y > 720:
                ref_w, ref_h = 1920, 1080
            elif max_x > 960 or max_y > 540:
                ref_w, ref_h = 1280, 720
            else:
                ref_w, ref_h = max(max_x, frame_w), max(max_y, frame_h)
                
            scale_x = frame_w / float(ref_w)
            scale_y = frame_h / float(ref_h)
            return [[int(round(pt[0] * scale_x)), int(round(pt[1] * scale_y))] for pt in self.points]
            
        return [[int(round(pt[0])), int(round(pt[1]))] for pt in self.points]

    def get_shapely_polygon(self, frame_w: int, frame_h: int) -> Optional[Polygon]:
        pts = self.get_points_for_frame(frame_w, frame_h)
        if len(pts) >= 3:
            try:
                poly = Polygon(pts)
                if poly.is_valid:
                    return poly
                return poly.buffer(0)
            except Exception:
                return None
        return None

    def to_dict(self) -> Dict[str, Any]:
        duration_sec = 0
        if self.is_occupied and self.entry_time:
            duration_sec = int((datetime.now() - self.entry_time).total_seconds())

        return {
            "id": self.id,
            "label": self.label,
            "spot_type": self.spot_type,
            "points": self.points,
            "is_occupied": self.is_occupied,
            "vehicle_id": self.current_vehicle_id,
            "vehicle_type": self.current_vehicle_type,
            "entry_time": self.entry_time.isoformat() if self.entry_time else None,
            "duration_seconds": duration_sec
        }

class SpotManager:
    def __init__(self):
        self.spots: Dict[str, ParkingSpot] = {}
        self.exclusion_zones: Dict[str, ExclusionZone] = {}
        self.load_spots()
        self.load_exclusion_zones()

    def load_exclusion_zones(self):
        """Loads exclusion / mask zones from database or fallback JSON file."""
        db_ez = db_get_all_exclusion_zones()
        if db_ez:
            for z in db_ez:
                self.exclusion_zones[z["id"]] = ExclusionZone(
                    zone_id=z["id"],
                    label=z["label"],
                    points=z["points"]
                )
        elif os.path.exists(EXCLUSION_ZONES_FILE):
            try:
                with open(EXCLUSION_ZONES_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for z in data:
                        zone = ExclusionZone(z["id"], z["label"], z["points"])
                        self.exclusion_zones[z["id"]] = zone
                        db_save_exclusion_zone(zone.id, zone.label, zone.points)
            except Exception as e:
                print(f"[SpotManager] Error cargando exclusion_zones.json: {e}")

    def save_exclusion_zones_backup(self):
        data = [z.to_dict() for z in self.exclusion_zones.values()]
        try:
            with open(EXCLUSION_ZONES_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"[SpotManager] Error guardando exclusion backup JSON: {e}")

    def add_or_update_exclusion_zone(self, zone_id: str, label: str, points: List[List[int]]) -> ExclusionZone:
        zone = ExclusionZone(zone_id, label, points)
        self.exclusion_zones[zone_id] = zone
        db_save_exclusion_zone(zone_id, label, points)
        self.save_exclusion_zones_backup()
        return zone

    def delete_exclusion_zone(self, zone_id: str) -> bool:
        if zone_id in self.exclusion_zones:
            del self.exclusion_zones[zone_id]
            db_delete_exclusion_zone(zone_id)
            self.save_exclusion_zones_backup()
            return True
        return False

    def clear_all_exclusion_zones(self):
        self.exclusion_zones.clear()
        db_clear_exclusion_zones()
        self.save_exclusion_zones_backup()

    def get_all_exclusion_zones(self) -> List[Dict[str, Any]]:
        return [z.to_dict() for z in self.exclusion_zones.values()]

    def is_in_exclusion_zone(self, center_point: Point, frame_w: int, frame_h: int) -> bool:
        """Returns True if the point lies inside any defined exclusion/mask zone."""
        if not self.exclusion_zones:
            return False
        for zone in self.exclusion_zones.values():
            poly = zone.get_shapely_polygon(frame_w, frame_h)
            if poly and poly.is_valid and poly.contains(center_point):
                return True
        return False

    def load_spots(self):
        """Loads spots from database or fallback JSON file."""
        db_spots = db_get_all_spots()
        if db_spots:
            for s in db_spots:
                self.spots[s["id"]] = ParkingSpot(
                    spot_id=s["id"],
                    label=s["label"],
                    points=s["points"],
                    spot_type=s.get("spot_type", "car")
                )
        elif os.path.exists(SPOTS_FILE):
            try:
                with open(SPOTS_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for s in data:
                        spot = ParkingSpot(
                            spot_id=s["id"],
                            label=s["label"],
                            points=s["points"],
                            spot_type=s.get("spot_type", "car")
                        )
                        self.spots[s["id"]] = spot
                        db_save_spot(spot.id, spot.label, spot.spot_type, spot.points)
            except Exception as e:
                print(f"[SpotManager] Error cargando spots.json: {e}")

    def save_spots_backup(self):
        """Saves current spots to local JSON file for extra backup."""
        data = [s.to_dict() for s in self.spots.values()]
        try:
            with open(SPOTS_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"[SpotManager] Error guardando backup JSON: {e}")

    def add_or_update_spot(self, spot_id: str, label: str, points: List[List[int]], spot_type: str = "car") -> ParkingSpot:
        spot = ParkingSpot(spot_id, label, points, spot_type)
        self.spots[spot_id] = spot
        db_save_spot(spot_id, label, spot_type, points)
        self.save_spots_backup()
        return spot

    def update_spot_metadata(self, old_id: str, new_id: str, new_label: str, new_spot_type: str = "car") -> Optional[ParkingSpot]:
        if old_id not in self.spots:
            return None
        spot = self.spots[old_id]
        points = spot.points
        if old_id != new_id:
            del self.spots[old_id]
            db_delete_spot(old_id)
            spot.id = new_id
        spot.label = new_label
        spot.spot_type = new_spot_type
        self.spots[new_id] = spot
        db_save_spot(new_id, new_label, new_spot_type, points)
        self.save_spots_backup()
        return spot

    def delete_spot(self, spot_id: str) -> bool:
        if spot_id in self.spots:
            # If occupied, close active session
            spot = self.spots[spot_id]
            if spot.is_occupied and spot.session_id:
                now = datetime.now()
                dur = int((now - spot.entry_time).total_seconds()) if spot.entry_time else 0
                db_record_exit(spot.session_id, now, dur)
                
            del self.spots[spot_id]
            db_delete_spot(spot_id)
            self.save_spots_backup()
            return True
        return False

    def clear_all(self):
        for spot in self.spots.values():
            if spot.is_occupied and spot.session_id:
                now = datetime.now()
                dur = int((now - spot.entry_time).total_seconds()) if spot.entry_time else 0
                db_record_exit(spot.session_id, now, dur)
        self.spots.clear()
        db_clear_spots()
        self.save_spots_backup()

    def get_all_spots(self) -> List[Dict[str, Any]]:
        return [s.to_dict() for s in self.spots.values()]

    def update_occupancy(self, detected_vehicles: List[Dict[str, Any]], frame_w: Optional[int] = None, frame_h: Optional[int] = None):
        """
        detected_vehicles is a list of:
        {
          "track_id": int,
          "class_name": str,
          "bbox": [x1, y1, x2, y2],
          "center": (cx, cy)
        }
        Calculates geometric overlap with each parking spot and updates states.
        """
        now = datetime.now()
        
        # Determine frame dimensions
        if frame_w is None or frame_h is None:
            max_bx = max([v["bbox"][2] for v in detected_vehicles] + [960])
            max_by = max([v["bbox"][3] for v in detected_vehicles] + [540])
            frame_w = 1920 if max_bx > 1280 else (1280 if max_bx > 960 else 960)
            frame_h = 1080 if max_by > 720 else (720 if max_by > 540 else 540)
        
        # 1. Perspective Parallax Compensation (Ground Contact Footprint & Wheelbase Center)
        # In angled / CCTV surveillance, the top portion (roof, windows) of a 3D vehicle
        # projects into adjacent spots. The vehicle's true physical position is where the tires
        # touch the asphalt ground plane (bottom 45% of the bounding box).
        vehicle_geoms = []
        for v in detected_vehicles:
            x1, y1, x2, y2 = v["bbox"]
            bw = x2 - x1
            bh = y2 - y1
            cx = (x1 + x2) // 2

            # Ground contact footprint: Bottom 48% of height, inset 8% horizontally
            gx1 = x1 + int(bw * 0.08)
            gx2 = x2 - int(bw * 0.08)
            gy1 = y1 + int(bh * 0.52)  # Eliminates roof & windshield perspective tilt!
            gy2 = y2                   # Asphalt contact level

            g_poly = Polygon([(gx1, gy1), (gx2, gy1), (gx2, gy2), (gx1, gy2)])
            # Ground contact point between axles
            ground_pt = Point(cx, int(y2 - bh * 0.18))

            vehicle_geoms.append({
                "track_id": v["track_id"],
                "class_name": v["class_name"],
                "ground_poly": g_poly,
                "ground_center": ground_pt,
                "bbox": v["bbox"]
            })

        # 2. Evaluate Match Quality for all (Spot, Vehicle) candidate pairs
        candidate_matches = []
        for spot_id, spot in self.spots.items():
            poly = spot.get_shapely_polygon(frame_w, frame_h)
            if not poly or not poly.is_valid or poly.area <= 0:
                continue

            spot_area = poly.area

            for v in vehicle_geoms:
                try:
                    g_poly = v["ground_poly"]
                    if not g_poly.is_valid or g_poly.area <= 0:
                        continue

                    inter = poly.intersection(g_poly)
                    if inter.is_empty:
                        continue

                    inter_area = inter.area
                    g_area = g_poly.area

                    g_overlap = inter_area / g_area if g_area > 0 else 0.0
                    s_overlap = inter_area / spot_area if spot_area > 0 else 0.0
                    pt_inside = poly.contains(v["ground_center"])

                    # Perspective scoring:
                    # Ground contact point inside gives high confidence; otherwise requires substantial overlap
                    if pt_inside:
                        score = 0.50 + 0.50 * g_overlap
                    else:
                        score = g_overlap

                    # Minimum threshold to qualify as a valid parking event
                    if (pt_inside and g_overlap >= 0.12) or (g_overlap >= 0.30) or (s_overlap >= 0.30):
                        candidate_matches.append({
                            "score": score,
                            "spot_id": spot_id,
                            "vehicle": v
                        })
                except Exception:
                    continue

        # 3. 1-to-1 Competitive Exclusive Assignment:
        # Sort candidates by match score (highest score wins).
        # A single vehicle can NEVER occupy more than one spot simultaneously!
        candidate_matches.sort(key=lambda m: m["score"], reverse=True)
        assigned_vehicles = set()
        spot_assigned_vehicle = {}  # spot_id -> vehicle

        for match in candidate_matches:
            s_id = match["spot_id"]
            v_id = match["vehicle"]["track_id"]
            if s_id not in spot_assigned_vehicle:
                if v_id is None or v_id not in assigned_vehicles:
                    spot_assigned_vehicle[s_id] = match["vehicle"]
                    if v_id is not None:
                        assigned_vehicles.add(v_id)

        # 4. Debounce and Occupancy State Updates
        for spot_id, spot in self.spots.items():
            best_match_vehicle = spot_assigned_vehicle.get(spot_id)
            frame_is_occupied = (best_match_vehicle is not None)

            if frame_is_occupied:
                spot.occupied_counter += 1
                spot.vacant_counter = 0
                if spot.occupied_counter >= SPOT_DEBOUNCE_FRAMES:
                    v_id = best_match_vehicle["track_id"]
                    v_type = best_match_vehicle["class_name"]

                    if not spot.is_occupied:
                        # NEW ENTRY
                        spot.is_occupied = True
                        spot.current_vehicle_id = v_id
                        spot.current_vehicle_type = v_type
                        spot.entry_time = now
                        spot.session_id = db_record_entry(spot.id, v_id, v_type, now)
                    else:
                        if spot.current_vehicle_id != v_id and v_id is not None:
                            spot.current_vehicle_id = v_id
            else:
                spot.vacant_counter += 1
                spot.occupied_counter = 0
                if spot.vacant_counter >= SPOT_DEBOUNCE_FRAMES:
                    if spot.is_occupied:
                        # VEHICLE EXITED
                        if spot.session_id and spot.entry_time:
                            dur = int((now - spot.entry_time).total_seconds())
                            db_record_exit(spot.session_id, now, dur)
                            
                        spot.is_occupied = False
                        spot.current_vehicle_id = None
                        spot.current_vehicle_type = None
                        spot.entry_time = None
                        spot.session_id = None

    def draw_spots(self, frame: np.ndarray) -> np.ndarray:
        """
        Draws parking spot polygons with colored overlay and status badge:
        - Vacant: Translucent Emerald Green
        - Occupied: Translucent Coral Red with Vehicle ID and Timer badge
        """
        if not self.spots:
            return frame

        frame_h, frame_w = frame.shape[:2]
        overlay = frame.copy()
        alpha = 0.35  # Opacity for filled polygon

        for spot in self.spots.values():
            scaled_pts = spot.get_points_for_frame(frame_w, frame_h)
            if len(scaled_pts) < 3:
                continue

            pts = np.array(scaled_pts, np.int32).reshape((-1, 1, 2))
            
            # Colors in BGR
            if spot.is_occupied:
                fill_color = (40, 40, 230)      # Red BGR
                border_color = (0, 0, 255)
            else:
                fill_color = (46, 204, 113)     # Green BGR
                border_color = (39, 174, 96)

            # Draw translucent filled area
            cv2.fillPoly(overlay, [pts], fill_color)
            # Draw crisp border
            cv2.polylines(frame, [pts], isClosed=True, color=border_color, thickness=2, lineType=cv2.LINE_AA)

        # Blend overlay
        cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)

        # Draw labels and badges on top (not blended)
        for spot in self.spots.values():
            scaled_pts = spot.get_points_for_frame(frame_w, frame_h)
            if len(scaled_pts) < 3:
                continue
                
            pts = np.array(scaled_pts, np.int32)
            # Center of the spot polygon
            M = cv2.moments(pts)
            if M["m00"] != 0:
                cx = int(M["m10"] / M["m00"])
                cy = int(M["m01"] / M["m00"])
            else:
                cx, cy = pts[0][0]

            if spot.is_occupied:
                dur_str = "00:00"
                if spot.entry_time:
                    dur_sec = int((datetime.now() - spot.entry_time).total_seconds())
                    m, s = divmod(dur_sec, 60)
                    h, m = divmod(m, 60)
                    dur_str = f"{h:02d}:{m:02d}:{s:02d}" if h > 0 else f"{m:02d}:{s:02d}"
                
                veh_info = f"#{spot.current_vehicle_id}" if spot.current_vehicle_id else ""
                badge_text = f"{spot.label} [{veh_info}] {dur_str}"
                badge_bg = (20, 20, 180)
            else:
                badge_text = f"{spot.label} VACANT"
                badge_bg = (25, 135, 60)

            # Draw pill badge
            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = 0.45
            thickness = 1
            (w, h), _ = cv2.getTextSize(badge_text, font, font_scale, thickness)

            x1 = cx - w // 2 - 6
            y1 = cy - h // 2 - 4
            x2 = cx + w // 2 + 6
            y2 = cy + h // 2 + 6

            cv2.rectangle(frame, (x1, y1), (x2, y2), badge_bg, -1, cv2.LINE_AA)
            cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 255, 255), 1, cv2.LINE_AA)
            cv2.putText(frame, badge_text, (cx - w // 2, cy + h // 2 - 1),
                        font, font_scale, (255, 255, 255), thickness, cv2.LINE_AA)

        return frame
