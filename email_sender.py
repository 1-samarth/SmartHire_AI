import smtplib
import os
from email.mime.text import MIMEText
from dotenv import load_dotenv

load_dotenv()

def send_email(to_email):
    sender = os.getenv("EMAIL_SENDER")
    password = os.getenv("EMAIL_PASSWORD")

    if not sender or not password:
        return False, "Missing EMAIL_SENDER or EMAIL_PASSWORD in .env"

    subject = "Interview Invitation - SmartHire AI"

    body = """
Dear Candidate,

Congratulations!

You have been shortlisted for the interview.

Our HR team will contact you soon.

Regards
SmartHire AI
"""

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = to_email

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587, timeout=20)
        server.starttls()
        server.login(sender, password)
        server.sendmail(sender, to_email, msg.as_string())
        server.quit()
        return True, "Email sent successfully"

    except Exception as e:
        return False, str(e)