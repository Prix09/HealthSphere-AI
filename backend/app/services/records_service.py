from typing import List
from sqlalchemy.orm import Session
from app.repositories.records_repository import RecordsRepository
from app.models.records import HealthRecord, EnvironmentalRecord, FitnessRecord, NutritionRecord

class RecordsService:
    def __init__(self, db: Session):
        self.records_repo = RecordsRepository(db)

    def get_health_records(self, user_id: int = None, skip: int = 0, limit: int = 100) -> List[HealthRecord]:
        return self.records_repo.get_health_records(user_id, skip, limit)

    def get_environmental_records(self, user_id: int = None, skip: int = 0, limit: int = 100) -> List[EnvironmentalRecord]:
        return self.records_repo.get_environmental_records(user_id, skip, limit)

    def get_fitness_records(self, user_id: int = None, skip: int = 0, limit: int = 100) -> List[FitnessRecord]:
        return self.records_repo.get_fitness_records(user_id, skip, limit)

    def get_nutrition_records(self, user_id: int = None, skip: int = 0, limit: int = 100) -> List[NutritionRecord]:
        return self.records_repo.get_nutrition_records(user_id, skip, limit)
