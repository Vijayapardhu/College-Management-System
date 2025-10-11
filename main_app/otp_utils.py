"""
OTP Utility Functions
Handles OTP generation, validation, and email sending
"""
import random
import string
from datetime import timedelta
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from .models import OTP


def generate_otp_code(length=6):
    """Generate a random 6-digit OTP code"""
    return ''.join(random.choices(string.digits, k=length))


def create_otp(user, ip_address=None):
    """
    Create and return a new OTP for the user
    Expires in 10 minutes
    """
    # Invalidate all previous OTPs for this user
    OTP.objects.filter(user=user, is_used=False).update(is_used=True)
    
    # Generate new OTP
    otp_code = generate_otp_code()
    expires_at = timezone.now() + timedelta(minutes=10)
    
    otp = OTP.objects.create(
        user=user,
        otp_code=otp_code,
        expires_at=expires_at,
        ip_address=ip_address
    )
    
    return otp


def send_otp_email(user, otp_code):
    """
    Send OTP to user's email
    Returns True if email sent successfully, False otherwise
    """
    subject = 'EduVision - Your Login OTP'
    
    message = f"""
Hello {user.first_name} {user.last_name},

Your One-Time Password (OTP) for logging into EduVision is:

    {otp_code}

This OTP is valid for 10 minutes only.

If you did not request this OTP, please ignore this email.

Security Tips:
- Do not share this OTP with anyone
- EduVision will never ask for your OTP via phone or email
- Always logout after using the system

Thank you,
EduVision Team

---
This is an automated email. Please do not reply.
    """
    
    from_email = settings.EMAIL_HOST_USER
    recipient_list = [user.email]
    
    try:
        send_mail(
            subject,
            message,
            from_email,
            recipient_list,
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Error sending OTP email: {e}")
        return False


def verify_otp(user, otp_code):
    """
    Verify the OTP code for the user
    Returns (True, OTP) if valid, (False, error_message) if invalid
    """
    try:
        otp = OTP.objects.filter(
            user=user,
            otp_code=otp_code,
            is_used=False
        ).latest('created_at')
        
        if not otp.is_valid():
            if timezone.now() > otp.expires_at:
                return False, "OTP has expired. Please request a new one."
            else:
                return False, "Invalid OTP code."
        
        # Mark OTP as used
        otp.is_used = True
        otp.save()
        
        return True, otp
        
    except OTP.DoesNotExist:
        return False, "Invalid OTP code."


def resend_otp(user, ip_address=None):
    """
    Resend OTP to user
    Returns (True, otp) if successful, (False, error_message) if failed
    """
    try:
        # Create new OTP
        otp = create_otp(user, ip_address)
        
        # Send email
        if send_otp_email(user, otp.otp_code):
            return True, otp
        else:
            return False, "Failed to send OTP email. Please try again."
            
    except Exception as e:
        return False, f"Error: {str(e)}"

