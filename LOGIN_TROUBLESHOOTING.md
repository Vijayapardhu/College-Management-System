# 🔧 Login Issue Troubleshooting Guide

## ✅ Fixed Issues

I've updated the authentication system to support **ALL login methods**:

### **What was fixed:**
1. ✅ **EmailBackend** - Now supports Email, Roll Number, Employee ID
2. ✅ **RollNumberOrEmailBackend** - Enhanced with Employee ID support
3. ✅ **Login page** - Made mobile responsive
4. ✅ **Case-insensitive** - Login works with any case (ABC123 = abc123)

---

## 🔐 How Login Works Now

Users can login with **ANY** of these:

### **Students:**
- ✅ Email: `student@example.com`
- ✅ Roll Number: `STU2025001`, `C23001`, etc.
- ✅ Password: `aditya` (default) or custom password

### **Staff/Faculty:**
- ✅ Email: `staff@example.com`
- ✅ Employee ID: `EMP001`, `FAC123`, etc. (if set)
- ✅ Password: `aditya` (default) or custom password

### **Admin/HOD:**
- ✅ Email: `admin@example.com`
- ✅ Username: (if set)
- ✅ Password: `aditya` (default) or custom password

### **Management:**
- ✅ Email: `manager@example.com`
- ✅ Employee ID: `MGT001`, etc. (if set)
- ✅ Password: `aditya` (default) or custom password

---

## 🐛 Common Login Errors & Solutions

### Error 1: "Invalid email/ID or password"

**Possible Causes:**
1. Wrong password
2. User doesn't exist in database
3. Email/ID typo
4. Account not properly created

**Solutions:**
```bash
# Check if user exists in database:
python manage.py shell
>>> from main_app.models import CustomUser
>>> CustomUser.objects.filter(email='your-email@example.com').exists()
>>> # Should return True if user exists

# Check user's password hash:
>>> user = CustomUser.objects.get(email='your-email@example.com')
>>> from django.contrib.auth.hashers import check_password
>>> check_password('aditya', user.password)
>>> # Should return True if password is 'aditya'
```

### Error 2: "Authentication error"

**Possible Causes:**
1. Database connection issue
2. Missing Student/Staff profile
3. Corrupted user record

**Solutions:**
1. Check database connection in settings.py
2. Verify Student/Staff profile exists:
```bash
python manage.py shell
>>> from main_app.models import Student, CustomUser
>>> user = CustomUser.objects.get(email='student@example.com')
>>> Student.objects.filter(admin=user).exists()
>>> # Should return True for students
```

### Error 3: "Session expired. Please login again"

**Cause:** OTP verification took too long

**Solution:** Click "Resend OTP" to get a new code

### Error 4: "Invalid OTP"

**Possible Causes:**
1. Wrong OTP entered
2. OTP expired (10 minutes)
3. OTP already used

**Solutions:**
1. Check email for correct OTP
2. Click "Resend OTP" if expired
3. If email doesn't work, OTP shows on screen

---

## 🔍 Quick Diagnostic Steps

### Step 1: Verify User Exists
```bash
python manage.py shell
>>> from main_app.models import CustomUser
>>> user = CustomUser.objects.get(email='YOUR_EMAIL')
>>> print(f"Name: {user.first_name} {user.last_name}")
>>> print(f"Type: {user.user_type}")
>>> print(f"Email: {user.email}")
>>> print(f"Active: {user.is_active}")
```

### Step 2: Test Password
```bash
>>> from django.contrib.auth.hashers import check_password
>>> check_password('aditya', user.password)
# If False, password is NOT 'aditya'
```

### Step 3: Reset Password (if needed)
```bash
python manage.py shell
>>> from main_app.models import CustomUser
>>> user = CustomUser.objects.get(email='YOUR_EMAIL')
>>> user.set_password('aditya')
>>> user.save()
>>> print("Password reset to 'aditya'")
```

### Step 4: Check Student/Staff Profile
```bash
python manage.py shell
>>> from main_app.models import CustomUser, Student, Staff
>>> user = CustomUser.objects.get(email='YOUR_EMAIL')

# For Students (user_type='3'):
>>> Student.objects.filter(admin=user).exists()
>>> student = Student.objects.get(admin=user)
>>> print(f"Roll Number: {student.roll_number}")

# For Staff (user_type='2'):
>>> Staff.objects.filter(admin=user).exists()
>>> staff = Staff.objects.get(admin=user)
>>> print(f"Employee ID: {staff.employee_id}")
```

---

## 📝 Test Specific Accounts

### Test the 3 WhatsApp Students:
```bash
Email: ksathwikraja5@gmail.com
Password: student123
Roll Number: STU2025001

Email: manikantanagireddy3@gmail.com
Password: student123
Roll Number: STU2025002

Email: asridhswaroop@gmail.com
Password: student123
Roll Number: STU2025003
```

Try logging in with:
- Their email addresses
- Their roll numbers
- Password: `student123`

---

## 🔧 Quick Fixes

### Reset All Passwords to 'aditya':
```bash
python manage.py shell
>>> from main_app.models import CustomUser
>>> for user in CustomUser.objects.all():
...     user.set_password('aditya')
...     user.save()
>>> print("All passwords reset!")
```

### Create Superuser:
```bash
python manage.py createsuperuser
# Follow prompts
```

---

## 🆘 If Still Not Working

1. **Clear browser cache** (Ctrl + Shift + Delete)
2. **Clear Django sessions**:
   ```bash
   python manage.py shell
   >>> from django.contrib.sessions.models import Session
   >>> Session.objects.all().delete()
   ```
3. **Check server logs** for specific error messages
4. **Try incognito/private browser window**
5. **Verify email is correct** (no spaces, correct domain)

---

## ✅ Verification Checklist

- [ ] Server is running (`python manage.py runserver`)
- [ ] Database has users (`CustomUser.objects.count()` > 0)
- [ ] User has correct password (`check_password('aditya', user.password)`)
- [ ] Student has roll_number set (for students)
- [ ] Staff has employee_id set (for staff)
- [ ] User account is active (`user.is_active == True`)
- [ ] No typos in email/ID
- [ ] Using correct password

---

**Need help?** Run the commands above in Django shell to diagnose your specific issue.

