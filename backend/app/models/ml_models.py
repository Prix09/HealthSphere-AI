from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.base import Base

class DatasetVersion(Base):
    __tablename__ = "dataset_versions"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    version = Column(String, nullable=False)
    file_hash = Column(String, nullable=False)
    row_count = Column(Integer)
    schema_info = Column(JSON) # Store column names/types
    uploaded_by = Column(Integer, ForeignKey("users.id"))
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
    description = Column(String)

    models = relationship("MLModelVersion", back_populates="dataset")

class MLModelVersion(Base):
    __tablename__ = "ml_model_versions"

    id = Column(Integer, primary_key=True, index=True)
    model_name = Column(String, index=True, nullable=False) # e.g., 'random_forest_diabetes'
    version = Column(String, nullable=False)
    dataset_id = Column(Integer, ForeignKey("dataset_versions.id"))
    metrics = Column(JSON) # e.g., {"accuracy": 0.95, "f1": 0.93}
    hyperparameters = Column(JSON)
    artifact_path = Column(String, nullable=False) # Path to the .joblib file
    is_active = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    dataset = relationship("DatasetVersion", back_populates="models")
    predictions = relationship("PredictionLog", back_populates="model")

class PredictionLog(Base):
    __tablename__ = "prediction_logs"

    id = Column(Integer, primary_key=True, index=True)
    model_id = Column(Integer, ForeignKey("ml_model_versions.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    prediction_type = Column(String, index=True) # e.g., 'diabetes_risk'
    input_data = Column(JSON)
    prediction_result = Column(JSON)
    explanation = Column(String)
    predicted_at = Column(DateTime(timezone=True), server_default=func.now())
    latency_ms = Column(Float)

    model = relationship("MLModelVersion", back_populates="predictions")
    user = relationship("User")

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    action_type = Column(String, index=True, nullable=False) # e.g., 'prediction', 'retraining', 'auth', 'api_request'
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    details = Column(JSON)
    ip_address = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    alert_type = Column(String, index=True, nullable=False) # e.g., 'health_risk', 'model_drift'
    severity = Column(String, nullable=False) # 'low', 'medium', 'high', 'critical'
    message = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    entity_id = Column(String, nullable=True) # Reference to related entity if applicable
    is_resolved = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    resolved_at = Column(DateTime(timezone=True), nullable=True)
