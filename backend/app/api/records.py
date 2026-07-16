from typing import Any, List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api import deps
from app.models.user import User
from app.models.records import HealthRecord, EnvironmentalRecord, FitnessRecord, NutritionRecord
from app.schemas.records import HealthRecord as HealthRecordSchema, EnvironmentalRecord as EnvironmentalRecordSchema, FitnessRecord as FitnessRecordSchema
from app.services.records_service import RecordsService

router = APIRouter()

@router.get("/health", response_model=List[HealthRecordSchema])
def read_health_records(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    records_service = RecordsService(db)
    return records_service.get_health_records(None, skip, limit)

@router.get("/environmental", response_model=List[EnvironmentalRecordSchema])
def read_environmental_records(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    records_service = RecordsService(db)
    return records_service.get_environmental_records(None, skip, limit)

@router.get("/fitness", response_model=List[FitnessRecordSchema])
def read_fitness_records(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    records_service = RecordsService(db)
    return records_service.get_fitness_records(None, skip, limit)

@router.get("/daily_summary")
def get_daily_summary(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    # Get population records
    records_service = RecordsService(db)
    h_records = records_service.get_health_records(None, 0, 5000)
    f_records = records_service.get_fitness_records(None, 0, 5000)
    e_records = records_service.get_environmental_records(None, 0, 5000)
    
    from datetime import date, timedelta
    today = date.today()
    yesterday = today - timedelta(days=1)
    d_7 = today - timedelta(days=7)
    d_30 = today - timedelta(days=30)
    
    def filter_by_date(lst, d):
        return [r for r in lst if getattr(r, 'record_date', None) == d]
        
    def filter_by_date_range(lst, start_d, end_d):
        return [r for r in lst if getattr(r, 'record_date', None) and start_d <= getattr(r, 'record_date') <= end_d]
        
    h_today, f_today, e_today = filter_by_date(h_records, today), filter_by_date(f_records, today), filter_by_date(e_records, today)
    h_yest, f_yest, e_yest = filter_by_date(h_records, yesterday), filter_by_date(f_records, yesterday), filter_by_date(e_records, yesterday)
    h_7d, f_7d, e_7d = filter_by_date_range(h_records, d_7, today), filter_by_date_range(f_records, d_7, today), filter_by_date_range(e_records, d_7, today)
    h_30d, f_30d, e_30d = filter_by_date_range(h_records, d_30, today), filter_by_date_range(f_records, d_30, today), filter_by_date_range(e_records, d_30, today)

    def avg(lst, key):
        if not lst: return 0
        valid = [getattr(x, key) for x in lst if getattr(x, key) is not None]
        return sum(valid) / len(valid) if valid else 0
        
    def latest(lst, key):
        if not lst: return 0
        for x in lst:
            if getattr(x, key) is not None:
                return getattr(x, key)
        return 0

    def extract_dynamic_metrics(lst, use_latest=False):
        ignore_keys = {'id', 'record_id', 'user_id', 'version_id', 'timestamp', 'created_at', 'updated_at', 'extra_data', 'steps', 'bmi', 'aqi', 'sleep_score', 'health_score', 'air_quality_index'}
        totals = {}
        counts = {}
        latest_vals = {}
        for rec in lst:
            if getattr(rec, 'extra_data', None):
                for k, v in rec.extra_data.items():
                    if k.lower() in ignore_keys:
                        continue
                    if isinstance(v, (int, float)):
                        totals[k] = totals.get(k, 0) + v
                        counts[k] = counts.get(k, 0) + 1
                        if k not in latest_vals:
                            latest_vals[k] = v
        if use_latest:
            return latest_vals
        return {k: round(totals[k]/counts[k], 2) for k in totals}

    return {
        "today": {
            "health_score": latest(h_today, "health_score"),
            "bmi": latest(h_today, "bmi"),
            "steps": latest(f_today, "steps"),
            "sleep_score": latest(f_today, "sleep_score"),
            "aqi": latest(e_today, "air_quality_index"),
            **extract_dynamic_metrics(h_today + f_today + e_today, use_latest=True)
        },
        "yesterday": {
            "health_score": avg(h_yest, "health_score"),
            "bmi": avg(h_yest, "bmi"),
            "steps": avg(f_yest, "steps"),
            "sleep_score": avg(f_yest, "sleep_score"),
            "aqi": avg(e_yest, "air_quality_index"),
            **extract_dynamic_metrics(h_yest + f_yest + e_yest)
        },
        "last_7_days": {
            "health_score": avg(h_7d, "health_score"),
            "bmi": avg(h_7d, "bmi"),
            "steps": avg(f_7d, "steps"),
            "sleep_score": avg(f_7d, "sleep_score"),
            "aqi": avg(e_7d, "air_quality_index"),
            **extract_dynamic_metrics(h_7d + f_7d + e_7d)
        },
        "last_30_days": {
            "health_score": avg(h_30d, "health_score"),
            "bmi": avg(h_30d, "bmi"),
            "steps": avg(f_30d, "steps"),
            "sleep_score": avg(f_30d, "sleep_score"),
            "aqi": avg(e_30d, "air_quality_index"),
            **extract_dynamic_metrics(h_30d + f_30d + e_30d)
        }
    }
