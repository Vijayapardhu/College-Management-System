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
    old_otps_count = OTP.objects.filter(user=user, is_used=False).update(is_used=True)
    print(f"[DEBUG] Invalidated {old_otps_count} old OTPs for user: {user.email}")
    
    # Generate new OTP
    otp_code = generate_otp_code()
    expires_at = timezone.now() + timedelta(minutes=10)
    
    print(f"[DEBUG] Creating new OTP: '{otp_code}' for user: {user.email}")
    print(f"[DEBUG] OTP will expire at: {expires_at}")
    
    otp = OTP.objects.create(
        user=user,
        otp_code=otp_code,
        expires_at=expires_at,
        ip_address=ip_address
    )
    
    print(f"[DEBUG] OTP created successfully with ID: {otp.id}")
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
    print(f"[DEBUG] Verifying OTP for user: {user.email}")
    print(f"[DEBUG] OTP code received: '{otp_code}' (length: {len(otp_code)})")
    
    # Get all OTPs for this user for debugging
    all_otps = OTP.objects.filter(user=user).order_by('-created_at')[:5]
    print(f"[DEBUG] Recent OTPs for user:")
    for otp_obj in all_otps:
        print(f"  - Code: '{otp_obj.otp_code}' | Used: {otp_obj.is_used} | Expired: {timezone.now() > otp_obj.expires_at} | Created: {otp_obj.created_at}")
    
    try:
        otp = OTP.objects.filter(
            user=user,
            otp_code=otp_code,
            is_used=False
        ).latest('created_at')
        
        print(f"[DEBUG] Found OTP: {otp.otp_code} | Created: {otp.created_at} | Expires: {otp.expires_at}")
        
        if not otp.is_valid():
            if timezone.now() > otp.expires_at:
                print(f"[DEBUG] OTP expired!")
                return False, "OTP has expired. Please request a new one."
            else:
                print(f"[DEBUG] OTP invalid (already used)!")
                return False, "Invalid OTP code."
        
        # Mark OTP as used
        otp.is_used = True
        otp.save()
        
        print(f"[DEBUG] OTP verified successfully!")
        return True, otp
        
    except OTP.DoesNotExist:
        print(f"[DEBUG] No matching OTP found in database!")
        return False, "Invalid OTP code. Please check and try again."


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

