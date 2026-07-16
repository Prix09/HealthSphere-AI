from sqlalchemy.orm import Session
from app.models.ml_models import Alert
from datetime import datetime, timedelta, timezone

# Throttling config (e.g., prevent duplicate alerts within X hours)
ALERT_THROTTLE_HOURS = 0

def trigger_alert(db: Session, alert_type: str, severity: str, message: str, user_id: int = None, entity_id: str = None) -> Alert:
    """
    Triggers an enterprise alert, applying throttling to prevent duplicates.
    Duplicate defined as: Same alert_type and user_id/entity_id within ALERT_THROTTLE_HOURS.
    """
    throttle_threshold = datetime.now(timezone.utc) - timedelta(hours=ALERT_THROTTLE_HOURS)
    
    # Check for recent duplicate
    query = db.query(Alert).filter(
        Alert.alert_type == alert_type,
        Alert.created_at >= throttle_threshold
    )
    
    if user_id:
        query = query.filter(Alert.user_id == user_id)
    if entity_id:
        query = query.filter(Alert.entity_id == entity_id)
        
    recent_alert = query.first()
    
    if recent_alert:
        # Throttled, do not create duplicate
        return recent_alert
        
    from app.services import ai_service
    try:
        recommendation = ai_service.generate_alert_recommendation(alert_type, severity, message)
        enhanced_message = f"{message}<br/><br/><hr/><br/>{recommendation}"
    except Exception as e:
        print("Failed to generate AI recommendation:", e)
        enhanced_message = message
        
    # Create new alert
    new_alert = Alert(
        alert_type=alert_type,
        severity=severity,
        message=enhanced_message,
        user_id=user_id,
        entity_id=entity_id
    )
    
    db.add(new_alert)
    db.commit()
    db.refresh(new_alert)
    return new_alert

def resolve_alert(db: Session, alert_id: int) -> Alert:
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if alert and not alert.is_resolved:
        alert.is_resolved = True
        alert.resolved_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(alert)
    return alert
