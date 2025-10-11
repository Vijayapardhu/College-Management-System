"""
OTP Utility Functions - Cache-Based
Handles OTP generation, validation, and email sending using Django cache
"""
import random
import string
from django.core.cache import cache
from django.core.mail import send_mail
from django.conf import settings


def generate_otp_code(length=6):
    """Generate a random 6-digit OTP code"""
    return ''.join(random.choices(string.digits, k=length))


def create_otp(user, ip_address=None):
    """
    Create and store OTP in cache
    Returns the OTP code
    Cache key: otp_{user_id}
    Expires in 10 minutes (600 seconds)
    """
    otp_code = generate_otp_code()
    cache_key = f'otp_{user.id}'
    
    # Store OTP in cache with 600 second (10 minute) expiry
    cache.set(cache_key, {
        'code': otp_code,
        'email': user.email,
        'ip_address': ip_address,
        'attempts': 0
    }, timeout=600)
    
    print(f"[OTP] Generated OTP: {otp_code} for user: {user.email}")
    print(f"[OTP] Stored in cache with key: {cache_key}")
    
    # Also store in database for audit trail (optional)
    try:
        from .models import OTP
        from django.utils import timezone
        from datetime import timedelta
        
        OTP.objects.filter(user=user, is_used=False).update(is_used=True)
        OTP.objects.create(
            user=user,
            otp_code=otp_code,
            expires_at=timezone.now() + timedelta(minutes=10),
            ip_address=ip_address
        )
    except:
        pass  # Cache is primary, database is just for logging
    
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
    Verify OTP from cache
    Returns (True, 'Success') if valid, (False, error_message) if invalid
    """
    cache_key = f'otp_{user.id}'
    
    print(f"[OTP] Verifying OTP for user: {user.email}")
    print(f"[OTP] Entered code: '{otp_code}'")
    print(f"[OTP] Cache key: {cache_key}")
    
    # Get OTP data from cache
    otp_data = cache.get(cache_key)
    
    if not otp_data:
        print(f"[OTP] No OTP found in cache (expired or not generated)")
        return False, "OTP expired or not found. Please request a new one."
    
    print(f"[OTP] Found OTP in cache: {otp_data['code']}")
    print(f"[OTP] Attempts so far: {otp_data.get('attempts', 0)}")
    
    # Check attempts
    if otp_data.get('attempts', 0) >= 5:
        cache.delete(cache_key)
        print(f"[OTP] Too many attempts, OTP invalidated")
        return False, "Too many failed attempts. Please request a new OTP."
    
    # Verify OTP
    if otp_data['code'] == otp_code:
        # OTP is correct - delete from cache
        cache.delete(cache_key)
        print(f"[OTP] ✅ OTP verified successfully!")
        
        # Mark as used in database (for audit)
        try:
            from .models import OTP
            OTP.objects.filter(user=user, otp_code=otp_code, is_used=False).update(is_used=True)
        except:
            pass
        
        return True, "Success"
    else:
        # Wrong OTP - increment attempts
        otp_data['attempts'] = otp_data.get('attempts', 0) + 1
        cache.set(cache_key, otp_data, timeout=600)
        
        remaining = 5 - otp_data['attempts']
        print(f"[OTP] ❌ Wrong OTP. Attempts remaining: {remaining}")
        
        return False, f"Invalid OTP. {remaining} attempts remaining."


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


def get_otp_from_cache(user_id):
    """Get OTP data from cache for debugging"""
    cache_key = f'otp_{user_id}'
    return cache.get(cache_key)

