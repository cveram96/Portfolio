import csv
import io
from typing import List, Dict, Any
from datetime import datetime
from app.db.database import db_get_sessions, db_get_all_spots

def format_duration(seconds: int) -> str:
    if seconds is None or seconds < 0:
        return "0s"
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    if hours > 0:
        return f"{hours}h {minutes:02d}m {secs:02d}s"
    elif minutes > 0:
        return f"{minutes}m {secs:02d}s"
    else:
        return f"{secs}s"

def generate_csv_report() -> str:
    sessions = db_get_sessions(limit=5000)
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Headers
    writer.writerow([
        "ID Sesión", 
        "Plaza / Espacio", 
        "ID Vehículo (Tracker)", 
        "Tipo de Vehículo", 
        "Fecha y Hora Ingreso", 
        "Fecha y Hora Salida", 
        "Duración Segundos", 
        "Duración Formateada", 
        "Estado"
    ])
    
    for s in sessions:
        entry = s.get("entry_time", "")
        exit_t = s.get("exit_time", "") or "En Parqueadero"
        duration_sec = s.get("duration_seconds", 0)
        formatted_dur = format_duration(duration_sec) if s.get("status") == "completed" else "En curso"
        status_label = "Completado" if s.get("status") == "completed" else "Activo (Estacionado)"
        
        writer.writerow([
            s.get("id"),
            s.get("spot_id"),
            f"#{s.get('vehicle_track_id')}",
            s.get("vehicle_type"),
            entry,
            exit_t,
            duration_sec,
            formatted_dur,
            status_label
        ])
        
    return output.getvalue()

def get_parking_analytics_summary() -> Dict[str, Any]:
    sessions = db_get_sessions(limit=5000)
    spots = db_get_all_spots()
    total_spots = len(spots)
    
    completed_sessions = [s for s in sessions if s.get("status") == "completed"]
    active_sessions = [s for s in sessions if s.get("status") == "active"]
    
    durations = [s.get("duration_seconds", 0) for s in completed_sessions if s.get("duration_seconds")]
    avg_duration_sec = int(sum(durations) / len(durations)) if durations else 0
    
    # Vehicle type breakdown
    type_counts = {}
    for s in sessions:
        vt = s.get("vehicle_type", "Automóvil")
        type_counts[vt] = type_counts.get(vt, 0) + 1

    # Hourly distribution of entries
    hourly_entries = [0] * 24
    for s in sessions:
        entry_str = s.get("entry_time")
        if entry_str:
            try:
                dt = datetime.fromisoformat(entry_str)
                hourly_entries[dt.hour] += 1
            except Exception:
                pass
                
    busiest_hour = hourly_entries.index(max(hourly_entries)) if any(hourly_entries) else 12

    return {
        "total_spots": total_spots,
        "active_parked": len(active_sessions),
        "total_historical_vehicles": len(sessions),
        "completed_stays": len(completed_sessions),
        "avg_duration_seconds": avg_duration_sec,
        "avg_duration_formatted": format_duration(avg_duration_sec),
        "vehicle_type_breakdown": type_counts,
        "busiest_hour": f"{busiest_hour:02d}:00 - {busiest_hour+1:02d}:00",
        "hourly_distribution": hourly_entries
    }
