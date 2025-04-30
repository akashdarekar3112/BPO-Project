from datetime import datetime, timedelta
from django.core.mail import send_mail
from django.conf import settings
from django.core.signing import TimestampSigner
import jwt
from .sendgrid_email import send_email_via_sendgrid


signer = TimestampSigner()

def send_verification_email(user):
    payload = {
        'uid': str(user.id),
        'exp': datetime.utcnow() + timedelta(hours=24),
        'type': 'access'
    }
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')

    verification_link = f"https://successbpo.com/api/users/email_verification?token={token}"
    print(verification_link, "==================")

    subject = "Verify Your Email"
    message = f"Please click the following link to verify your email:\n{verification_link}"
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [user.email]

    send_mail(subject, message, from_email, recipient_list)




def send_payment_success_email(user):
    subject = "Payment Successful"
    message = f"Hi {user.first_name},\n\nYour payment was successful. Thank you for subscribing!"
    send_email_via_sendgrid(user.email, subject, message)



def send_payment_failed_email(user):
    subject = "Payment Failed"
    message = f"Hi {user.first_name},\n\nUnfortunately, your recent payment failed. Please update your payment method."
    send_email_via_sendgrid(user.email, subject, message)
