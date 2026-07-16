from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.ml_models import PredictionLog, MLModelVersion
from app.services.alert_service import trigger_alert
from typing import Dict, Any

def check_model_latency(db: Session, model_name: str) -> Dict[str, Any]:
    """Check average prediction latency for a model."""
    avg_latency = db.query(func.avg(PredictionLog.latency_ms)).join(MLModelVersion).filter(
        MLModelVersion.model_name == model_name
    ).scalar()
    
    return {"model_name": model_name, "avg_latency_ms": float(avg_latency) if avg_latency else 0.0}

def detect_model_drift(db: Session, model_name: str, threshold: float = 0.5) -> bool:
    """
    A basic drift detection mechanism.
    For demonstration, we could compare the distribution of recent predictions vs baseline.
    If a significant shift is detected, trigger an alert.
    """
    # Placeholder logic for drift detection:
    # If the variance of recent predictions is wildly different, we could trigger an alert.
    # We will just do a mock check.
    recent_preds = db.query(PredictionLog).join(MLModelVersion).filter(
        MLModelVersion.model_name == model_name
    ).order_by(PredictionLog.predicted_at.desc()).limit(100).all()
    
    if len(recent_preds) < 10:
        return False # Not enough data
        
    # Analyze result distribution
    # Here we mock it as False, but could be dynamic
    drift_detected = False
    
    # Just an example condition for drift triggering
    if drift_detected:
        trigger_alert(db, "model_drift", "high", f"Model drift detected in {model_name}")
        
    return drift_detected

def check_health_thresholds(db: Session, user_data: Dict[str, Any], user_id: int = None):
    """
    Evaluates incoming health metrics and triggers specific explanatory alerts if thresholds are breached.
    Alert throttling in alert_service prevents duplicate spam.
    """
    alerts_triggered = []
    
    # 1. AQI Alert
    aqi = user_data.get('aqi')
    if aqi is not None and int(aqi) > 150:
        msg = f"AQI Alert: Current AQI {aqi} exceeds healthy threshold of 150. Risk of respiratory inflammation."
        alert = trigger_alert(db, "high_aqi", "high", msg, user_id)
        if alert: alerts_triggered.append(alert)
        
    # 2. Sleep Alert
    sleep = user_data.get('sleep') or user_data.get('sleep_hours')
    if sleep is not None and float(sleep) < 5.0:
        msg = f"Poor Sleep Alert: {sleep} hours of sleep is below the 5.0h critical threshold. Risk of fatigue and cognitive strain."
        alert = trigger_alert(db, "poor_sleep", "medium", msg, user_id)
        if alert: alerts_triggered.append(alert)
        
    # 3. Activity Alert
    steps = user_data.get('steps')
    if steps is not None and int(steps) < 3000:
        msg = f"Low Activity Alert: {steps} steps is below the minimal 3000 baseline. High risk of cardiovascular stiffness."
        alert = trigger_alert(db, "low_activity", "medium", msg, user_id)
        if alert: alerts_triggered.append(alert)
        
    # 4. BMI Alert
    bmi = user_data.get('bmi')
    if bmi is not None and float(bmi) >= 30.0:
        msg = f"High BMI Alert: BMI of {bmi} indicates clinical obesity class I. Elevated metabolic risk."
        alert = trigger_alert(db, "high_bmi", "high", msg, user_id)
        if alert: alerts_triggered.append(alert)
        
    # 5. Risk Score Alert (e.g., from prediction output)
    risk_prediction = user_data.get('risk_prediction')
    if risk_prediction is not None and (str(risk_prediction) == 'High' or str(risk_prediction) == '1'):
        msg = "High Health Risk Alert: ML Model flagged an elevated composite risk based on recent vitals."
        alert = trigger_alert(db, "high_risk", "critical", msg, user_id)
        if alert: alerts_triggered.append(alert)
        
    # 6. Dynamic Metrics Check
    for col, val in user_data.items():
        if not isinstance(val, (int, float)):
            continue
        col_lower = col.lower()
        if col_lower in ['aqi', 'sleep', 'sleep_hours', 'steps', 'bmi', 'risk_prediction']:
            continue
            
        matched_registry = None
        for key, reg_data in METRIC_THRESHOLD_REGISTRY.items():
            if key in col_lower:
                matched_registry = reg_data
                break
                
        if matched_registry:
            threshold = matched_registry['threshold']
            is_higher_bad = matched_registry['type'] == 'higher_is_bad'
            name = matched_registry['name']
            
            breach = (is_higher_bad and val > threshold) or (not is_higher_bad and val < threshold)
            
            if breach:
                severity = matched_registry['severity']
                msg = f"Alert: {name} level of {val} breached the healthy threshold of {threshold}."
                alert = trigger_alert(db, f"manual_dynamic_{col_lower}", severity, msg, user_id)
                if alert: alerts_triggered.append(alert)
                
    return alerts_triggered

METRIC_THRESHOLD_REGISTRY = {
    'health_score': {'type': 'lower_is_bad', 'threshold': 70, 'severity': 'high', 'name': 'Health Score'},
    'sleep': {'type': 'lower_is_bad', 'threshold': 5.0, 'severity': 'medium', 'name': 'Sleep Hours'},
    'sleep_score': {'type': 'lower_is_bad', 'threshold': 60, 'severity': 'medium', 'name': 'Sleep Score'},
    'steps': {'type': 'lower_is_bad', 'threshold': 3000, 'severity': 'medium', 'name': 'Daily Steps'},
    'aqi': {'type': 'higher_is_bad', 'threshold': 150, 'severity': 'high', 'name': 'AQI'},
    'air_quality_index': {'type': 'higher_is_bad', 'threshold': 150, 'severity': 'high', 'name': 'AQI'},
    'bmi': {'type': 'higher_is_bad', 'threshold': 30.0, 'severity': 'high', 'name': 'BMI'},
    'stress': {'type': 'higher_is_bad', 'threshold': 80, 'severity': 'high', 'name': 'Stress Level'},
    'heart_rate': {'type': 'higher_is_bad', 'threshold': 100, 'severity': 'high', 'name': 'Resting Heart Rate'},
    'anxiety': {'type': 'higher_is_bad', 'threshold': 80, 'severity': 'high', 'name': 'Anxiety Score'},
    'sugar': {'type': 'higher_is_bad', 'threshold': 140, 'severity': 'high', 'name': 'Blood Sugar'},
    'calories': {'type': 'higher_is_bad', 'threshold': 3000, 'severity': 'medium', 'name': 'Caloric Intake'},
    'protein': {'type': 'lower_is_bad', 'threshold': 40, 'severity': 'medium', 'name': 'Protein Intake'},
    'spo2': {'type': 'lower_is_bad', 'threshold': 92, 'severity': 'critical', 'name': 'SpO2 Level'},
    'mood': {'type': 'lower_is_bad', 'threshold': 40, 'severity': 'medium', 'name': 'Mood Score'},
    'mental_wellness': {'type': 'lower_is_bad', 'threshold': 50, 'severity': 'high', 'name': 'Mental Wellness Score'}
}

def generate_dynamic_alerts_from_dataset(db: Session, dataset_id: int, df):
    alerts_triggered = []
    # Identify numeric columns
    numeric_cols = df.select_dtypes(include=['number']).columns
    entity_id = f"dataset_{dataset_id}"
    
    for col in numeric_cols:
        col_lower = col.lower()
        
        # Check against registry
        matched_registry = None
        for key, reg_data in METRIC_THRESHOLD_REGISTRY.items():
            if key in col_lower:
                matched_registry = reg_data
                break
                
        if matched_registry:
            # Use registry rules
            threshold = matched_registry['threshold']
            is_higher_bad = matched_registry['type'] == 'higher_is_bad'
            name = matched_registry['name']
            
            if is_higher_bad:
                breaches = df[df[col] > threshold]
            else:
                breaches = df[df[col] < threshold]
                
            if not breaches.empty:
                mean_breach = breaches[col].mean()
                severity = matched_registry['severity']
                msg = f"Dataset uploaded with alarming {name} levels. Average anomalous value is {mean_breach:.2f} (Threshold: {threshold})."
                alert = trigger_alert(db, f"dynamic_{col_lower}_alert", severity, msg, entity_id=entity_id)
                if alert: alerts_triggered.append(alert)
        else:
            # Unknown metric -> Use statistical anomaly
            mean_val = df[col].mean()
            std_val = df[col].std()
            if std_val > 0:
                max_val = df[col].max()
                min_val = df[col].min()
                z_max = (max_val - mean_val) / std_val
                z_min = (mean_val - min_val) / std_val
                
                if z_max > 3:
                    msg = f"Statistical Anomaly Detected: {col} reached a high of {max_val:.2f} (Mean: {mean_val:.2f})."
                    alert = trigger_alert(db, f"dynamic_{col_lower}_high", "medium", msg, entity_id=entity_id)
                    if alert: alerts_triggered.append(alert)
                elif z_min > 3:
                    msg = f"Statistical Anomaly Detected: {col} reached a low of {min_val:.2f} (Mean: {mean_val:.2f})."
                    alert = trigger_alert(db, f"dynamic_{col_lower}_low", "medium", msg, entity_id=entity_id)
                    if alert: alerts_triggered.append(alert)

    return alerts_triggered
