import os
from typing import Dict, Any, List
from openai import OpenAI
from app.core.config import settings

# Initialize the OpenAI client
# It will automatically pick up OPENAI_API_KEY from environment, or we pass it explicitly.
client = OpenAI(api_key=settings.OPENAI_API_KEY)
MODEL_NAME = "gpt-4o-mini"

def _generate_text(prompt: str, system_message: str = "You are a highly skilled AI Health Assistant.") -> str:
    """Helper method to generate text from OpenAI API."""
    try:
        # Strictly bypass AI for Dashboard Daily Insights as requested by user
        if any(p in prompt for p in ["'period': 'today'", "'period': 'yesterday'", "'period': 'last_7_days'", "'period': 'last_30_days'"]):
            raise ValueError("Bypass AI for deterministic dashboard logic")
            
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500,
            temperature=0.7
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        # Helper for deterministic rule-based insights
        def _get_deterministic_insight(bmi, sleep, aqi, steps, prefix_status="Based on your parameters"):
            risk = "High" if (bmi >= 25 or sleep < 6 or aqi > 100 or steps < 4000) else "Low"
            
            # Precise "Why It Is Happening"
            why = []
            if bmi >= 25: why.append("- <b>Excess Body Weight:</b> A BMI above 25 places continuous mechanical stress on joints and forces the heart to work harder to pump blood, increasing resting heart rate.")
            if sleep < 6: why.append("- <b>Sleep Deprivation:</b> Less than 6 hours of sleep prevents the body from completing essential metabolic repair cycles and elevates cortisol (stress hormone) levels.")
            if steps < 4000: why.append("- <b>Sedentary Lifestyle:</b> Low daily steps (<4000) lead to poor blood circulation, insulin resistance, and muscle atrophy.")
            if aqi > 100: why.append("- <b>High Pollution Exposure:</b> An AQI over 100 means fine particulate matter (PM2.5) is entering your lungs and bloodstream, triggering systemic inflammation.")
            if not why: why.append("Your metrics are generally within healthy clinical ranges.")
            why_str = "<br/>".join(why)
            
            # Precise "Future Risk" (Diseases)
            future = []
            if bmi >= 25: future.append("<b>Type 2 Diabetes</b>, <b>Hypertension</b>, and <b>Osteoarthritis</b>")
            if sleep < 6: future.append("<b>Chronic Fatigue Syndrome</b>, <b>Cognitive Decline</b>, and <b>Weakened Immunity</b>")
            if steps < 4000: future.append("<b>Coronary Artery Disease</b> and <b>Metabolic Syndrome</b>")
            if aqi > 100: future.append("<b>Asthma Exacerbation</b>, <b>COPD</b>, and <b>Arrhythmia</b>")
            if not future: 
                future_str = "You have <b>no significant immediate risk</b> of chronic lifestyle diseases if you maintain this baseline."
            else:
                future_str = f"If current trends continue without intervention, you are at an elevated risk of developing: {', '.join(future)}."
            
            # Precise "Things to NOT do" & Recommendations
            not_do = []
            actions = []
            if bmi >= 25: 
                not_do.append("- <b>DO NOT</b> consume high-glycemic processed sugars and late-night heavy meals.")
                actions.append("- <b>DO</b> incorporate a caloric deficit and 30 minutes of moderate aerobic exercise daily.")
            if sleep < 6: 
                not_do.append("- <b>DO NOT</b> consume caffeine after 3 PM or use blue-light emitting screens 1 hour before bed.")
                actions.append("- <b>DO</b> maintain a strict sleep schedule aiming for at least 7.5 uninterrupted hours.")
            if steps < 4000: 
                not_do.append("- <b>DO NOT</b> sit continuously for more than 60 minutes without standing or stretching.")
                actions.append("- <b>DO</b> set hourly alarms to walk for 5 minutes, aiming for a minimum of 7,000 steps/day.")
            if aqi > 100: 
                not_do.append("- <b>DO NOT</b> perform strenuous outdoor cardiovascular exercises (like running) during peak pollution hours.")
                actions.append("- <b>DO</b> use indoor HEPA air purifiers and wear an N95 mask if you must go outside.")

            # Check dynamic metrics from prompt context
            from app.services.monitoring import METRIC_THRESHOLD_REGISTRY
            import re
            for key, reg_data in METRIC_THRESHOLD_REGISTRY.items():
                if key in ['bmi', 'sleep', 'sleep_score', 'aqi', 'air_quality_index', 'steps']:
                    continue
                # Look for 'key: value' or 'key value' or "'key': value" in the prompt
                match = re.search(rf"['\"]?{key}['\"]?\s*[:=]?\s*([\d\.]+)", prompt, re.IGNORECASE)
                if match:
                    try:
                        val = float(match.group(1))
                        threshold = reg_data['threshold']
                        is_higher_bad = reg_data['type'] == 'higher_is_bad'
                        name = reg_data['name']
                        breach = (is_higher_bad and val > threshold) or (not is_higher_bad and val < threshold)
                        if breach:
                            risk = "High"
                            why.append(f"- <b>Abnormal {name}:</b> Level of {val} breaches the healthy threshold of {threshold}.")
                            actions.append(f"- <b>DO</b> monitor your {name} closely and consult a professional if it persists.")
                            future.append(f"<b>Complications related to abnormal {name}</b>")
                    except Exception:
                        pass
            
            if risk == "Low":
                not_do.append("- <b>DO NOT</b> drastically alter your current routine, as it is working well.")
                actions.append("- <b>DO</b> maintain your balanced diet and consistent activity levels.")

            not_do_str = "<br/>".join(not_do) if not_do else "None"
            actions_str = "<br/>".join(actions)

            return (
                f"<b>Current Status:</b><br/>{prefix_status} (BMI: {bmi:.2f}, Sleep: {sleep:.1f}h, Steps: {steps}, AQI: {aqi}), "
                f"your current health risk is estimated as <b>{risk}</b>.<br/><br/>"
                f"<b>Why It Is Happening:</b><br/>{why_str}<br/><br/>"
                f"<b>Future Risk Projections:</b><br/>{future_str}<br/><br/>"
                f"<b>Things to AVOID:</b><br/>{not_do_str}<br/><br/>"
                f"<b>Recommended Actions:</b><br/>{actions_str}"
            )

        # Dynamic Fallback Logic
        import re
        if "Manual Health Assessment" in prompt:
            try:
                bmi_match = re.search(r"BMI\s([\d\.]+)", prompt)
                bmi = float(bmi_match.group(1)) if bmi_match else 25.0
                
                sleep_match = re.search(r"Sleep\s([\d\.]+)h", prompt)
                sleep = float(sleep_match.group(1)) if sleep_match else 7.0
                
                aqi_match = re.search(r"AQI\s(\d+)", prompt)
                aqi = int(aqi_match.group(1)) if aqi_match else 50
                
                steps_match = re.search(r"Steps\s(\d+)", prompt)
                steps = int(steps_match.group(1)) if steps_match else 5000
                
                return _get_deterministic_insight(bmi, sleep, aqi, steps, prefix_status="Based on your manually entered parameters")
            except Exception:
                pass
                
        # Dashboard Daily Insights parsing
        try:
            bmi_match = re.search(r"'bmi':\s*([\d\.]+)", prompt)
            bmi = float(bmi_match.group(1)) if bmi_match else 25.0
            
            sleep_match = re.search(r"'sleep_score':\s*([\d\.]+)", prompt)
            sleep = float(sleep_match.group(1)) / 10.0 if sleep_match else 7.0
            
            aqi_match = re.search(r"'aqi':\s*([\d\.]+)", prompt)
            aqi = int(float(aqi_match.group(1))) if aqi_match else 50
            
            steps_match = re.search(r"'steps':\s*([\d\.]+)", prompt)
            steps = int(float(steps_match.group(1))) if steps_match else 5000
            
            period = "recent"
            if "'period': 'today'" in prompt: period = "today's"
            elif "'period': 'yesterday'" in prompt: period = "yesterday's"
            elif "'period': 'last_7_days'" in prompt: period = "the last 7 days'"
            elif "'period': 'last_30_days'" in prompt: period = "the last 30 days'"
            
            prefix_status = f"Based on {period} aggregated data"
            return _get_deterministic_insight(bmi, sleep, aqi, steps, prefix_status=prefix_status)
        except Exception:
            # Absolute ultimate fallback
            return _get_deterministic_insight(25.0, 7.0, 50, 5000, prefix_status="Based on default parameters")

def generate_executive_summary(user_data: Dict[str, Any]) -> str:
    prompt = f"Based on the following user health data: {user_data}, generate a short executive summary of their overall health status."
    return _generate_text(prompt)

def generate_health_insights(user_data: Dict[str, Any]) -> str:
    prompt = f"""
    Analyze the following user health and fitness data: {user_data}. 
    Provide a highly actionable AI insight strictly following this 5-point format:
    <b>Current Status:</b> [status]
    <b>Main Risk Factors:</b> [risks]
    <b>Future Risk Trend:</b> [trend]
    <b>Recommended Actions:</b> [actions]
    <b>Confidence Explanation:</b> [confidence based on data quality/model]
    
    Ensure responses are medical, precise, and not generic. Do not hallucinate. Use <b> HTML tags for headers and important terms. Use <br/> for newlines.
    """
    return _generate_text(prompt)

def generate_prediction_explanation(prediction_type: str, prediction_result: Any, features: Dict[str, Any]) -> str:
    prompt = (
        f"The machine learning model predicted '{prediction_result}' for '{prediction_type}' "
        f"based on these features: {features}. Explain this prediction to a non-technical user in simple, natural language."
    )
    return _generate_text(prompt, system_message="You are a medical AI assistant explaining model predictions clearly.")

def generate_personalized_recommendations(user_data: Dict[str, Any]) -> str:
    prompt = f"Given the user's data: {user_data}, provide 3 personalized lifestyle and dietary recommendations."
    return _generate_text(prompt)

def generate_environmental_insights(env_data: Dict[str, Any]) -> str:
    prompt = f"Based on the environmental data (AQI, Temperature, etc.): {env_data}, what are the potential health impacts and recommendations?"
    return _generate_text(prompt)

def generate_trend_analysis(historical_data: List[Dict[str, Any]]) -> str:
    prompt = f"Analyze the following historical health trends over time: {historical_data}. What are the major improvements or concerning patterns?"
    return _generate_text(prompt)

def generate_periodic_report(user_data: Dict[str, Any], report_type: str = "daily") -> str:
    prompt = f"Generate a {report_type} health report for the user based on today's summary: {user_data}."
    return _generate_text(prompt)

def generate_insight(insight_type: str, context: Dict[str, Any], user_id: int) -> str:
    prompt = f"Type: {insight_type}. Context: {context}. Please provide an analysis including: Current Health Status, Why It Is Happening, Future Risk, and Recommended Actions."
    return _generate_text(prompt, system_message="You are a medical AI assistant. Keep the response clean and well-formatted.")

def generate_alert_recommendation(alert_type: str, severity: str, original_message: str) -> str:
    prompt = f"""
    An enterprise health alert was just triggered. 
    Alert Type: {alert_type}
    Severity: {severity}
    Details: {original_message}
    
    Please provide a structured, actionable recommendation exactly following this 5-point format. Do not add intro or outro text. Use valid HTML tags:
    <b>What happened?</b><br/>[Explanation of the alert]<br/><br/>
    <b>Why it happened?</b><br/>[Probable medical/lifestyle causes]<br/><br/>
    <b>Potential health impact:</b><br/>[Short-term and long-term consequences]<br/><br/>
    <b>Immediate action:</b><br/>[What the user should do right now]<br/><br/>
    <b>Long-term prevention:</b><br/>[Lifestyle changes to prevent recurrence]
    """
    try:
        recommendation = _generate_text(prompt, system_message="You are a strict medical AI assistant providing actionable, precise alert recommendations.")
        return recommendation
    except Exception:
        # Fallback
        return (
            f"<b>What happened?</b><br/>{original_message}<br/><br/>"
            f"<b>Why it happened?</b><br/>Threshold was breached.<br/><br/>"
            f"<b>Potential health impact:</b><br/>Depends on the severity ({severity}).<br/><br/>"
            f"<b>Immediate action:</b><br/>Review your recent health logs.<br/><br/>"
            f"<b>Long-term prevention:</b><br/>Maintain a balanced lifestyle."
        )
