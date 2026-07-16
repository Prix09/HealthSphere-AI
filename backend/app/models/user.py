from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.base import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    health_records = relationship("HealthRecord", back_populates="user", cascade="all, delete")
    environmental_records = relationship("EnvironmentalRecord", back_populates="user", cascade="all, delete")
    fitness_records = relationship("FitnessRecord", back_populates="user", cascade="all, delete")
    nutrition_records = relationship("NutritionRecord", back_populates="user", cascade="all, delete")
