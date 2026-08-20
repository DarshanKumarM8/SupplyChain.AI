"""
Database ORM Models
=====================
SQLAlchemy models for PostgreSQL persistence.
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, Boolean
from sqlalchemy.orm import DeclarativeBase
from datetime import datetime


class Base(DeclarativeBase):
    pass


class Scenario(Base):
    __tablename__ = "scenarios"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    node_count = Column(Integer, default=120)
    graph_data = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)


class SimulationRun(Base):
    __tablename__ = "simulation_runs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    scenario_id = Column(String, nullable=False)
    beta = Column(Float, default=0.6)
    adoption_pct = Column(Float, default=0.0)
    shock_intensity = Column(Float, default=0.85)
    naive_index_peak = Column(Float)
    ai_index_peak = Column(Float)
    cost_naive = Column(Float)
    cost_ai = Column(Float)
    result_data = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)


class ManifoldFrame(Base):
    __tablename__ = "manifold_frames"

    id = Column(Integer, primary_key=True, autoincrement=True)
    frame_id = Column(Integer, unique=True)
    beta = Column(Float, nullable=False)
    adoption_pct = Column(Float, nullable=False)
    shock_intensity = Column(Float, nullable=False)
    frame_data = Column(JSON, nullable=False)
