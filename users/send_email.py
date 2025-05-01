from datetime import datetime, timedelta
from django.core.mail import send_mail
from django.conf import settings
from django.core.signing import TimestampSigner
import jwt
from .sendgrid_email import send_email_via_sendgrid
import sendgrid
from sendgrid.helpers.mail import Email, To, Content, Mail, TrackingSettings, ClickTracking, HtmlContent


signer = TimestampSigner()

def send_verification_email(user):
    payload = {
        'uid': str(user.id),
        'exp': datetime.utcnow() + timedelta(hours=24),
        'type': 'access'
    }
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')

    verification_link = f"http://localhost:5173/verify-email?token={token}"
    print(verification_link, "==================")

    # Create HTML email content
    html_content = f"""
    <html>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; max-width: 600px; margin: 0 auto; padding: 20px;">
        <div style="text-align: center; margin-bottom: 30px;">
            <h1 style="color: #333;">Welcome</h1>
        </div>
        
        <p style="color: #666;">Hello {user.first_name},</p>
        
        <p style="color: #666;">Welcome to SuccessBPO! Please take a moment to verify your email address to unlock the full potential of your subscription.</p>
        
        <div style="text-align: center; margin: 30px 0;">
            <a href="{verification_link}" style="background-color: #7C3AED; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; font-weight: bold;">Verify Email Address</a>
        </div>
        
        <p style="color: #666;">If the button doesn't work, copy and paste the link below into your browser:</p>
        <p style="background-color: #f5f5f5; padding: 10px; border-radius: 4px; word-break: break-all;">
            <a href="{verification_link}" style="color: #7C3AED; text-decoration: none;">{verification_link}</a>
        </p>
        
        <div style="margin-top: 30px;">
            <h3 style="color: #333;">Why Verify?</h3>
            <ul style="color: #666;">
                <li>Keep your company profile active and discoverable by banks, lenders, and corporate buyers.</li>
                <li>Enjoy greater visibility as we continuously onboard more banks and corporates.</li>
                <li>Boost your chances of connecting with opportunities that align with your goals.</li>
            </ul>
        </div>

        <div style="margin-top: 40px; padding-top: 20px; border-top: 1px solid #eee;">
            <p style="color: #666; margin-bottom: 5px;">Best regards,</p>
            <p style="color: #333; font-weight: bold; margin-top: 0;">SuccessBPO Team</p>
            <p style="color: #666; margin-top: 5px;">
                <a href="https://successbpo.com" style="color: #7C3AED; text-decoration: none;">www.successbpo.com</a>
            </p>
        </div>
    </body>
    </html>
    """

    subject = "Verify Your Email"
    
    try:
        sg = sendgrid.SendGridAPIClient(api_key=settings.SENDGRID_API_KEY)
        from_email = Email(settings.DEFAULT_FROM_EMAIL)
        to_email = To(user.email)
        content = HtmlContent(html_content)
        mail = Mail(from_email, to_email, subject, content)
        
        # Disable click tracking
        mail.tracking_settings = TrackingSettings()
        mail.tracking_settings.click_tracking = ClickTracking(enable=False)
        
        response = sg.client.mail.send.post(request_body=mail.get())
        print(f"Verification email sent: {response.status_code}")
    except Exception as e:
        print(f"Failed to send verification email: {str(e)}")
        # Fallback to Django's send_mail if SendGrid fails
        send_mail(subject, f"Please verify your email by clicking this link: {verification_link}", 
                 settings.DEFAULT_FROM_EMAIL, [user.email], html_message=html_content)




def send_payment_success_email(user):
    html_content = f"""
    <html>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; max-width: 600px; margin: 0 auto; padding: 20px;">
        <div style="text-align: center; margin-bottom: 30px;">
            <h1 style="color: #333;">Payment Successful</h1>
        </div>
        
        <p style="color: #666;">Hello {user.first_name},</p>
        
        <div style="background-color: #f8f8f8; border-left: 4px solid #4CAF50; padding: 20px; margin: 20px 0;">
            <p style="color: #333; margin: 0;">Your payment was successful. Thank you for subscribing to SuccessBPO!</p>
        </div>
        
        <p style="color: #666;">If you have any questions or need assistance, please don't hesitate to contact our support team.</p>

        <div style="margin-top: 40px; padding-top: 20px; border-top: 1px solid #eee;">
            <p style="color: #666; margin-bottom: 5px;">Best regards,</p>
            <p style="color: #333; font-weight: bold; margin-top: 0;">SuccessBPO Team</p>
            <p style="color: #666; margin-top: 5px; text-decoration: none;">www.successbpo.com</p>
        </div>
    </body>
    </html>
    """
    
    subject = "Payment Successful"
    try:
        sg = sendgrid.SendGridAPIClient(api_key=settings.SENDGRID_API_KEY)
        from_email = Email(settings.DEFAULT_FROM_EMAIL)
        to_email = To(user.email)
        content = HtmlContent(html_content)
        mail = Mail(from_email, to_email, subject, content)
        
        # Disable click tracking
        tracking_settings = TrackingSettings()
        tracking_settings.click_tracking = ClickTracking(enable=False)
        mail.tracking_settings = tracking_settings
        
        response = sg.client.mail.send.post(request_body=mail.get())
        print(f"Payment success email sent: {response.status_code}")
    except Exception as e:
        print(f"Failed to send payment success email: {str(e)}")
        send_mail(subject, "Your payment was successful. Thank you for subscribing!", 
                 settings.DEFAULT_FROM_EMAIL, [user.email], html_message=html_content)



def send_payment_failed_email(user):
    html_content = f"""
    <html>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; max-width: 600px; margin: 0 auto; padding: 20px;">
        <div style="text-align: center; margin-bottom: 30px;">
            <h1 style="color: #333;">Payment Failed</h1>
        </div>
        
        <p style="color: #666;">Hello {user.first_name},</p>
        
        <div style="background-color: #fff3f3; border-left: 4px solid #dc3545; padding: 20px; margin: 20px 0;">
            <p style="color: #333; margin: 0;">Unfortunately, your recent payment was unsuccessful. To ensure uninterrupted service, please update your payment method.</p>
        </div>
        
        <p style="color: #666;">To update your payment information:</p>
        <ol style="color: #666;">
            <li>Log in to your account</li>
            <li>Go to Payment Settings</li>
            <li>Update your payment method</li>
        </ol>
        
        <p style="color: #666;">If you need any assistance, our support team is here to help.</p>

        <div style="margin-top: 40px; padding-top: 20px; border-top: 1px solid #eee;">
            <p style="color: #666; margin-bottom: 5px;">Best regards,</p>
            <p style="color: #333; font-weight: bold; margin-top: 0;">SuccessBPO Team</p>
            <p style="color: #666; margin-top: 5px; text-decoration: none;">www.successbpo.com</p>
        </div>
    </body>
    </html>
    """
    
    subject = "Payment Failed"
    try:
        sg = sendgrid.SendGridAPIClient(api_key=settings.SENDGRID_API_KEY)
        from_email = Email(settings.DEFAULT_FROM_EMAIL)
        to_email = To(user.email)
        content = HtmlContent(html_content)
        mail = Mail(from_email, to_email, subject, content)
        
        # Disable click tracking
        tracking_settings = TrackingSettings()
        tracking_settings.click_tracking = ClickTracking(enable=False)
        mail.tracking_settings = tracking_settings
        
        response = sg.client.mail.send.post(request_body=mail.get())
        print(f"Payment failed email sent: {response.status_code}")
    except Exception as e:
        print(f"Failed to send payment failed email: {str(e)}")
        send_mail(subject, "Your payment failed. Please update your payment method.", 
                 settings.DEFAULT_FROM_EMAIL, [user.email], html_message=html_content)
