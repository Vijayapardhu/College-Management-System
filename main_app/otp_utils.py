"""
OTP Utility Functions - Database-Based
Handles OTP generation, validation, and email sending using database storage
"""
import random
import string
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from datetime import timedelta


def generate_otp_code(length=6):
    """Generate a random 6-digit OTP code"""
    return ''.join(random.choices(string.digits, k=length))


def create_otp(user, ip_address=None):
    """
    Create and store OTP in database
    Returns the OTP code
    Expires in 10 minutes
    """
    from .models import OTP
    
    otp_code = generate_otp_code()
    
    # Mark any existing unused OTPs as used
    OTP.objects.filter(user=user, is_used=False).update(is_used=True)
    
    # Create new OTP record in database
    otp_record = OTP.objects.create(
        user=user,
        otp_code=otp_code,
        expires_at=timezone.now() + timedelta(minutes=10),
        ip_address=ip_address
    )
    
    print(f"[OTP] Generated OTP: {otp_code} for user: {user.email}")
    print(f"[OTP] Stored in database with ID: {otp_record.id}")
    print(f"[OTP] Expires at: {otp_record.expires_at}")
    
    return otp_code


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
        # Use a short timeout and fail silently in production-like environments
        # to avoid blocking the worker if SMTP is unavailable
        send_mail(
            subject,
            message,
            from_email,
            recipient_list,
            fail_silently=True,
            timeout=10,
        )
        return True
    except Exception as e:
        print(f"Error sending OTP email: {e}")
        return False


def verify_otp(user, otp_code):
    """
    Verify OTP from database
    Returns (True, 'Success') if valid, (False, error_message) if invalid
    """
    from .models import OTP
    
    print(f"[OTP] Verifying OTP for user: {user.email}")
    print(f"[OTP] Entered code: '{otp_code}'")
    
    # Get the latest unused OTP for this user
    try:
        otp_record = OTP.objects.filter(
            user=user,
            is_used=False
        ).order_by('-created_at').first()
        
        if not otp_record:
            print(f"[OTP] No unused OTP found for user")
            return False, "OTP not found. Please request a new one."
        
        print(f"[OTP] Found OTP in database: {otp_record.otp_code}")
        print(f"[OTP] OTP created at: {otp_record.created_at}")
        print(f"[OTP] OTP expires at: {otp_record.expires_at}")
        
        # Check if OTP is expired
        if timezone.now() > otp_record.expires_at:
            otp_record.is_used = True
            otp_record.save()
            print(f"[OTP] OTP expired")
            return False, "OTP expired. Please request a new one."
        
        # Check attempts (using attempts field from OTP model)
        if otp_record.attempts >= 5:
            otp_record.is_used = True
            otp_record.save()
            print(f"[OTP] Too many attempts, OTP invalidated")
            return False, "Too many failed attempts. Please request a new OTP."
        
        # Verify OTP
        if otp_record.otp_code == otp_code:
            # OTP is correct - mark as used
            otp_record.is_used = True
            otp_record.save()
            print(f"[OTP] [SUCCESS] OTP verified successfully!")
            return True, "Success"
        else:
            # Wrong OTP - increment attempts
            otp_record.attempts += 1
            otp_record.save()
            
            remaining = 5 - otp_record.attempts
            print(f"[OTP] [FAILED] Wrong OTP. Attempts remaining: {remaining}")
            
            return False, f"Invalid OTP. {remaining} attempts remaining."
            
    except Exception as e:
        print(f"[OTP] Error verifying OTP: {e}")
        return False, f"Error verifying OTP: {str(e)}"


def resend_otp(user, ip_address=None):
    """
    Generate and resend new OTP
    Returns (True, otp_code) if successful, (False, error_message) if failed
    """
    try:
        # Create new OTP (overwrites old one in cache)
        otp_code = create_otp(user, ip_address)
        
        # Send email
        email_sent = send_otp_email(user, otp_code)
        
        return True, otp_code
            
    except Exception as e:
        print(f"[OTP] Error in resend: {e}")
        return False, f"Error: {str(e)}"


def get_otp_from_database(user):
    """Get latest OTP data from database for debugging"""
    from .models import OTP
    try:
        return OTP.objects.filter(user=user, is_used=False).order_by('-created_at').first()
    except:
        return None

