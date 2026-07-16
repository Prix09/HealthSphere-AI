import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

def send_subscription_email(to_email: str):
    """
    Attempts to send a real email using standard SMTP configurations.
    Set the environment variables SMTP_HOST, SMTP_PORT, SMTP_USER, and SMTP_PASS in the .env file.
    """
    smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", 587))
    smtp_user = os.getenv("SMTP_USER")
    smtp_pass = os.getenv("SMTP_PASS")
    
    msg = MIMEMultipart("alternative")
    msg['Subject'] = "Welcome to HealthSphere AI!"
    msg['From'] = smtp_user or "no-reply@healthsphere.ai"
    msg['To'] = to_email
    
    text = f"""
Welcome to HealthSphere AI!

We are thrilled to have you onboard. HealthSphere AI is the world's most advanced platform for predictive health intelligence and real-time telemetry processing.

Would you like to receive our daily blog updates? Please reply to this email with "YES" to opt-in.

Best regards,
The HealthSphere Team
"""
    
    part1 = MIMEText(text, "plain")
    msg.attach(part1)
    
    if not smtp_user or not smtp_pass:
        print("--------------------------------------------------")
        print("SMTP_USER and SMTP_PASS are not set. Skipping real internet email dispatch.")
        print(f"Would have sent the following real email to {to_email}:\n\n{text}")
        print("--------------------------------------------------")
        return True # Simulate success if no credentials provided so UI proceeds smoothly
        
    try:
        server = smtplib.SMTP(smtp_host, smtp_port)
        server.starttls()
        server.login(smtp_user, smtp_pass)
        server.sendmail(msg['From'], to_email, msg.as_string())
        server.quit()
        print(f"Real email successfully dispatched to {to_email}!")
        return True
    except Exception as e:
        print(f"Failed to dispatch real email via SMTP: {e}")
        return False
