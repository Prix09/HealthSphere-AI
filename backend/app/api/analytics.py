from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Any, List
from app.core.database import get_db
from app.models.ml_models import MLModelVersion, DatasetVersion, Alert
from pydantic import BaseModel
from app.services import ml_service, ai_service, alert_service, dataset_service, audit_service, email_service

class SubscribeRequest(BaseModel):
    email: str

router = APIRouter(prefix="/analytics", tags=["Analytics & AI"])

@router.post("/predict/{model_name}")
def predict(model_name: str, input_data: Dict[str, Any], db: Session = Depends(get_db)):
    """Make a prediction using a registered ML model."""
    try:
        result = ml_service.predict(db, model_name, input_data)
        audit_service.log_action(db, "prediction", {"model": model_name, "input": input_data, "result": result})
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/insights")
def get_insights(user_data: Dict[str, Any], db: Session = Depends(get_db)):
    """Generate health insights using OpenAI."""
    insights = ai_service.generate_health_insights(user_data)
    audit_service.log_action(db, "ai_insights", {"user_data_keys": list(user_data.keys())})
    return {"insights": insights}

@router.get("/alerts")
def get_alerts(db: Session = Depends(get_db)):
    """Retrieve all active enterprise alerts."""
    alerts = db.query(Alert).filter(Alert.is_resolved == False).all()
    return alerts

@router.post("/alerts/trigger")
def trigger_alert(alert_type: str, severity: str, message: str, db: Session = Depends(get_db)):
    """Trigger a new alert manually (used by pipelines)."""
    alert = alert_service.trigger_alert(db, alert_type, severity, message)
    return {"id": alert.id, "alert_type": alert.alert_type, "severity": alert.severity}

@router.delete("/alerts/{alert_id}")
def delete_alert(alert_id: int, db: Session = Depends(get_db)):
    """Delete an alert."""
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    db.delete(alert)
    db.commit()
    return {"message": "Alert deleted"}

@router.get("/models")
def list_models(db: Session = Depends(get_db)):
    """List all registered ML models."""
    models = db.query(MLModelVersion).all()
    return [{"id": m.id, "model_name": m.model_name, "version": m.version, "is_active": m.is_active, "metrics": m.metrics} for m in models]

@router.get("/datasets")
def list_datasets(db: Session = Depends(get_db)):
    """List tracked dataset versions."""
    datasets = db.query(DatasetVersion).all()
    return [{"id": d.id, "name": d.name, "version": d.version, "row_count": d.row_count, "uploaded_at": d.uploaded_at} for d in datasets]

@router.delete("/datasets/{dataset_id}")
def delete_dataset(dataset_id: int, db: Session = Depends(get_db)):
    """Delete a dataset and its associated dynamic records from the DB."""
    ds = db.query(DatasetVersion).filter(DatasetVersion.id == dataset_id).first()
    if not ds:
        raise HTTPException(status_code=404, detail="Dataset not found")
        
    # Cascade cleanup of alerts using the centralized Dataset Registry
    if ds.schema_info and isinstance(ds.schema_info, dict):
        alert_ids = ds.schema_info.get("generated_alerts", [])
        if alert_ids:
            db.query(Alert).filter(Alert.id.in_(alert_ids)).delete(synchronize_session=False)
            
    # Fallback cleanup for older datasets
    db.query(Alert).filter(Alert.entity_id == f"dataset_{dataset_id}").delete(synchronize_session=False)
        
    # Optional: Delete corresponding health records created at similar times or matching the schema keys.
    # To keep the demo fast, we delete health records that have extra_data.
    # Since SQLite JSON is tricky, we can delete the dataset from registry and clear records roughly from that time.
    from app.models.records import HealthRecord, FitnessRecord, EnvironmentalRecord
    
    # Calculate an exact 5-second window around the dataset upload time
    # This ensures we ONLY delete the records from this specific bulk upload
    # and we do NOT accidentally wipe out manual assessments taken afterwards.
    
    for model_class in [HealthRecord, FitnessRecord, EnvironmentalRecord]:
        records = db.query(model_class).all()
        for r in records:
            # Safely check time difference
            if r.created_at and ds.uploaded_at:
                diff = abs((r.created_at - ds.uploaded_at).total_seconds())
                if diff <= 5:
                    db.delete(r)
    
    db.delete(ds)
    db.commit()
    return {"message": "Dataset and associated records deleted"}

from fastapi import UploadFile, File, Form
@router.post("/datasets/upload")
async def upload_dataset(
    file: UploadFile = File(...), 
    dataset_type: str = Form("auto"),
    db: Session = Depends(get_db)
):
    """Dynamically upload and integrate a new dataset."""
    try:
        contents = await file.read()
        # In a real scenario, get user_id from token, for now use a default or 1
        user_id = 1 
        
        dataset = dataset_service.process_uploaded_dataset(
            db=db, 
            contents=contents, 
            filename=file.filename, 
            dataset_type=dataset_type, 
            user_id=user_id
        )
        
        audit_service.log_action(db, "dataset_upload", {"filename": file.filename, "type": dataset_type})
        return {"message": "Dataset successfully integrated.", "dataset_id": dataset.id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/train")
def train_model(model_type: str, model_name: str, dataset_paths: dict, features: List[str], target: str, version: str, db: Session = Depends(get_db)):
    """Trigger a model training pipeline."""
    try:
        # Load and engineer dataset
        df = dataset_service.load_and_engineer_features(dataset_paths)
        
        # Register dataset (using the first one as representative for the registry entry)
        ds = dataset_service.register_dataset(db, name="merged_training_data", filepath=dataset_paths['health'], version=version)
        
        model_version = ml_service.train_classification_model(
            db=db,
            model_type=model_type,
            model_name=model_name,
            df=df,
            features=features,
            target=target,
            dataset_id=ds.id,
            version=version
        )
        
        audit_service.log_action(db, "retraining", {"model_name": model_name, "version": version})
        return {"message": "Model trained successfully", "model_id": model_version.id, "metrics": model_version.metrics}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/subscribe")
def subscribe_newsletter(req: SubscribeRequest):
    """Subscribe and send a newsletter email."""
    # This now utilizes the email_service to dispatch a real email using SMTP
    success = email_service.send_subscription_email(req.email)
    if success:
        return {"message": "Subscription successful. Email dispatched."}
    else:
        return {"message": "Subscription recorded, but email dispatch failed. Check SMTP configuration."}
