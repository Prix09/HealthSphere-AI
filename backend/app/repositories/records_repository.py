from sqlalchemy.orm import Session
from app.models.records import HealthRecord, EnvironmentalRecord, FitnessRecord, NutritionRecord
from typing import List

class RecordsRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_health_records(self, user_id: int = None, skip: int = 0, limit: int = 100) -> List[HealthRecord]:
        q = self.db.query(HealthRecord)
        if user_id:
            q = q.filter(HealthRecord.user_id == user_id)
        return q.order_by(HealthRecord.record_date.desc(), HealthRecord.id.desc()).offset(skip).limit(limit).all()

    def get_environmental_records(self, user_id: int = None, skip: int = 0, limit: int = 100) -> List[EnvironmentalRecord]:
        q = self.db.query(EnvironmentalRecord)
        if user_id:
            q = q.filter(EnvironmentalRecord.user_id == user_id)
        return q.order_by(EnvironmentalRecord.record_date.desc(), EnvironmentalRecord.id.desc()).offset(skip).limit(limit).all()

    def get_fitness_records(self, user_id: int = None, skip: int = 0, limit: int = 100) -> List[FitnessRecord]:
        q = self.db.query(FitnessRecord)
        if user_id:
            q = q.filter(FitnessRecord.user_id == user_id)
        return q.order_by(FitnessRecord.record_date.desc(), FitnessRecord.id.desc()).offset(skip).limit(limit).all()

    def get_nutrition_records(self, user_id: int = None, skip: int = 0, limit: int = 100) -> List[NutritionRecord]:
        q = self.db.query(NutritionRecord)
        if user_id:
            q = q.filter(NutritionRecord.user_id == user_id)
        return q.order_by(NutritionRecord.record_date.desc(), NutritionRecord.id.desc()).offset(skip).limit(limit).all()
