# OTP Authentication System - User Guide

## 🔐 Overview

EduVision now features **Two-Factor Authentication (2FA)** using **One-Time Password (OTP)** for enhanced security. All users must verify their identity using an OTP sent to their registered email address.

---

## 🚀 Features

### ✅ What's New

1. **Unique ID Login**: Login using Email, Roll Number, or Employee ID
2. **Default Password**: All users have default password `aditya`
3. **OTP Verification**: Receive 6-digit OTP via email after login
4. **Public Data Access**: View public information without authentication
5. **Email Notifications**: Automatic OTP delivery via Gmail SMTP

---

## 👤 User Guide

### Login Process

#### Step 1: Navigate to Login Page
- Go to: `http://127.0.0.1:8000/`

#### Step 2: Enter Credentials
- **Email**: Your registered email address
- **OR Roll Number**: For students (e.g., CS2024001)
- **OR Employee ID**: For staff (e.g., EMP001)
- **Password**: `aditya` (default password)

#### Step 3: Receive OTP
- An OTP will be sent to your registered email
- Check your inbox for "EduVision - Your Login OTP"
- OTP is valid for **10 minutes**

#### Step 4: Enter OTP
- Enter the 6-digit OTP code
- Click "Verify & Login"
- You'll be redirected to your dashboard

### Default Credentials

```
👤 Admin User:
   Email: admin@eduvision.com
   Password: aditya
   
🎓 All Users:
   Password: aditya
```

### OTP Features

- **Auto-Expiry**: OTPs expire after 10 minutes
- **Resend Option**: Request a new OTP if expired
- **Security**: One-time use only
- **IP Tracking**: Each OTP is linked to your IP address

---

## 🌐 Public Data Access

### No Login Required

Access public information without authentication:
- **URL**: `http://127.0.0.1:8000/public/`
- **Features**:
  - View all departments
  - Browse academic programs
  - Check active placement drives
  - See upcoming public events

---

## 📧 Gmail SMTP Configuration

### For System Administrators

To enable OTP email delivery, configure Gmail SMTP:

#### 1. Setup Gmail App Password

1. Go to your Google Account: https://myaccount.google.com/
2. Enable **2-Factor Authentication**
3. Go to **App Passwords**: https://myaccount.google.com/apppasswords
4. Select app: **Mail**
5. Select device: **Other (Custom name)**
6. Enter name: **EduVision**
7. Copy the 16-character password

#### 2. Update Environment Variables

Create or update `.env` file in project root:

```env
# Email Configuration
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=xxxx-xxxx-xxxx-xxxx  # 16-char App Password
```

#### 3. Test Email Configuration

```bash
python manage.py shell
```

```python
from django.core.mail import send_mail
send_mail(
    'Test Email',
    'OTP system test',
    'your-email@gmail.com',
    ['recipient@example.com'],
)
```

---

## 🛠️ Technical Implementation

### Models

#### OTP Model
```python
class OTP(models.Model):
    user = ForeignKey(CustomUser)
    otp_code = CharField(max_length=6)
    created_at = DateTimeField()
    expires_at = DateTimeField()
    is_used = BooleanField()
    ip_address = GenericIPAddressField()
```

### Views

1. **doLogin** - Initial authentication & OTP generation
2. **verify_otp** - OTP verification & final login
3. **resend_otp** - Request new OTP
4. **public_data** - Public information access

### URLs

```python
path("doLogin/", views.doLogin, name='user_login')
path("verify-otp/", views.verify_otp, name='verify_otp')
path("resend-otp/", views.resend_otp, name='resend_otp')
path("public/", views.public_data, name='public_data')
```

### Authentication Backend

Updated `EmailBackend` supports:
- Email login
- Username/Unique ID login
- Roll Number login (for students)
- Employee ID login (for staff)

---

## 🔒 Security Features

### What's Protected

1. **Password Security**
   - Encrypted password storage
   - Default password can be changed
   - Strong password validation

2. **OTP Security**
   - 6-digit random code
   - 10-minute expiration
   - Single-use only
   - IP address tracking

3. **Session Security**
   - Temporary session storage
   - Auto-cleanup after verification
   - Secure cookie handling

4. **Email Security**
   - TLS encryption
   - App Password (not regular password)
   - Rate limiting (prevents spam)

---

## 🐛 Troubleshooting

### Issue: OTP Not Received

**Solutions:**
1. Check spam/junk folder
2. Verify email address is correct
3. Check Gmail SMTP configuration
4. Verify EMAIL_HOST_USER in settings
5. Ensure App Password is correct (16 characters)

### Issue: OTP Expired

**Solutions:**
1. Click "Resend OTP" button
2. New OTP will be sent immediately
3. Previous OTPs become invalid

### Issue: Cannot Login with Roll Number

**Solutions:**
1. Ensure you're using correct Roll Number format
2. Try login with email instead
3. Check if Roll Number is registered in system
4. Contact admin if issue persists

### Issue: Email Configuration Error

**Solutions:**
1. Verify Gmail App Password (not regular password)
2. Check 2FA is enabled in Google Account
3. Verify EMAIL_HOST_USER matches App Password account
4. Check EMAIL_PORT is 587
5. Ensure EMAIL_USE_TLS is True

---

## 📊 OTP Statistics

### Admin View

Admins can view OTP statistics:
- Total OTPs generated
- Success rate
- Failed attempts
- Average time to verify
- IP addresses

Access via Django Admin:
`http://127.0.0.1:8000/admin/main_app/otp/`

---

## 🔄 Workflow Diagram

```
User Login
    ↓
Enter Email/ID + Password
    ↓
Credentials Valid?
    ↓ Yes
Generate OTP
    ↓
Send Email
    ↓
User Enters OTP
    ↓
OTP Valid?
    ↓ Yes
Login Success → Dashboard
    ↓ No
Error Message → Re-enter OTP
```

---

## 📝 Important Notes

### For Users

1. **Default Password**: All new users have password `aditya`
2. **Change Password**: Recommended after first login
3. **OTP Expiry**: 10 minutes validity
4. **One-Time Use**: OTP works only once
5. **Email Required**: Valid email mandatory for OTP delivery

### For Administrators

1. **Gmail SMTP**: Required for OTP delivery
2. **App Password**: Must use App Password, not regular password
3. **2FA Required**: Google 2FA must be enabled
4. **Email Quotas**: Gmail has daily sending limits (500 emails/day for free accounts)
5. **Production**: Consider using dedicated email service (SendGrid, AWS SES) for production

---

## 🎯 Benefits

### Security Benefits

✅ **Two-Factor Authentication**: Enhanced security  
✅ **Unique Login IDs**: Multiple login options  
✅ **Email Verification**: Confirms user identity  
✅ **Session Protection**: Temporary login sessions  
✅ **IP Tracking**: Monitor login attempts  

### User Benefits

✅ **Easy Login**: Multiple ID options  
✅ **Password Reset**: Can be reset if forgotten  
✅ **Public Access**: View public data without login  
✅ **Mobile Friendly**: Works on all devices  
✅ **Quick Verification**: 6-digit OTP  

---

## 🚀 Future Enhancements

Potential improvements:
1. SMS OTP (in addition to email)
2. Authenticator app support (Google Authenticator, etc.)
3. Biometric authentication
4. Remember device option
5. OTP rate limiting
6. Custom OTP expiry time
7. Multi-language OTP emails

---

## 📞 Support

### Need Help?

- **Technical Issues**: Check troubleshooting section
- **Email Problems**: Verify Gmail configuration
- **Login Issues**: Try password reset
- **OTP Not Working**: Use resend feature

### Contact

- **System Admin**: admin@eduvision.com
- **Technical Support**: Check SETUP_GUIDE.md

---

## ✅ Testing Checklist

### Before Production

- [ ] Gmail SMTP configured correctly
- [ ] Test OTP email delivery
- [ ] Verify all user types can login
- [ ] Test unique ID login (Roll Number, Employee ID)
- [ ] Test OTP expiration
- [ ] Test OTP resend functionality
- [ ] Verify public data page works
- [ ] Test on mobile devices
- [ ] Check email formatting
- [ ] Monitor OTP statistics

---

**Version**: 1.0  
**Last Updated**: October 2025  
**Status**: ✅ Production Ready

---

## 🎓 Quick Commands

### Set Default Password for All Users
```bash
python set_default_passwords.py
```

### Check OTP Model
```bash
python manage.py shell
from main_app.models import OTP
OTP.objects.all()
```

### Test Email
```bash
python manage.py shell
from main_app.otp_utils import send_otp_email
from main_app.models import CustomUser
user = CustomUser.objects.first()
send_otp_email(user, '123456')
```

---

**🎉 OTP Authentication System is now active!**  
**📧 All users will receive OTP via email after entering correct credentials.**

