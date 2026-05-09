from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()

class ParkingSpace(Base):
    __tablename__ = "parking_spaces"
    id = Column(Integer, primary_key=True, index=True)
    poly_data = Column(String)  # JSON string of polygon coordinates
    space_type = Column(String, default="Estándar")  # Estándar, Motos, VIP, Discapacitados

class OccupancyLog(Base):
    __tablename__ = "occupancy_logs"
    id = Column(Integer, primary_key=True, index=True)
    space_id = Column(Integer, index=True)
    is_occupied = Column(Boolean)
    timestamp = Column(DateTime, default=datetime.now)

class Alert(Base):
    __tablename__ = "alerts"
    id = Column(Integer, primary_key=True, index=True)
    message = Column(String)
    timestamp = Column(DateTime, default=datetime.now)

class Metric(Base):
    __tablename__ = "metrics"
    id = Column(Integer, primary_key=True, index=True)
    metric_name = Column(String, index=True)
    value = Column(Float)
    timestamp = Column(DateTime, default=datetime.now)
