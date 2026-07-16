from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any
from app.api import deps
from app.services import ml_service, ai_service

router = APIRouter()

@router.post("/generate")
def generate_assessment(
    payload: dict,
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_user)
):
    try:
        # Extract fields
        age = payload.get("age", 30)
        weight_kg = payload.get("weight_kg", 70)
        height_cm = payload.get("height_cm", 170)
        sleep_hours = payload.get("sleep_hours", 7.0)
        daily_steps = payload.get("daily_steps", 5000)
        systolic_bp = payload.get("systolic_bp", 120)
        diastolic_bp = payload.get("diastolic_bp", 80)
        fasting_blood_sugar = payload.get("fasting_blood_sugar", 90)
        hba1c = payload.get("hba1c", 5.5)
        aqi = payload.get("aqi", 50)
        daily_calories = payload.get("daily_calories", 2000)

        # 1. Calculate Derived Metrics (BMI)
        height_m = height_cm / 100.0
        bmi = weight_kg / (height_m * height_m) if height_m > 0 else 0
        bmi = round(bmi, 2)

        # Build feature dict for ML model
        input_data = {
            "Age": age,
            "Height_cm": height_cm,
            "Weight_kg": weight_kg,
            "BMI": bmi,
            "Sleep_Hours": sleep_hours,
            "Systolic_BP": systolic_bp,
            "Diastolic_BP": diastolic_bp,
            "Fasting_Blood_Sugar": fasting_blood_sugar,
            "HbA1c": hba1c,
            "Daily_Calories": daily_calories
        }

        # Run prediction
        try:
            prediction_result = ml_service.predict(db, "test_model_v1", payload)
        except Exception as e:
            prediction_result = {"prediction": 1, "confidence": 0.85, "explanation": "Fallback due to missing model."}
        
        # Trigger Alerts based on thresholds
        from app.services.monitoring import check_health_thresholds
        payload_with_risk = {
            **payload, 
            "risk_prediction": prediction_result["prediction"],
            "bmi": bmi,
            "steps": daily_steps
        }
        alerts_triggered = check_health_thresholds(db, payload_with_risk, user_id=current_user.id)
        
        # Extract alert data before db.commit to prevent DetachedInstanceError
        alerts_data = [{"alert_type": a.alert_type, "severity": a.severity, "message": a.message} for a in alerts_triggered]
        
        # 3. Save to DB so it populates the Dashboard's daily summaries
        from datetime import date
        from app.models.records import HealthRecord, FitnessRecord, EnvironmentalRecord
        
        today = date.today()
        
        # Safely parse risk prediction to a float
        try:
            risk_val = float(prediction_result["prediction"])
        except (ValueError, TypeError):
            risk_val = 1.0 if str(prediction_result["prediction"]).lower() == 'high' else 0.0
            
        known_keys = {"age", "weight_kg", "height_cm", "sleep_hours", "daily_steps", "systolic_bp", "diastolic_bp", "fasting_blood_sugar", "hba1c", "aqi", "daily_calories", "gender", "exercise_frequency"}
        dynamic_extra = {k: v for k, v in payload.items() if k not in known_keys and isinstance(v, (int, float))}
        
        health_record = HealthRecord(
            user_id=current_user.id,
            record_date=today,
            health_score=85.0 if risk_val == 0.0 else 60.0,
            bmi=bmi,
            risk_index=risk_val,
            extra_data=dynamic_extra
        )
        fitness_record = FitnessRecord(
            user_id=current_user.id,
            record_date=today,
            steps=daily_steps,
            activity_index=daily_steps / 100.0,
            sleep_score=sleep_hours * 10
        )
        env_record = EnvironmentalRecord(
            user_id=current_user.id,
            record_date=today,
            air_quality_index=aqi,
            exposure_index=aqi / 10.0
        )
        db.add(health_record)
        db.add(fitness_record)
        db.add(env_record)
        db.commit()

        context = {
            "User Profile": f"Age {age}, BMI {bmi}, Sleep {sleep_hours}h, Steps {daily_steps}",
            "Clinical": f"BP {systolic_bp}/{diastolic_bp}, Sugar {fasting_blood_sugar}, HbA1c {hba1c}",
            "Environment": f"AQI {aqi}",
            "Model Output": str(prediction_result)
        }
        if dynamic_extra:
            context["Dynamic Metrics"] = ", ".join([f"{k}: {v}" for k, v in dynamic_extra.items()])
        
        # Fetch simple historical trend for context
        try:
            from app.services.records_service import RecordsService
            past_records = RecordsService(db).get_health_records(current_user.id, 0, 14)
            if len(past_records) > 1:
                past_bmis = [r.bmi for r in past_records[1:] if r.bmi]
                if past_bmis:
                    avg_past_bmi = sum(past_bmis) / len(past_bmis)
                    bmi_delta = ((bmi - avg_past_bmi) / avg_past_bmi) * 100
                    context["Historical Trend"] = f"BMI changed by {bmi_delta:.1f}% over the last 14 records. Incorporate this trend dynamically."
        except Exception as e:
            print("Could not calculate historical trend", e)
        
        ai_insight = ai_service.generate_insight(
            insight_type="Manual Health Assessment",
            context=context,
            user_id=current_user.id
        )

        return {
            "derived_metrics": {"bmi": bmi},
            "prediction": prediction_result,
            "insight": ai_insight,
            "alerts": alerts_data
        }

    except Exception as e:
        import traceback
        with open("error.log", "w") as f:
            f.write(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))
