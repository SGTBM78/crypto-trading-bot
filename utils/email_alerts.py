import os
import smtplib
from email.mime.text import MIMEText

def send_email_alert(message):
    try:
        gmail_user = os.getenv("GMAIL_USER")
        gmail_password = os.getenv("GMAIL_APP_PASSWORD")
        to_email = os.getenv("ALERT_EMAIL_TO")

        msg = MIMEText(message)
        msg['Subject'] = "🚨 Crypto Bot Alert"
        msg['From'] = gmail_user
        msg['To'] = to_email

        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(gmail_user, gmail_password)
        server.sendmail(gmail_user, to_email, msg.as_string())
        server.quit()
    except Exception as e:
        print(f"❌ Email failed: {e}")
