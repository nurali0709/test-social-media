'''Sending verification email'''
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from celery import Celery
from social_media.config import SMTP_HOST, SMTP_PASSWORD, SMTP_PORT, SMTP_USER

celery = Celery('tasks', broker="redis://localhost:6379")


@celery.task
def send_verification_code(email, verification_code):
    '''Sending email using SMTP library and celery'''
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
    except smtplib.SMTPException as smtp_ex:
        print(f"Failed to send verification code email: {str(smtp_ex)}")
    except Exception as ex:
        print(f"An error occurred while sending verification code email: {str(ex)}")
