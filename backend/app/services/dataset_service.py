import pandas as pd
import hashlib
from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.ml_models import DatasetVersion
import os

def calculate_file_hash(filepath: str) -> str:
    hasher = hashlib.sha256()
    with open(filepath, 'rb') as f:
        buf = f.read()
        hasher.update(buf)
    return hasher.hexdigest()

def register_dataset(db: Session, name: str, filepath: str, version: str, description: str = "", user_id: int = None) -> DatasetVersion:
    """Register a new dataset version in the database if it doesn't exist."""
    file_hash = calculate_file_hash(filepath)
    
    # Check if dataset version already exists based on hash
    existing = db.query(DatasetVersion).filter(DatasetVersion.file_hash == file_hash).first()
    if existing:
        return existing
        
    df = pd.read_csv(filepath)
    schema_info = {col: str(dtype) for col, dtype in df.dtypes.items()}
    
    db_dataset = DatasetVersion(
        name=name,
        version=version,
        file_hash=file_hash,
        row_count=len(df),
        schema_info=schema_info,
        uploaded_by=user_id,
        description=description
    )
    db.add(db_dataset)
    db.commit()
    db.refresh(db_dataset)
    return db_dataset

def load_and_engineer_features(filepaths: dict) -> pd.DataFrame:
    """Load the raw datasets and engineer features as specified."""
    # Assuming filepaths dictionary has keys: 'health', 'fitbit', 'air'
    health_df = pd.read_csv(filepaths['health'])
    fitbit_df = pd.read_csv(filepaths['fitbit'])
    air_df = pd.read_csv(filepaths['air'])
    
    # Merge datasets on User_ID if present, or assume they are aligned by index for simplicity if no common key
    # In HealthSphere Phase 1, there's usually a User_ID. 
    # Let's ensure User_ID is present or use index.
    
    # If User_ID exists, merge on it. Else, concat horizontally.
    if 'User_ID' in health_df.columns and 'User_ID' in fitbit_df.columns:
        df = pd.merge(health_df, fitbit_df, on='User_ID', how='inner')
    else:
        df = pd.concat([health_df, fitbit_df], axis=1)
        
    if 'User_ID' in df.columns and 'User_ID' in air_df.columns:
        df = pd.merge(df, air_df, on='User_ID', how='inner')
    else:
        df = pd.concat([df, air_df], axis=1)
        
    # Feature Engineering
    # 1. Health Score
    if 'BMI' in df.columns:
        # Example logic: Normalize BMI (ideal ~22), Blood Pressure, etc.
        df['Health_Score'] = 100 - abs(df['BMI'] - 22) * 2
    else:
        df['Health_Score'] = 80
        
    # 2. Activity Index
    if 'Daily_Steps' in df.columns and 'Active_Minutes' in df.columns:
        df['Activity_Index'] = (df['Daily_Steps'] / 10000) * 50 + (df['Active_Minutes'] / 60) * 50
    else:
        df['Activity_Index'] = 50
        
    # 3. Sleep Score
    if 'Sleep_Duration' in df.columns:
        df['Sleep_Score'] = 100 - abs(df['Sleep_Duration'] - 8) * 10
    else:
        df['Sleep_Score'] = 75
        
    # 4. Lifestyle Score
    df['Lifestyle_Score'] = (df['Activity_Index'] + df['Sleep_Score']) / 2
    
    # 5. Environmental Exposure Index
    if 'AQI' in df.columns:
        df['Environmental_Exposure_Index'] = df['AQI'] / 500 * 100
    else:
        df['Environmental_Exposure_Index'] = 50
        
    # 6. Risk Score (Target for some models, or inverse of Health Score)
    df['Risk_Score'] = 100 - df['Health_Score'] + (df['Environmental_Exposure_Index'] * 0.1)
    
    # Ensure all required features are present based on user comments
    # Health Indicators: Age, Gender, BMI, Blood_Pressure, Blood_Sugar, HbA1c, Family_History
    # Fitbit: Daily_Steps, Calories_Burned, Sleep_Duration, Active_Minutes, Exercise_Frequency
    # Air: AQI, Temperature, Humidity
    
    # We will let the specific ML models pick the features they need.
    return df

import json
from datetime import datetime
from app.models.records import HealthRecord, FitnessRecord, EnvironmentalRecord
import io

def process_uploaded_dataset(db: Session, contents: bytes, filename: str, dataset_type: str, user_id: int):
    # 1. Read CSV
    try:
        df = pd.read_csv(io.BytesIO(contents))
    except Exception as e:
        raise ValueError(f"Failed to read CSV: {e}")
        
    # Drop full duplicates
    df = df.drop_duplicates()
    
    # 2. Schema mapping
    if dataset_type == "health":
        model_cls = HealthRecord
    elif dataset_type == "fitness":
        model_cls = FitnessRecord
    elif dataset_type == "environmental":
        model_cls = EnvironmentalRecord
    else:
        # Auto-detect based on common columns if possible, default to health
        if 'AQI' in df.columns or 'Temperature' in df.columns:
            model_cls = EnvironmentalRecord
        elif 'Steps' in df.columns or 'Daily_Steps' in df.columns:
            model_cls = FitnessRecord
        else:
            model_cls = HealthRecord

    known_columns = model_cls.__table__.columns.keys()
    records_to_insert = []
    
    # Auto-provision missing users to prevent ForeignKeyViolation
    csv_user_ids = []
    if 'User_ID' in df.columns:
        csv_user_ids = df['User_ID'].dropna().unique().tolist()
    elif 'user_id' in df.columns:
        csv_user_ids = df['user_id'].dropna().unique().tolist()
        
    if csv_user_ids:
        from app.models.user import User
        existing_users = db.query(User.id).filter(User.id.in_(csv_user_ids)).all()
        existing_user_ids = {u[0] for u in existing_users}
        missing_user_ids = set(csv_user_ids) - existing_user_ids
        
        if missing_user_ids:
            new_users = []
            for uid in missing_user_ids:
                new_users.append(User(
                    id=int(uid),
                    email=f"auto_user_{int(uid)}@healthsphere.local",
                    hashed_password="dummy",
                    full_name=f"Auto User {int(uid)}",
                    is_active=True
                ))
            db.bulk_save_objects(new_users)
            db.commit()
    
    # Iterate records
    for _, row in df.iterrows():
        row_dict = row.to_dict()
        record_kwargs = {}
        extra_data = {}
        
        # Standardize User_ID and Date if possible
        if 'User_ID' in row_dict:
            record_kwargs['user_id'] = int(row_dict.pop('User_ID'))
        elif 'user_id' in row_dict:
            record_kwargs['user_id'] = int(row_dict.pop('user_id'))
        else:
            record_kwargs['user_id'] = user_id or 1 # Fallback
            
        raw_date = row_dict.pop('Date', None) or row_dict.pop('record_date', None)
        if raw_date is not None:
            try:
                record_kwargs['record_date'] = pd.to_datetime(raw_date).date()
            except Exception:
                record_kwargs['record_date'] = datetime.utcnow().date()
        else:
            record_kwargs['record_date'] = datetime.utcnow().date()
            
        for col, val in row_dict.items():
            if pd.isna(val):
                val = None
            else:
                if hasattr(val, 'item'):
                    val = val.item()
                if hasattr(val, 'isoformat'):  # Catch Timestamp/datetime
                    val = val.isoformat()
            
            norm_col = col.lower()
            if norm_col in known_columns:
                record_kwargs[norm_col] = val
            else:
                extra_data[col] = val
                
        record_kwargs['extra_data'] = extra_data
        records_to_insert.append(model_cls(**record_kwargs))
        
    db.bulk_save_objects(records_to_insert)
    
    # 3. Register Dataset
    schema_info = {col: str(dtype) for col, dtype in df.dtypes.items()}
    file_hash = hashlib.sha256(contents).hexdigest()
    
    db_dataset = DatasetVersion(
        name=filename,
        version=datetime.now().strftime("%Y%m%d%H%M%S"),
        file_hash=file_hash,
        row_count=len(df),
        schema_info=schema_info,
        uploaded_by=user_id,
        description=f"Dynamically uploaded {dataset_type} dataset"
    )
    db.add(db_dataset)
    from app.services.monitoring import generate_dynamic_alerts_from_dataset
    alert_ids = []
    try:
        alerts = generate_dynamic_alerts_from_dataset(db, db_dataset.id, df)
        alert_ids = [a.id for a in alerts if a.id]
    except Exception as e:
        print(f"Failed to generate dynamic alerts: {e}")
        
    registry_data = {
        "schema": schema_info,
        "metric_types": list(df.select_dtypes(include=['number']).columns),
        "generated_alerts": alert_ids,
        "generated_charts": list(df.select_dtypes(include=['number']).columns)
    }
    db_dataset.schema_info = registry_data
    db.commit()
    
    return db_dataset
