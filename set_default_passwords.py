"""
Script to set default password 'aditya' for all users
Run this once after implementing OTP authentication
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'student_management_system.settings')
django.setup()

from main_app.models import CustomUser

def set_default_password():
    """Set default password 'aditya' for all users"""
    default_password = 'aditya'
    
    users = CustomUser.objects.all()
    count = users.count()
    
    print(f"Found {count} users in the system.")
    print(f"Setting default password '{default_password}' for all users...\n")
    
    updated_count = 0
    for user in users:
        user.set_password(default_password)
        user.save()
        updated_count += 1
        print(f"✓ Updated password for: {user.email} ({user.get_user_type_display()})")
    
    print(f"\n✅ Successfully updated passwords for {updated_count} users!")
    print(f"\n📧 All users can now login with password: '{default_password}'")
    print("⚠️  Users will receive OTP via email after entering correct credentials.")

if __name__ == '__main__':
    try:
        set_default_password()
    except Exception as e:
        print(f"❌ Error: {str(e)}")

