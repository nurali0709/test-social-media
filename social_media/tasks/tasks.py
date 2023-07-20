import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from celery import Celery
from social_media.config import SMTP_HOST, SMTP_PASSWORD, SMTP_PORT, SMTP_USER

celery = Celery('tasks', broker="redis://localhost:6379")


@celery.task
def send_verification_code(email, verification_code):

    # Create the email message
    msg = MIMEMultipart()
    msg['From'] = SMTP_USER
    msg['To'] = email
    msg['Subject'] = "Verification Code"

    # Create the email body
    body = f"Your verification code is: {verification_code}"
    msg.attach(MIMEText(body, 'plain'))

    # Connect to the SMTP server and send the email
    try:
        # Enable debug mode for smtplib
        smtp_debug_level = 1
        smtp_handler = logging.StreamHandler()
        smtp_handler.setLevel(smtp_debug_level)
        logger = logging.getLogger("smtplib")
        logger.addHandler(smtp_handler)

        server = smtplib.SMTP(SMTP_HOST, SMTP_PORT)
        server.set_debuglevel(smtp_debug_level)
        server.starttls()
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.sendmail(SMTP_USER, email, msg.as_string())
        server.quit()
        
        print("Verification code email sent successfully!")
    except Exception as e:
        print(f"Failed to send verification code email: {str(e)}")
