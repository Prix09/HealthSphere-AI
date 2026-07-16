import pytest
import pandas as pd
from unittest.mock import MagicMock
from app.services import dataset_service, ml_service
from app.models.ml_models import MLModelVersion

def test_calculate_file_hash(tmp_path):
    d = tmp_path / "sub"
    d.mkdir()
    p = d / "hello.txt"
    p.write_text("content")
    
    hash_val = dataset_service.calculate_file_hash(str(p))
    assert isinstance(hash_val, str)
    assert len(hash_val) == 64 # sha256 length

def test_feature_engineering():
    health_data = {"User_ID": [1], "BMI": [25]}
    fitbit_data = {"User_ID": [1], "Daily_Steps": [10000], "Active_Minutes": [60]}
    air_data = {"User_ID": [1], "AQI": [50]}
    
    # We can mock read_csv
    with pytest.MonkeyPatch.context() as m:
        def mock_read_csv(filepath):
            if "health" in filepath: return pd.DataFrame(health_data)
            if "fitbit" in filepath: return pd.DataFrame(fitbit_data)
            if "air" in filepath: return pd.DataFrame(air_data)
            
        m.setattr(pd, "read_csv", mock_read_csv)
        
        paths = {"health": "health.csv", "fitbit": "fitbit.csv", "air": "air.csv"}
        df = dataset_service.load_and_engineer_features(paths)
        
        assert "Health_Score" in df.columns
        assert "Activity_Index" in df.columns
        assert "Lifestyle_Score" in df.columns
        assert "Environmental_Exposure_Index" in df.columns
        assert "Risk_Score" in df.columns
        assert df["Health_Score"].iloc[0] == 94.0 # 100 - abs(25-22)*2

def test_train_model():
    # Mock DB session
    db_mock = MagicMock()
    df = pd.DataFrame({
        "feature1": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        "feature2": [0, 1, 0, 1, 0, 1, 0, 1, 0, 1],
        "target": [0, 1, 0, 1, 0, 1, 0, 1, 0, 1]
    })
    
    model_version = ml_service.train_classification_model(
        db=db_mock,
        model_type="random_forest",
        model_name="test_model",
        df=df,
        features=["feature1", "feature2"],
        target="target",
        dataset_id=1,
        version="v1"
    )
    
    assert model_version is not None
    assert db_mock.add.called
    assert db_mock.commit.called
