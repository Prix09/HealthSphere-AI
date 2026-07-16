from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey, Date, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.base import Base

class HealthRecord(Base):
    __tablename__ = "health_records"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    record_date = Column(Date, nullable=False)
    health_score = Column(Float)
    bmi = Column(Float)
    risk_index = Column(Float)
    extra_data = Column(JSON, default={})
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="health_records")

class EnvironmentalRecord(Base):
    __tablename__ = "environmental_records"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    record_date = Column(Date, nullable=False)
    air_quality_index = Column(Float)
    exposure_index = Column(Float)
    extra_data = Column(JSON, default={})
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="environmental_records")

class FitnessRecord(Base):
    __tablename__ = "fitness_records"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    record_date = Column(Date, nullable=False)
    steps = Column(Integer)
    activity_index = Column(Float)
    sleep_score = Column(Float)
    extra_data = Column(JSON, default={})
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="fitness_records")

class NutritionRecord(Base):
    __tablename__ = "nutrition_records"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    record_date = Column(Date, nullable=False)
    calories_intake = Column(Float)
    nutrition_score = Column(Float)
    extra_data = Column(JSON, default={})
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="nutrition_records")
