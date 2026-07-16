from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime

class HealthRecordBase(BaseModel):
    user_id: int
    record_date: date
    health_score: Optional[float] = None
    bmi: Optional[float] = None
    risk_index: Optional[float] = None
    extra_data: Optional[dict] = {}

class HealthRecordCreate(HealthRecordBase):
    pass

class HealthRecord(HealthRecordBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class EnvironmentalRecordBase(BaseModel):
    user_id: int
    record_date: date
    air_quality_index: Optional[float] = None
    exposure_index: Optional[float] = None
    extra_data: Optional[dict] = {}

class EnvironmentalRecordCreate(EnvironmentalRecordBase):
    pass

class EnvironmentalRecord(EnvironmentalRecordBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class FitnessRecordBase(BaseModel):
    user_id: int
    record_date: date
    steps: Optional[int] = None
    activity_index: Optional[float] = None
    sleep_score: Optional[float] = None
    extra_data: Optional[dict] = {}

class FitnessRecordCreate(FitnessRecordBase):
    pass

class FitnessRecord(FitnessRecordBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
