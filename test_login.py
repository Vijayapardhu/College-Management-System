#!/usr/bin/env python
"""
Test Login Credentials - Quick verification script
Run: python test_login.py
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'student_management_system.settings')
django.setup()

from main_app.models import CustomUser, Student, Staff, Management
from django.contrib.auth.hashers import check_password

def test_login_credentials():
    """Test if login credentials are working"""
    print("=" * 80)
    print("🔍 LOGIN CREDENTIALS TEST")
    print("=" * 80)
    
    # Test all users
    all_users = CustomUser.objects.all()
    
    if not all_users.exists():
        print("\n❌ No users found in database!")
        print("   Run: python manage.py createsuperuser")
        return
    
    print(f"\n✅ Found {all_users.count()} users in system\n")
    
    # Group users by type
    students = CustomUser.objects.filter(user_type='3')
    staff = CustomUser.objects.filter(user_type='2')
    admins = CustomUser.objects.filter(user_type='1')
    management = CustomUser.objects.filter(user_type='4')
    
    # Test Students
    print("\n📚 STUDENTS:")
    print("-" * 80)
    if students.exists():
        for user in students[:5]:  # Show first 5
            try:
                student = Student.objects.get(admin=user)
                roll = student.roll_number or 'N/A'
                print(f"   ✓ {user.first_name} {user.last_name}")
                print(f"     Email: {user.email}")
                print(f"     Roll Number: {roll}")
                print(f"     Can login with: {user.email} OR {roll}")
                print()
            except Student.DoesNotExist:
                print(f"   ⚠️  {user.email} - Student profile missing!")
    else:
        print("   No students found")
    
    # Test Staff
    print("\n👨‍🏫 STAFF/FACULTY:")
    print("-" * 80)
    if staff.exists():
        for user in staff[:5]:  # Show first 5
            try:
                staff_obj = Staff.objects.get(admin=user)
                emp_id = staff_obj.employee_id or 'N/A'
                print(f"   ✓ {user.first_name} {user.last_name}")
                print(f"     Email: {user.email}")
                print(f"     Employee ID: {emp_id}")
                print(f"     Can login with: {user.email}" + (f" OR {emp_id}" if emp_id != 'N/A' else ""))
                print()
            except Staff.DoesNotExist:
                print(f"   ⚠️  {user.email} - Staff profile missing!")
    else:
        print("   No staff found")
    
    # Test Admins/HOD
    print("\n👑 ADMINS/HOD:")
    print("-" * 80)
    if admins.exists():
        for user in admins[:5]:
            print(f"   ✓ {user.first_name} {user.last_name}")
            print(f"     Email: {user.email}")
            print(f"     Username: {user.username or 'N/A'}")
            print(f"     Can login with: {user.email}")
            print()
    else:
        print("   No admins found")
    
    # Test Management
    print("\n💼 MANAGEMENT:")
    print("-" * 80)
    if management.exists():
        for user in management[:5]:
            try:
                mgmt_obj = Management.objects.get(admin=user)
                emp_id = mgmt_obj.employee_id or 'N/A'
                print(f"   ✓ {user.first_name} {user.last_name}")
                print(f"     Email: {user.email}")
                print(f"     Employee ID: {emp_id}")
                print(f"     Can login with: {user.email}" + (f" OR {emp_id}" if emp_id != 'N/A' else ""))
                print()
            except Management.DoesNotExist:
                print(f"   ⚠️  {user.email} - Management profile missing!")
    else:
        print("   No management users found")
    
    # Password verification
    print("\n🔐 PASSWORD VERIFICATION:")
    print("-" * 80)
    print("   Testing default password: 'aditya'")
    
    default_password = 'aditya'
    users_with_default = []
    users_with_custom = []
    
    for user in all_users[:10]:  # Test first 10 users
        if check_password(default_password, user.password):
            users_with_default.append(user.email)
        else:
            users_with_custom.append(user.email)
    
    if users_with_default:
        print(f"\n   ✅ {len(users_with_default)} users have default password 'aditya':")
        for email in users_with_default[:3]:
            print(f"      - {email}")
        if len(users_with_default) > 3:
            print(f"      ... and {len(users_with_default) - 3} more")
    
    if users_with_custom:
        print(f"\n   ⚠️  {len(users_with_custom)} users have custom passwords")
        print(f"      (They need to remember their password or reset it)")
    
    # Summary
    print("\n" + "=" * 80)
    print("📊 SUMMARY:")
    print("=" * 80)
    print(f"   Total Users: {all_users.count()}")
    print(f"   Students: {students.count()}")
    print(f"   Staff: {staff.count()}")
    print(f"   Admins: {admins.count()}")
    print(f"   Management: {management.count()}")
    print()
    print("✅ Login methods enabled:")
    print("   1. Email address (all users)")
    print("   2. Roll Number (students)")
    print("   3. Employee ID (staff & management)")
    print("   4. Username (if set)")
    print()
    print("🔑 Default password: aditya")
    print("=" * 80)

if __name__ == '__main__':
    test_login_credentials()

