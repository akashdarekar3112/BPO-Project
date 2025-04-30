# import sendgrid
# from sendgrid.helpers.mail import Mail, Email, To, Content
# from django.conf import settings
# from django.urls import reverse
# from django.utils.http import urlsafe_base64_encode, force_text
# from django.contrib.sites.shortcuts import get_current_site
# from .tokens import account_activation_token  # You need to implement this part (see below)
# from django.contrib.auth.tokens import default_token_generator

# def send_verification_email(user):
#     """
#     Sends an email verification link to the user after registration.
#     """
#     # Generate the email token
#     token = default_token_generator.make_token(user)

#     # Get the email verification URL
#     uid = urlsafe_base64_encode(force_text(user.pk).encode())
#     verification_url = f"{get_current_site(request).domain}{reverse('verify_email', kwargs={'uidb64': uid, 'token': token})}"

#     # Prepare the SendGrid email content
#     subject = "Verify Your Email Address"
#     from_email = Email(settings.SENDGRID_FROM_EMAIL)
#     to_email = To(user.email)
#     content = Content("text/plain", f"Please click the link to verify your email address: {verification_url}")

#     # Create and send the email via SendGrid
#     mail = Mail(from_email, to_email, subject, content)

#     try:
#         sendgrid_client = sendgrid.SendGridAPIClient(api_key=settings.SENDGRID_API_KEY)
#         response = sendgrid_client.send(mail)
#         print(f"Email sent! Status code: {response.status_code}")
#     except Exception as e:
#         print(f"Error sending email: {e}")