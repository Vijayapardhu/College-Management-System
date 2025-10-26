# Create Your .env File - IMMEDIATE ACTION REQUIRED

## Your Supabase Project is Already Set Up!

You're already using Supabase PostgreSQL database at:
- Project ID: `yqwszaekwucrnnjuadtp`
- Region: `aws-1-ap-south-1`

You just need to add the **Storage API key** to enable file uploads!

---

## ⚡ Quick Setup (2 Minutes)

### Step 1: Get Your Supabase API Key

1. Go to: https://supabase.com/dashboard
2. Log in
3. Select your project: **yqwszaekwucrnnjuadtp**
4. Click **Settings** (gear icon) → **API**
5. Scroll down to find: **"service_role" key**
6. Click "Copy" or "Reveal" to see the key
7. It looks like: `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...` (very long string)

### Step 2: Create .env File

Create a file named `.env` (exactly, with the dot) in your project root:
```
C:\Users\PARDHU\Desktop\projects\College-Management-System\.env
```

### Step 3: Paste This Content Into .env

Copy everything below and paste into your `.env` file:

```env
# Django Settings
SECRET_KEY=MySecretKey123!
DEBUG=True
ALLOWED_HOSTS=*

# Database Configuration (Supabase PostgreSQL) - ALREADY WORKING
DB_ENGINE=django.db.backends.postgresql
DB_NAME=postgres
DB_USER=postgres.yqwszaekwucrnnjuadtp
DB_PASSWORD=oiXsUCnflSlzH7zH
DB_HOST=aws-1-ap-south-1.pooler.supabase.com
DB_PORT=6543
DB_SSL_MODE=require

# Email Configuration
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=23404.cms@gmail.com
EMAIL_HOST_PASSWORD=tqocekqesdmzgjnx

# Supabase Storage Configuration (for file uploads)
SUPABASE_URL=https://yqwszaekwucrnnjuadtp.supabase.co
SUPABASE_KEY=PASTE_YOUR_SERVICE_ROLE_KEY_HERE
SUPABASE_BUCKET=student-documents
```

### Step 4: Replace the Key

In the `.env` file you just created, replace:
```env
SUPABASE_KEY=PASTE_YOUR_SERVICE_ROLE_KEY_HERE
```

With:
```env
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.your-actual-key-here...
```

### Step 5: Restart Django Server

```bash
# Stop the server (Ctrl+C)
# Then restart:
python manage.py runserver
```

---

## ✅ That's It!

Your Supabase Storage is now configured and ready to use!

---

## 🧪 Test It

1. Go to Add Student page
2. Fill required fields
3. Upload a photo
4. Click Save
5. **Check Django console** for:
   ```
   ✓ Supabase storage initialized
   ✓ photo uploaded successfully
   ```

---

## ❓ Can't Find Service Role Key?

### Alternative: Use Anon Key (Less Secure but Works)

If you can't find the service_role key:

1. In Supabase Dashboard → Settings → API
2. Copy the **"anon" "public"** key instead
3. Use that as `SUPABASE_KEY`

Note: The anon key has limited permissions, but will work for testing.

---

## 🚨 IMPORTANT: .env File Security

**NEVER** commit `.env` file to Git!
- It's already in `.gitignore`
- Contains sensitive credentials
- Keep it secret!

---

## Still Not Working?

Run this command and share the output:

```bash
python -c "from decouple import config; print('SUPABASE_URL:', config('SUPABASE_URL', default='NOT SET')); print('SUPABASE_KEY:', 'SET' if config('SUPABASE_KEY', default='') else 'NOT SET')"
```

This will tell us if the .env file is being read correctly.

---

**Once you add the SUPABASE_KEY, the file uploads will work! 🎉**



