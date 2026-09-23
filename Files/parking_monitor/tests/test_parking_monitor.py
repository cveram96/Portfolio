import os
import sys
import unittest
import numpy as np
from datetime import datetime, timedelta

# Add root to sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from app.utils.device_utils import get_system_gpu_info, get_system_cpu_info, resolve_device_config
from app.db.database import (
    init_db, db_save_spot, db_get_all_spots, db_delete_spot,
    db_record_entry, db_record_exit, db_get_sessions
)
from app.vision.spot_manager import SpotManager, ParkingSpot
from app.utils.report_exporter import generate_csv_report, get_parking_analytics_summary
from fastapi.testclient import TestClient
from app.main import app

class TestParkingMonitor(unittest.TestCase):
    def setUp(self):
        init_db()

    def test_hardware_detection(self):
        gpu = get_system_gpu_info()
        cpu = get_system_cpu_info()
        self.assertIsNotNone(gpu)
        self.assertIsNotNone(cpu)
        print(f"\n[Hardware Test] GPU detectada: {gpu} | CPU detectada: {cpu}")
        
        mode, model_path, msg = resolve_device_config("auto")
        self.assertIn(mode, ["gpu_dml", "gpu_cuda", "cpu"])
        print(f"[Device Resolution] Modo: {mode} | Modelo: {os.path.basename(model_path)} | Mensaje: {msg}")

    def test_database_and_sessions(self):
        spot_id = "TEST-01"
        pts = [[100, 100], [200, 100], [200, 300], [100, 300]]
        db_save_spot(spot_id, "Bay Test 1", "car", pts)
        
        spots = db_get_all_spots()
        self.assertTrue(any(s["id"] == spot_id for s in spots))

        entry_time = datetime.now() - timedelta(minutes=15)
        session_id = db_record_entry(spot_id, 99, "Car", entry_time)
        self.assertIsNotNone(session_id)

        exit_time = datetime.now()
        db_record_exit(session_id, exit_time, 900)

        sessions = db_get_sessions(spot_id=spot_id)
        self.assertTrue(len(sessions) >= 1)
        self.assertEqual(sessions[0]["status"], "completed")
        self.assertEqual(sessions[0]["duration_seconds"], 900)

        db_delete_spot(spot_id)

    def test_spot_geometry_and_occupancy(self):
        sm = SpotManager()
        spot_id = "GEO-01"
        pts = [[100, 100], [200, 100], [200, 200], [100, 200]]
        sm.add_or_update_spot(spot_id, "Bay Geo", pts, "car")

        vehicle_inside = [{
            "track_id": 5,
            "class_name": "Car",
            "bbox": [110, 110, 190, 190],
            "center": (150, 150)
        }]

        for _ in range(6):
            sm.update_occupancy(vehicle_inside)

        spot = sm.spots[spot_id]
        self.assertTrue(spot.is_occupied)
        self.assertEqual(spot.current_vehicle_id, 5)

        dummy_frame = np.zeros((480, 640, 3), dtype=np.uint8)
        rendered = sm.draw_spots(dummy_frame)
        self.assertEqual(rendered.shape, (480, 640, 3))

        for _ in range(6):
            sm.update_occupancy([])

        self.assertFalse(spot.is_occupied)
        sm.delete_spot(spot_id)

    def test_reports(self):
        csv_data = generate_csv_report()
        self.assertIn("Session ID", csv_data)
        self.assertIn("Bay / Spot ID", csv_data)

        summary = get_parking_analytics_summary()
        self.assertIn("total_spots", summary)
        self.assertIn("avg_duration_formatted", summary)

    def test_fastapi_endpoints(self):
        with TestClient(app) as client:
            res_dev = client.get("/api/device")
            self.assertEqual(res_dev.status_code, 200)
            self.assertIn("gpu_name", res_dev.json())

            res_src = client.get("/api/sources")
            self.assertEqual(res_src.status_code, 200)
            self.assertIn("samples", res_src.json())

            res_spots = client.get("/api/spots")
            self.assertEqual(res_spots.status_code, 200)

            res_stats = client.get("/api/stats/live")
            self.assertEqual(res_stats.status_code, 200)

            res_csv = client.get("/api/reports/download-csv")
            self.assertEqual(res_csv.status_code, 200)
            self.assertEqual(res_csv.headers["content-type"], "text/csv; charset=utf-8")

            # Test create spot
            res_create = client.post("/api/spots", json={
                "id": "T-PUT-1",
                "label": "Initial Bay",
                "spot_type": "car",
                "points": [[10, 10], [50, 10], [50, 50], [10, 50]]
            })
            self.assertEqual(res_create.status_code, 200)

            # Test edit spot (PUT)
            res_edit = client.put("/api/spots/T-PUT-1", json={
                "new_id": "T-PUT-RENAMED",
                "label": "VIP Bay Edited",
                "spot_type": "disabled"
            })
            self.assertEqual(res_edit.status_code, 200)
            self.assertEqual(res_edit.json()["spot"]["label"], "VIP Bay Edited")
            self.assertEqual(res_edit.json()["spot"]["id"], "T-PUT-RENAMED")

            # Cleanup
            client.delete("/api/spots/T-PUT-RENAMED")

            # Test Exclusion Zones API
            res_ez = client.post("/api/exclusions", json={
                "id": "EZ-TEST-1",
                "label": "Zona Calle Test",
                "points": [[0, 0], [100, 0], [100, 100], [0, 100]]
            })
            self.assertEqual(res_ez.status_code, 200)
            self.assertEqual(res_ez.json()["exclusion"]["id"], "EZ-TEST-1")

            res_ez_list = client.get("/api/exclusions")
            self.assertEqual(res_ez_list.status_code, 200)
            self.assertTrue(any(z["id"] == "EZ-TEST-1" for z in res_ez_list.json()))

            res_ez_del = client.delete("/api/exclusions/EZ-TEST-1")
            self.assertEqual(res_ez_del.status_code, 200)

if __name__ == "__main__":
    unittest.main()
