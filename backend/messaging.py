from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from dotenv import load_dotenv
import os
import logging

load_dotenv()

logger = logging.getLogger(__name__)

sg = SendGridAPIClient(os.getenv('SENDGRID_API_KEY'))

def send_email_update(to_email: str, content: str, client_id: int):
    try:
        message = Mail(
            from_email='advisor@relate.io',
            to_emails=to_email,
            subject='Your Weekly Portfolio Update',
            html_content=f"<p>{content}</p><br/><a href='http://localhost:3000/feedback?client_id={client_id}'>Provide Feedback</a>"
        )
        response = sg.send(message)
        if response.status_code != 202:
            raise Exception(f"Email send failed with status {response.status_code}")
        logger.info(f"Email sent to {to_email}")
    except Exception as e:
        logger.error(f"Error sending email: {e}")
        raise