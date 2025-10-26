# Debug Logs Guide - Student Form Troubleshooting

This guide will help you view and interpret the comprehensive debug logs added to the student form.

## How to View Debug Logs

### 1. Backend Logs (Django Server Console)

**Where**: In your terminal/command prompt where you run `python manage.py runserver`

**What you'll see**: Detailed server-side logging with symbols:
- `✓` = Success
- `✗` = Error/Failure
- `⚠` = Warning

**Example Output**:
```
================================================================================
ADD STUDENT VIEW CALLED
Request Method: POST
POST Data: dict_keys(['csrfmiddlewaretoken', 'first_name', 'last_name', ...])
FILES Data: dict_keys(['photo', 'signature'])
✓ Form is VALID
Basic Info - Name: John Doe, Email: john@example.com
Academic Info - Course: Computer Science, Session: 2024-2025, Roll: CSE2024001
Generated password (length: 10)
Creating CustomUser object...
✓ User created successfully with ID: 123
Creating Student object...
✓ Student created successfully with ID: 456
Starting document upload process...
✓ Supabase storage initialized
Uploading photo: student_photo.jpg (45678 bytes)
✓ photo uploaded successfully: photo/student_456/20241024_123456_abc123.jpg
✓ Uploaded 2 documents successfully
Attempting to send credentials email...
✓ Email sent successfully to john@example.com
✓✓✓ Student addition completed successfully!
Redirecting to manage_student...
================================================================================
```

### 2. Frontend Logs (Browser Console)

**Where**: 
- **Chrome/Edge**: Press `F12` or `Ctrl+Shift+I` → Console tab
- **Firefox**: Press `F12` or `Ctrl+Shift+K` → Console tab
- **Safari**: Press `Cmd+Option+C`

**What you'll see**: JavaScript execution and form validation

**Example Output**:
```
========================================
Simplified Student Form LOADED
jQuery version: 3.6.0
Form element: 1 found
========================================
Submit button found: 1
========================================
✓ All form handlers initialized successfully
✓ File upload handlers: 7 attached
✓ Submit handler attached to form
Ready to accept form submissions!
========================================

[When you submit the form:]
========================================
FORM SUBMIT EVENT TRIGGERED
isSubmitting: false
Checking required fields...
✓ Field OK: first_name = John
✓ Field OK: last_name = Doe
✓ Field OK: email = john@example.com
...
✓ Validation passed, submitting form...
Form will now submit to: /student/add/
Method: POST
========================================
```

## Common Issues and What Logs Show

### Issue 1: Form Not Submitting

**Check Browser Console For**:
```javascript
✗ Required field empty: email
✗ Required field empty: roll_number
FORM VALIDATION FAILED
Empty required fields: email, roll_number
```

**Solution**: Fill in all required fields (marked with *)

---

### Issue 2: Form is Valid but Not Saving

**Check Django Console For**:
```python
✓ Form is VALID
Basic Info - Name: ...
✗✗✗ EXCEPTION in add_student: ...
Traceback (most recent call last):
  ...
```

**Solution**: Look at the exception details in the Django console

---

### Issue 3: Documents Not Uploading

**Check Django Console For**:
```python
Starting document upload process...
✗ Document upload error: Supabase configuration missing
```

**Or**:
```python
Uploading photo: image.jpg (2048000 bytes)
✗ Failed to upload photo: File size exceeds 2MB limit
```

**Solutions**:
- First error: Configure Supabase (see SUPABASE_SETUP_GUIDE.md)
- Second error: Reduce file size or increase limit

---

### Issue 4: Form Validation Failing

**Check Django Console For**:
```python
✗ Form is INVALID
Form errors: {"email": ["This email is already registered"], ...}
  - email: ['This email is already registered']
  - roll_number: ['This roll number is already assigned']
```

**Solution**: Fix the specific field errors shown

---

### Issue 5: Email Not Sending

**Check Django Console For**:
```python
Attempting to send credentials email...
✗ Email sending error: SMTPAuthenticationError: ...
```

**Solution**: Check email configuration in `.env` file

---

## Step-by-Step Debugging Process

### 1. Open Both Consoles

**Terminal** (for Django logs):
```bash
python manage.py runserver
```

**Browser** (press F12 for developer tools):
- Go to Console tab
- Make sure "Preserve log" is checked

### 2. Fill Out the Form

Watch the browser console for:
- ✓ "Form loaded" message
- File upload confirmations when you select files

### 3. Click Submit

**In Browser Console**, you should see:
- "FORM SUBMIT EVENT TRIGGERED"
- Field validation messages
- "Validation passed, submitting form..."

**In Django Console**, you should see:
- "ADD STUDENT VIEW CALLED"
- "POST request received"
- Form validation status
- Each step of student creation

### 4. Identify Where It Fails

The logs will show exactly where the process stops:

**Example - Stops at user creation**:
```python
✓ Form is VALID
Basic Info - Name: John Doe...
Creating CustomUser object...
✗✗✗ EXCEPTION in add_student: UNIQUE constraint failed: main_app_customuser.email
```
→ **Problem**: Email already exists

**Example - Stops at document upload**:
```python
✓ Student created successfully with ID: 123
Starting document upload process...
✗ Document upload error: No module named 'supabase'
```
→ **Problem**: Supabase not installed

## Log Symbols Reference

### Backend (Django Console)

| Symbol | Meaning |
|--------|---------|
| `✓` | Success - Operation completed |
| `✓✓✓` | Major success - Full process completed |
| `✗` | Error - Operation failed |
| `✗✗✗` | Critical error - Process terminated |
| `⚠` | Warning - Non-critical issue |
| `================` | Section separator |

### Frontend (Browser Console)

| Type | Meaning |
|------|---------|
| `console.log` (black) | Informational message |
| `console.error` (red) | Error occurred |
| `console.warn` (yellow) | Warning message |

## Advanced Debugging

### Enable More Verbose Logging

In `student_management_system/settings.py`, set:

```python
DEBUG = True  # Should already be True for development

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'main_app': {
            'handlers': ['console'],
            'level': 'DEBUG',  # Changed from INFO to DEBUG
            'propagate': False,
        },
    },
}
```

### Check Database Queries

Add to Django console view:
```python
from django.db import connection
print(connection.queries)  # Shows all SQL queries executed
```

### Network Tab Debugging

In browser developer tools:
1. Go to **Network** tab
2. Check "Preserve log"
3. Submit form
4. Look for the POST request
5. Check:
   - **Status**: Should be 200 or 302
   - **Response**: Check for errors
   - **Form Data**: Verify all fields are being sent

## Quick Troubleshooting Checklist

When form doesn't work:

- [ ] Check browser console - any red errors?
- [ ] Check Django console - where does it stop?
- [ ] Are all required fields filled? (check browser console validation)
- [ ] Is form showing "Saving..." button? (means submit was triggered)
- [ ] Is Django showing "POST request received"? (means form reached server)
- [ ] Is form showing as valid? (look for "✓ Form is VALID")
- [ ] Did user creation succeed? (look for "✓ User created")
- [ ] Did student creation succeed? (look for "✓ Student created")
- [ ] Are documents uploading? (look for upload progress)
- [ ] Is email sending? (look for "✓ Email sent")
- [ ] Is redirect happening? (look for "Redirecting to...")

## Getting Help

When asking for help, provide:

1. **Browser console output** (copy the entire output)
2. **Django console output** (copy everything between the `====` separators)
3. **Steps you took** before the error
4. **Expected behavior** vs **actual behavior**

## Example Full Debug Session

```
[Browser opens form]
Browser Console:
========================================
Simplified Student Form LOADED
jQuery version: 3.6.0
Form element: 1 found
========================================
✓ All form handlers initialized successfully

[User fills form and clicks submit]
Browser Console:
========================================
FORM SUBMIT EVENT TRIGGERED
isSubmitting: false
Checking required fields...
✓ Field OK: first_name = John
✓ Field OK: last_name = Doe
...all fields validated...
✓ Validation passed, submitting form...
========================================

[Server receives request]
Django Console:
================================================================================
ADD STUDENT VIEW CALLED
Request Method: POST
POST Data: dict_keys(['first_name', 'last_name', ...])
✓ Form is VALID
Creating CustomUser object...
✓ User created successfully with ID: 156
✓ Student created successfully with ID: 201
✓ Uploaded 0 documents successfully
✓ Email sent successfully to john@example.com
✓✓✓ Student addition completed successfully!
Redirecting to manage_student...
================================================================================

[Browser shows success message and redirects]
```

## Disabling Debug Logs (Production)

When deploying to production, reduce logging:

```python
# In settings.py
DEBUG = False

LOGGING = {
    ...
    'loggers': {
        'main_app': {
            'handlers': ['console'],
            'level': 'WARNING',  # Only show warnings and errors
            'propagate': False,
        },
    },
}
```

And remove console.log statements from JavaScript (or use a minifier that removes them).

---

**With these debug logs, you can pinpoint exactly where and why the form submission fails!**



