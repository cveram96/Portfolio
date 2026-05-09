from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
from db.models import Base, OccupancyLog, Alert, Metric, ParkingSpace
import json
import csv
import os
from datetime import datetime

DATABASE_URL = "sqlite:///./parking.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """Context manager for database sessions."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    Base.metadata.create_all(bind=engine)

def log_occupancy_change(space_id: int, is_occupied: bool):
    db = SessionLocal()
    try:
        log = OccupancyLog(space_id=space_id, is_occupied=is_occupied)
        db.add(log)
        db.commit()
        
        # Guardar en CSV automáticamente
        try:
            file_exists = os.path.isfile('parking_occupancy_log.csv')
            with open('parking_occupancy_log.csv', 'a', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f)
                if not file_exists:
                    writer.writerow(['timestamp', 'space_id', 'is_occupied'])
                writer.writerow([datetime.now().strftime('%Y-%m-%d %H:%M:%S'), space_id, 1 if is_occupied else 0])
        except Exception as e:
            print(f"Error al guardar CSV: {e}")
            
    finally:
        db.close()

def log_periodic_state(states: dict):
    """Guarda el estado de todos los espacios cada N segundos."""
    db = SessionLocal()
    try:
        now = datetime.now()
        # Guardar en DB
        for space_id, is_occupied in states.items():
            log = OccupancyLog(space_id=space_id, is_occupied=is_occupied, timestamp=now)
            db.add(log)
        db.commit()
        
        # Guardar en CSV
        try:
            file_exists = os.path.isfile('parking_occupancy_log.csv')
            with open('parking_occupancy_log.csv', 'a', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f)
                if not file_exists:
                    writer.writerow(['timestamp', 'space_id', 'is_occupied'])
                for space_id, is_occupied in states.items():
                    writer.writerow([now.strftime('%Y-%m-%d %H:%M:%S'), space_id, 1 if is_occupied else 0])
        except:
            pass
    finally:
        db.close()

def create_alert(message: str):
    db = SessionLocal()
    try:
        alert = Alert(message=message)
        db.add(alert)
        db.commit()
    finally:
        db.close()

def save_metric(name: str, value: float):
    db = SessionLocal()
    try:
        metric = Metric(metric_name=name, value=value)
        db.add(metric)
        db.commit()
    finally:
        db.close()

def get_recent_alerts(limit=10):
    db = SessionLocal()
    try:
        alerts = db.query(Alert).order_by(Alert.timestamp.desc()).limit(limit).all()
        return [{"message": a.message, "timestamp": a.timestamp.isoformat()} for a in alerts]
    finally:
        db.close()

def get_metrics():
    db = SessionLocal()
    try:
        metrics = db.query(Metric).order_by(Metric.timestamp.desc()).limit(20).all()
        return [{"name": m.metric_name, "value": m.value, "timestamp": m.timestamp.isoformat()} for m in metrics]
    finally:
        db.close()

def get_occupancy_report(limit=5000):
    """Get occupancy logs with space names and types."""
    db = SessionLocal()
    try:
        results = db.query(
            OccupancyLog.id,
            OccupancyLog.space_id,
            OccupancyLog.is_occupied,
            OccupancyLog.timestamp,
            ParkingSpace.poly_data,
            ParkingSpace.space_type
        ).outerjoin(ParkingSpace, OccupancyLog.space_id == ParkingSpace.id
        ).order_by(OccupancyLog.id.desc()).limit(limit).all()
        
        report = []
        for row in results:
            space_name = f'Espacio {row.space_id}'
            if row.poly_data:
                try:
                    data = json.loads(row.poly_data)
                    if isinstance(data, dict) and 'name' in data and data['name']:
                        space_name = data['name']
                except:
                    pass
            
            report.append({
                'id': row.id,
                'space_id': row.space_id,
                'space_name': space_name,
                'space_type': row.space_type or 'Estándar',
                'is_occupied': row.is_occupied,
                'timestamp': row.timestamp
            })
        return report
    finally:
        db.close()
