import pytest
from app.services import ai_service
from unittest.mock import patch

def test_generate_health_insights():
    # Mock the OpenAI client
    with patch("app.services.ai_service._generate_text") as mock_generate:
        mock_generate.return_value = "Mocked health insight."
        
        result = ai_service.generate_health_insights({"age": 30, "bmi": 25})
        assert result == "Mocked health insight."
        mock_generate.assert_called_once()

def test_generate_prediction_explanation():
    with patch("app.services.ai_service._generate_text") as mock_generate:
        mock_generate.return_value = "Mocked explanation."
        
        result = ai_service.generate_prediction_explanation("Diabetes Risk", "High", {"bmi": 30})
        assert result == "Mocked explanation."
        mock_generate.assert_called_once()
