# Quick Installation Guide - Simplified Student Form

Follow these steps to get the new simplified student form working.

## Step 1: Install Required Package

```bash
pip install supabase==2.3.0
```

Or install all requirements:

```bash
pip install -r requirements.txt
```

## Step 2: Configure Supabase

### Get Supabase Credentials:

1. Sign up at https://supabase.com (if you don't have an account)
2. Create a new project
3. Go to Project Settings → API
4. Copy your:
   - Project URL (e.g., `https://xxxxx.supabase.co`)
   - Service Role Key (secret key for backend)

### Update .env File:

Add these lines to your `.env` file:

```env
# Supabase Storage Configuration
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=your-service-role-key-here
SUPABASE_BUCKET=student-documents
```

Replace with your actual values.

**If `.env` file doesn't exist**, create it in the project root directory.

## Step 3: Run Migrations (Optional)

If you've made any database changes:

```bash
python manage.py makemigrations
python manage.py migrate
```

## Step 4: Start the Server

```bash
python manage.py runserver
```

## Step 5: Test the Form

1. Open your browser and go to: `http://127.0.0.1:8000`
2. Login as HOD/Admin
3. Go to "Add Student" or "Student Management"
4. You should see the new simplified form with 4 sections

## Step 6: Add a Test Student

Try adding a student with:
- **Basic Info**: Name, email, DOB, gender, mobile
- **Academic**: Course, session, roll number
- **Parents**: Father/mother names and contacts
- **Documents**: Upload a test photo or PDF

The system should:
- Create the student account
- Upload documents to Supabase
- Send an email with login credentials
- Show success message with temporary password

## Step 7: Test Dual Login

1. Logout
2. Try logging in with the **roll number** you assigned
3. Try logging in with the **email address**
4. Both should work with the same password

## Troubleshooting

### Error: "supabase module not found"
```bash
pip install supabase==2.3.0
```

### Error: "Supabase configuration missing"
- Check your `.env` file has `SUPABASE_URL` and `SUPABASE_KEY`
- Make sure there are no extra spaces
- Restart the Django server after updating `.env`

### Error: "Template does not exist"
- Make sure `student_form_simple.html` is in `main_app/templates/forms/`
- Clear any cached templates
- Restart the server

### Error: "No module named 'main_app.auth_backends'"
- Make sure `auth_backends.py` exists in `main_app/`
- Check that it's not named `auth_backend.py` (without 's')
- Restart the server

### Documents not uploading
- Verify Supabase credentials are correct
- Check that file size is within limits
- Check browser console for JavaScript errors
- Make sure bucket exists (app creates it automatically)

### Email not sending
- Check email configuration in `.env`:
  ```env
  EMAIL_HOST_USER=your-email@gmail.com
  EMAIL_HOST_PASSWORD=your-app-password
  ```
- For Gmail, use an app password, not your regular password
- Enable "Less secure app access" or use 2FA with app password

## What's Different?

### Old Form:
- 80+ fields
- Username field required
- Manual password entry
- Local file storage
- Complex UI with many collapsible sections

### New Form:
- 20 essential fields
- No username (uses email internally)
- Auto-generated secure passwords
- Supabase cloud storage
- Clean, simple 4-section UI

## Need Help?

Refer to:
- `SIMPLIFIED_STUDENT_FORM_IMPLEMENTATION.md` - Complete implementation details
- `SUPABASE_SETUP_GUIDE.md` - Detailed Supabase setup
- Django logs in console for error messages

## Quick Commands Reference

```bash
# Install dependencies
pip install -r requirements.txt

# Run server
python manage.py runserver

# Create superuser (if needed)
python manage.py createsuperuser

# Check for issues
python manage.py check

# Clear cache (if needed)
python manage.py collectstatic --clear
```

## Success Indicators

✅ Server starts without errors
✅ Can access add student form
✅ Form has only 4 sections (Basic, Academic, Parents, Documents)
✅ No username field visible
✅ Can add student successfully
✅ Documents upload to Supabase
✅ Email sent with credentials
✅ Can login with roll number
✅ Can login with email

## Next Steps

After successful installation:

1. **Test thoroughly** - Try all form features
2. **Configure Supabase** - Set up proper bucket policies
3. **Test on mobile** - Form is responsive
4. **Train users** - Show HOD/Admin the new interface
5. **Monitor** - Check for any issues in first few days

## Important Notes

- ⚠️ Keep `.env` file secure and never commit it to Git
- ⚠️ Backup database before major updates
- ⚠️ Test in development before using in production
- ⚠️ Existing students are not affected - data remains intact

## Production Deployment

Before deploying to production:

1. Set `DEBUG = False` in settings
2. Configure proper `ALLOWED_HOSTS`
3. Set up HTTPS for secure file uploads
4. Configure production email service
5. Set up regular Supabase backups
6. Test all functionality on staging server

---

**Installation Complete!** 🎉

You now have a simplified, efficient student management system with cloud storage.



