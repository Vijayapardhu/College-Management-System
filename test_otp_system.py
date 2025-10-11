"""
Test OTP Generation and Verification
Run this to verify the OTP system is working correctly
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'student_management_system.settings')
django.setup()

from main_app.models import CustomUser, OTP
from main_app.otp_utils import create_otp, verify_otp
from django.utils import timezone

print("="*60)
print("  OTP SYSTEM TEST")
print("="*60)

# Get admin user
try:
    user = CustomUser.objects.get(email='admin@eduvision.com')
    print(f"\n✅ Found user: {user.email}")
    
    # Create OTP
    print("\n1. Creating OTP...")
    otp = create_otp(user, ip_address='127.0.0.1')
    print(f"   ✅ OTP Created: {otp.otp_code}")
    print(f"   Created at: {otp.created_at}")
    print(f"   Expires at: {otp.expires_at}")
    print(f"   Is used: {otp.is_used}")
    print(f"   Is valid: {otp.is_valid()}")
    
    # Check database
    print("\n2. Checking database...")
    db_otp = OTP.objects.filter(user=user, is_used=False).latest('created_at')
    print(f"   ✅ OTP in DB: {db_otp.otp_code}")
    print(f"   Matches created OTP: {db_otp.otp_code == otp.otp_code}")
    
    # Test verification with correct OTP
    print("\n3. Testing verification with CORRECT OTP...")
    is_valid, result = verify_otp(user, otp.otp_code)
    print(f"   Result: {'✅ VALID' if is_valid else '❌ INVALID'}")
    if is_valid:
        print(f"   OTP object: {result}")
    else:
        print(f"   Error message: {result}")
    
    # Check if OTP was marked as used
    otp.refresh_from_db()
    print(f"   OTP marked as used: {otp.is_used}")
    
    # Test verification with wrong OTP
    print("\n4. Testing verification with WRONG OTP...")
    is_valid2, result2 = verify_otp(user, '000000')
    print(f"   Result: {'✅ VALID' if is_valid2 else '❌ INVALID'}")
    print(f"   Error message: {result2}")
    
    print("\n" + "="*60)
    print("  TEST COMPLETE")
    print("="*60)
    
except CustomUser.DoesNotExist:
    print("\n❌ Admin user not found!")
    print("   Create one first using: python set_default_passwords.py")
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()

