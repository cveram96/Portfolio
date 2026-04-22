from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db.models import Base, OccupancyLog, Alert, Metric

DATABASE_URL = "sqlite:///./parking.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)

def log_occupancy_change(space_id: int, is_occupied: bool):
    db = SessionLocal()
    log = OccupancyLog(space_id=space_id, is_occupied=is_occupied)
    db.add(log)
    db.commit()
    db.close()

def create_alert(message: str):
    db = SessionLocal()
    alert = Alert(message=message)
    db.add(alert)
    db.commit()
    db.close()

def save_metric(name: str, value: float):
    db = SessionLocal()
    metric = Metric(metric_name=name, value=value)
    db.add(metric)
    db.commit()
    db.close()

def get_recent_alerts(limit=10):
    db = SessionLocal()
    alerts = db.query(Alert).order_by(Alert.timestamp.desc()).limit(limit).all()
    db.close()
    return [{"message": a.message, "timestamp": a.timestamp.isoformat()} for a in alerts]

def get_metrics():
    db = SessionLocal()
    metrics = db.query(Metric).order_by(Metric.timestamp.desc()).limit(20).all()
    db.close()
    return [{"name": m.metric_name, "value": m.value, "timestamp": m.timestamp.isoformat()} for m in metrics]
