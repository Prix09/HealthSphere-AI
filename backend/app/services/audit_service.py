from sqlalchemy.orm import Session
from app.models.ml_models import AuditLog
from typing import Any, Dict

def log_action(db: Session, action_type: str, details: Dict[str, Any], user_id: int = None, ip_address: str = None) -> AuditLog:
    """Logs critical actions into the audit_logs table."""
    audit_entry = AuditLog(
        action_type=action_type,
        user_id=user_id,
        details=details,
        ip_address=ip_address
    )
    db.add(audit_entry)
    db.commit()
    db.refresh(audit_entry)
    return audit_entry
