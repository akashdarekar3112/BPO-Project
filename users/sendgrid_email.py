import sendgrid
from sendgrid.helpers.mail import Mail, Email, To, Content
from django.conf import settings
import logging

logger = logging.getLogger("django")

def send_email_via_sendgrid(to_email, subject, content):
    try:
        sg = sendgrid.SendGridAPIClient(api_key=settings.SENDGRID_API_KEY)
        from_email = Email(settings.DEFAULT_FROM_EMAIL)
        to_email = To(to_email)
        content = Content("text/plain", content)
        mail = Mail(from_email, to_email, subject, content)
        response = sg.client.mail.send.post(request_body=mail.get())
        logger.info(f"SendGrid email sent: {response.status_code}")
    except Exception as e:
        logger.error(f"Failed to send SendGrid email: {str(e)}")
