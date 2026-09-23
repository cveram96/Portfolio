import sqlite3
import json
import os
from typing import List, Dict, Any, Optional
from datetime import datetime
from app.config.settings import DB_PATH

def get_db_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Table for configured parking spots
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS spots (
        id TEXT PRIMARY KEY,
        label TEXT NOT NULL,
        spot_type TEXT NOT NULL DEFAULT 'car',
        points_json TEXT NOT NULL,
        created_at TEXT NOT NULL
    );
    """)

    # Table for parking sessions (historical & active)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS parking_sessions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        spot_id TEXT NOT NULL,
        vehicle_track_id INTEGER NOT NULL,
        vehicle_type TEXT NOT NULL DEFAULT 'Automóvil',
        entry_time TEXT NOT NULL,
        exit_time TEXT,
        duration_seconds INTEGER DEFAULT 0,
        status TEXT NOT NULL DEFAULT 'active',
        created_at TEXT NOT NULL
    );
    """)

    # Table for exclusion / mask zones
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS exclusion_zones (
        id TEXT PRIMARY KEY,
        label TEXT NOT NULL,
        points_json TEXT NOT NULL,
        created_at TEXT NOT NULL
    );
    """)

    cursor.execute("CREATE INDEX IF NOT EXISTS idx_sessions_spot ON parking_sessions(spot_id);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_sessions_status ON parking_sessions(status);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_sessions_entry ON parking_sessions(entry_time);")

    conn.commit()
    conn.close()

# Database helper functions
def db_save_spot(spot_id: str, label: str, spot_type: str, points: List[List[int]]):
    conn = get_db_connection()
    cursor = conn.cursor()
    now = datetime.now().isoformat()
    cursor.execute("""
        INSERT INTO spots (id, label, spot_type, points_json, created_at)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(id) DO UPDATE SET
            label=excluded.label,
            spot_type=excluded.spot_type,
            points_json=excluded.points_json
    """, (spot_id, label, spot_type, json.dumps(points), now))
    conn.commit()
    conn.close()

def db_get_all_spots() -> List[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, label, spot_type, points_json, created_at FROM spots ORDER BY id ASC")
    rows = cursor.fetchall()
    conn.close()
    result = []
    for r in rows:
        result.append({
            "id": r["id"],
            "label": r["label"],
            "spot_type": r["spot_type"],
            "points": json.loads(r["points_json"]),
            "created_at": r["created_at"]
        })
    return result

def db_delete_spot(spot_id: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM spots WHERE id = ?", (spot_id,))
    conn.commit()
    conn.close()

def db_clear_spots():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM spots")
    conn.commit()
    conn.close()

def db_record_entry(spot_id: str, track_id: int, vehicle_type: str, entry_time: datetime) -> int:
    conn = get_db_connection()
    cursor = conn.cursor()
    now_str = entry_time.isoformat()
    cursor.execute("""
        INSERT INTO parking_sessions (spot_id, vehicle_track_id, vehicle_type, entry_time, status, created_at)
        VALUES (?, ?, ?, ?, 'active', ?)
    """, (spot_id, track_id, vehicle_type, now_str, now_str))
    session_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return session_id

def db_record_exit(session_id: int, exit_time: datetime, duration_seconds: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE parking_sessions
        SET exit_time = ?, duration_seconds = ?, status = 'completed'
        WHERE id = ?
    """, (exit_time.isoformat(), duration_seconds, session_id))
    conn.commit()
    conn.close()

def db_get_sessions(limit: int = 100, spot_id: Optional[str] = None, status: Optional[str] = None) -> List[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    query = "SELECT id, spot_id, vehicle_track_id, vehicle_type, entry_time, exit_time, duration_seconds, status FROM parking_sessions"
    params = []
    conditions = []
    if spot_id:
        conditions.append("spot_id = ?")
        params.append(spot_id)
    if status:
        conditions.append("status = ?")
        params.append(status)
    
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    query += " ORDER BY id DESC LIMIT ?"
    params.append(limit)

    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

# Exclusion Zones CRUD
def db_save_exclusion_zone(zone_id: str, label: str, points: List[List[int]]):
    conn = get_db_connection()
    cursor = conn.cursor()
    now = datetime.now().isoformat()
    cursor.execute("""
        INSERT INTO exclusion_zones (id, label, points_json, created_at)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(id) DO UPDATE SET
            label=excluded.label,
            points_json=excluded.points_json
    """, (zone_id, label, json.dumps(points), now))
    conn.commit()
    conn.close()

def db_get_all_exclusion_zones() -> List[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, label, points_json, created_at FROM exclusion_zones ORDER BY id ASC")
    rows = cursor.fetchall()
    conn.close()
    result = []
    for r in rows:
        result.append({
            "id": r["id"],
            "label": r["label"],
            "points": json.loads(r["points_json"]),
            "created_at": r["created_at"]
        })
    return result

def db_delete_exclusion_zone(zone_id: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM exclusion_zones WHERE id = ?", (zone_id,))
    conn.commit()
    conn.close()

def db_clear_exclusion_zones():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM exclusion_zones")
    conn.commit()
    conn.close()

