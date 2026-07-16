import os
import sys
import pandas as pd
import joblib
from sqlalchemy.orm import Session
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
from sklearn.model_selection import train_test_split

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from backend.app.core.database import SessionLocal
from backend.app.models.ml_models import MLModelVersion
from backend.app.services.dataset_service import load_and_engineer_features
from backend.app.services.ml_service import train_classification_model

ACCEPTABLE_ACCURACY = 0.80

def evaluate_model(clf, cols, df, target):
    X = df[cols]
    y = df[target]
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    y_pred = clf.predict(X_test)
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
        pass
    return metrics

def run_validation():
    db = SessionLocal()
    print("Fetching active models...")
    models = db.query(MLModelVersion).filter(MLModelVersion.is_active == True).all()
    
    if not models:
        print("No active models found in registry. Will need to train.")
    
    # Load dataset to evaluate
    try:
        print("Loading test data...")
        dataset_paths = {
            "health": "../data_engineering/mock_data/health_indicators.csv",
            "environmental": "../data_engineering/mock_data/air_quality.csv",
            "fitness": "../data_engineering/mock_data/fitness_activity.csv"
        }
        df = load_and_engineer_features(dataset_paths)
        df = pd.get_dummies(df)
        target = 'Diabetes_Risk_High' # Example target mapped in dataset_service
    except Exception as e:
        print(f"Warning: Could not load dataset for evaluation: {e}")
        return

    for db_model in models:
        print(f"\n--- Validating Model: {db_model.model_name} v{db_model.version} ---")
        needs_retraining = False
        
        # 1. Model file missing
        if not os.path.exists(db_model.artifact_path):
            print(f"✗ Model file missing: {db_model.artifact_path}")
            needs_retraining = True
        
        # 2. Model corrupted
        clf = None
        cols = None
        if not needs_retraining:
            try:
                clf = joblib.load(db_model.artifact_path)
                cols = joblib.load(db_model.artifact_path + ".cols")
                print("✓ Model file loaded successfully.")
            except Exception as e:
                print(f"✗ Model file corrupted: {e}")
                needs_retraining = True
        
        # 3. Evaluate Metrics
        if not needs_retraining:
            try:
                # Align columns
                for col in cols:
                    if col not in df.columns:
                        df[col] = 0
                
                calculated_metrics = evaluate_model(clf, cols, df, target)
                db_metrics = db_model.metrics
                
                print(f"Calculated Metrics: {calculated_metrics}")
                print(f"Stored Metrics: {db_metrics}")
                
                # Compare accuracy
                if calculated_metrics['accuracy'] < ACCEPTABLE_ACCURACY:
                    print(f"✗ Accuracy ({calculated_metrics['accuracy']}) below acceptable threshold ({ACCEPTABLE_ACCURACY}).")
                    needs_retraining = True
                else:
                    # Update stored metrics to actual ones if they were placeholders
                    db_model.metrics = calculated_metrics
                    db.commit()
                    print("✓ Metrics verified and updated in database.")
            except Exception as e:
                print(f"✗ Could not reproduce metrics. Error: {e}")
                needs_retraining = True
                
        if needs_retraining:
            print(">>> Initiating Retraining Sequence...")
            try:
                print(f"Retraining {db_model.model_name}...")
                new_model = train_classification_model(
                    db=db,
                    model_type='random_forest',
                    model_name=db_model.model_name,
                    df=df,
                    features=cols if cols else [c for c in df.columns if c != target],
                    target=target,
                    dataset_id=db_model.dataset_id,
                    version=f"{db_model.version}_retrained"
                )
                print(f"✓ Model retrained successfully as v{new_model.version}")
            except Exception as e:
                print(f"Failed to retrain: {e}")
        else:
            print(f"Model {db_model.model_name} passed all validation checks.")

if __name__ == "__main__":
    run_validation()
