import os
import joblib
import pandas as pd
from typing import Dict, Any, Tuple
from sqlalchemy.orm import Session
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, IsolationForest
from xgboost import XGBClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
from sklearn.model_selection import train_test_split
from app.models.ml_models import MLModelVersion, PredictionLog

MODELS_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "trained_models")
os.makedirs(MODELS_DIR, exist_ok=True)

def train_classification_model(
    db: Session,
    model_type: str,
    model_name: str,
    df: pd.DataFrame,
    features: list,
    target: str,
    dataset_id: int,
    version: str,
    hyperparameters: Dict[str, Any] = None
) -> MLModelVersion:
    if hyperparameters is None:
        hyperparameters = {}
        
    X = df[features]
    y = df[target]
    
    # Handle categorical variables if needed (simple approach for now)
    X = pd.get_dummies(X)
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    if model_type == 'random_forest':
        clf = RandomForestClassifier(**hyperparameters, random_state=42)
    elif model_type == 'xgboost':
        clf = XGBClassifier(**hyperparameters, random_state=42)
    elif model_type == 'gradient_boosting':
        clf = GradientBoostingClassifier(**hyperparameters, random_state=42)
    else:
        raise ValueError(f"Unsupported model_type: {model_type}")
        
    clf.fit(X_train, y_train)
    y_pred = clf.predict(X_test)
    
    # Check if target is multiclass or binary for roc_auc
    metrics = {
        "accuracy": float(accuracy_score(y_test, y_pred)),
        "precision": float(precision_score(y_test, y_pred, average='macro', zero_division=0)),
        "recall": float(recall_score(y_test, y_pred, average='macro', zero_division=0)),
        "f1": float(f1_score(y_test, y_pred, average='macro', zero_division=0))
    }
    try:
        y_prob = clf.predict_proba(X_test)
        if y_prob.shape[1] == 2:
            metrics["roc_auc"] = float(roc_auc_score(y_test, y_prob[:, 1]))
        else:
            metrics["roc_auc"] = float(roc_auc_score(y_test, y_prob, multi_class='ovr'))
    except Exception:
        pass # roc_auc might not be applicable
        
    artifact_path = os.path.join(MODELS_DIR, f"{model_name}_{version}.joblib")
    joblib.dump(clf, artifact_path)
    
    # Save column names for inference
    joblib.dump(list(X.columns), artifact_path + ".cols")
    
    db_model = MLModelVersion(
        model_name=model_name,
        version=version,
        dataset_id=dataset_id,
        metrics=metrics,
        hyperparameters=hyperparameters,
        artifact_path=artifact_path,
        is_active=True
    )
    
    # Deactivate older versions
    old_models = db.query(MLModelVersion).filter(MLModelVersion.model_name == model_name).all()
    for om in old_models:
        om.is_active = False
        
    db.add(db_model)
    db.commit()
    db.refresh(db_model)
    
    return db_model

def train_anomaly_model(
    db: Session,
    model_name: str,
    df: pd.DataFrame,
    features: list,
    dataset_id: int,
    version: str,
    hyperparameters: Dict[str, Any] = None
) -> MLModelVersion:
    if hyperparameters is None:
        hyperparameters = {}
        
    X = df[features]
    X = pd.get_dummies(X)
    
    clf = IsolationForest(**hyperparameters, random_state=42)
    clf.fit(X)
    
    # For Isolation forest, we don't have standard precision/recall without labeled anomalies.
    metrics = {"status": "trained_unsupervised"}
    
    artifact_path = os.path.join(MODELS_DIR, f"{model_name}_{version}.joblib")
    joblib.dump(clf, artifact_path)
    joblib.dump(list(X.columns), artifact_path + ".cols")
    
    db_model = MLModelVersion(
        model_name=model_name,
        version=version,
        dataset_id=dataset_id,
        metrics=metrics,
        hyperparameters=hyperparameters,
        artifact_path=artifact_path,
        is_active=True
    )
    
    old_models = db.query(MLModelVersion).filter(MLModelVersion.model_name == model_name).all()
    for om in old_models:
        om.is_active = False
        
    db.add(db_model)
    db.commit()
    db.refresh(db_model)
    
    return db_model

def get_active_model(db: Session, model_name: str) -> Tuple[Any, list, MLModelVersion]:
    db_model = db.query(MLModelVersion).filter(
        MLModelVersion.model_name == model_name, 
        MLModelVersion.is_active == True
    ).first()
    
    if not db_model:
        raise ValueError(f"No active model found for {model_name}")
        
    clf = joblib.load(db_model.artifact_path)
    cols = joblib.load(db_model.artifact_path + ".cols")
    
    return clf, cols, db_model

def predict(db: Session, model_name: str, input_data: Dict[str, Any], user_id: int = None) -> Dict[str, Any]:
    import time
    start_time = time.time()
    
    clf, cols, db_model = get_active_model(db, model_name)
    
    df = pd.DataFrame([input_data])
    df = pd.get_dummies(df)
    
    # Align columns
    for col in cols:
        if col not in df.columns:
            df[col] = 0
    df = df[cols]
    
    prediction = clf.predict(df)[0]
    
    # Explanation (Basic feature importance based if available, or just fallback)
    explanation = "Based on the provided metrics."
    if hasattr(clf, 'feature_importances_'):
        importances = clf.feature_importances_
        top_indices = importances.argsort()[-3:][::-1]
        top_features = [cols[i] for i in top_indices]
        explanation = f"Top contributing factors: {', '.join(top_features)}."
        
    result = {"prediction": int(prediction) if isinstance(prediction, (int, float, bool, pd.Series, pd.DataFrame)) or hasattr(prediction, 'item') else str(prediction)}
    
    if hasattr(clf, 'predict_proba'):
        prob = clf.predict_proba(df)[0].max()
        result['confidence'] = float(prob)
        
    latency_ms = (time.time() - start_time) * 1000
    
    log = PredictionLog(
        model_id=db_model.id,
        user_id=user_id,
        prediction_type=model_name,
        input_data=input_data,
        prediction_result=result,
        explanation=explanation,
        latency_ms=latency_ms
    )
    db.add(log)
    db.commit()
    
    result['explanation'] = explanation
    return result
