# Render Deployment with Supabase (Quick Setup)

## 🚀 Your Setup
- **URL:** `https://eduvision.onrender.com`
- **Database:** Supabase PostgreSQL
- **Storage:** Supabase Storage
- **Platform:** Render (Free Tier)

---

## Step 1: Get Supabase Credentials

### Database Connection
1. Go to your Supabase project dashboard
2. Click **Settings** → **Database**
3. Copy the **Connection String** (URI format):
   ```
   postgresql://postgres.[PROJECT_ID]:[PASSWORD]@aws-0-[REGION].pooler.supabase.com:6543/postgres
   ```

### Storage Credentials
1. Go to **Settings** → **API**
2. Copy:
   - **Project URL** (e.g., `https://xxxxx.supabase.co`)
   - **anon/public API Key**
3. Make sure you have a bucket named `media` created in **Storage**

---

## Step 2: Deploy to Render

### A. Create New Web Service
1. Go to https://render.com/dashboard
2. Click **New +** → **Web Service**
3. Connect your GitHub repository
4. Configure:
   - **Name:** `eduvision` (this gives you `eduvision.onrender.com`)
   - **Environment:** Python 3
   - **Branch:** `main` (or your branch)
   - **Build Command:** 
     ```bash
     pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate --noinput
     ```
   - **Start Command:**
     ```bash
     gunicorn student_management_system.wsgi:application --bind 0.0.0.0:$PORT
     ```

### B. Add Environment Variables

Click **Advanced** → **Add Environment Variable** and add these:

#### Required Variables:
```bash
# Django Settings
DEBUG=False
SECRET_KEY=(leave it - Render auto-generates)
ALLOWED_HOSTS=eduvision.onrender.com
CSRF_TRUSTED_ORIGINS=https://eduvision.onrender.com

# Supabase Database (from Step 1)
DATABASE_URL=postgresql://postgres.[PROJECT_ID]:[PASSWORD]@aws-0-[REGION].pooler.supabase.com:6543/postgres

# Supabase Storage (from Step 1)
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_KEY=your-supabase-anon-key
SUPABASE_BUCKET=media

# Database Config (for Supabase)
DB_ENGINE=django.db.backends.postgresql
```

#### Optional - Email Configuration:
```bash
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
EMAIL_USE_TLS=True
DEFAULT_FROM_EMAIL=EduVision <your-email@gmail.com>
```

---

## Step 3: Deploy!

1. Click **Create Web Service**
2. Wait 3-5 minutes for deployment
3. Your app will be live at: `https://eduvision.onrender.com`

---

## Step 4: Create Superuser (First Time Only)

After deployment completes:

1. Go to your service dashboard
2. Click **Shell** tab
3. Run:
   ```bash
   python manage.py createsuperuser
   ```
4. Follow the prompts to create admin account

---

## 📋 Environment Variables Summary

| Variable | Value | Required |
|----------|-------|----------|
| `DEBUG` | `False` | ✅ Yes |
| `SECRET_KEY` | (auto-generated) | ✅ Yes |
| `ALLOWED_HOSTS` | `eduvision.onrender.com` | ✅ Yes |
| `CSRF_TRUSTED_ORIGINS` | `https://eduvision.onrender.com` | ✅ Yes |
| `DATABASE_URL` | Your Supabase connection string | ✅ Yes |
| `SUPABASE_URL` | Your Supabase project URL | ✅ Yes |
| `SUPABASE_KEY` | Your Supabase anon key | ✅ Yes |
| `SUPABASE_BUCKET` | `media` | ✅ Yes |
| `DB_ENGINE` | `django.db.backends.postgresql` | ✅ Yes |
| Email configs | (optional) | ❌ No |

---

## 🔧 Troubleshooting

### Database Connection Failed
- ✅ Check DATABASE_URL format is correct
- ✅ Verify password has no special characters that need escaping
- ✅ Try using "Connection Pooler" URL from Supabase (port 6543)
- ✅ Ensure your Supabase project is not paused

### Static Files Not Loading
- ✅ Check build logs - `collectstatic` should run successfully
- ✅ Verify `STATIC_URL` in settings.py
- ✅ Clear browser cache

### File Uploads Failing
- ✅ Verify SUPABASE_URL and SUPABASE_KEY are correct
- ✅ Check bucket name is `media` in Supabase Storage
- ✅ Ensure bucket is **public** or your key has access
- ✅ Check Supabase Storage policies

### Migrations Not Running
- ✅ Run manually in Shell: `python manage.py migrate`
- ✅ Check database connection works
- ✅ Look at deploy logs for errors

---

## 🎯 Post-Deployment Checklist

- [ ] App loads at `https://eduvision.onrender.com`
- [ ] Admin login works (`/admin`)
- [ ] Database connections working
- [ ] File uploads working (test with an image)
- [ ] Static files (CSS/JS) loading correctly
- [ ] Create test student/staff accounts
- [ ] Test key features (attendance, reports, etc.)

---

## 💰 Cost Breakdown

| Service | Plan | Cost |
|---------|------|------|
| Render Web Service | Free | $0/month |
| Supabase Database | Free | $0/month (500MB) |
| Supabase Storage | Free | $0/month (1GB) |
| **Total** | | **$0/month** |

**Free Tier Limits:**
- Render: 750 hours/month (enough for 1 app 24/7)
- Supabase: 500MB database, 1GB storage, 2GB bandwidth

---

## 🚀 Next Steps

1. **Custom Domain** (Optional):
   - Go to Render dashboard → Your service → Settings → Custom Domain
   - Add your domain and configure DNS

2. **Enable HTTPS** (Automatic):
   - Render provides free SSL certificates
   - Already enabled for `.onrender.com` URLs

3. **Monitor Performance**:
   - Check Render metrics dashboard
   - Set up Supabase performance monitoring

4. **Backups**:
   - Supabase auto-backs up your database daily
   - Consider exporting data regularly

---

**Your app is ready! 🎉**

Access it at: **https://eduvision.onrender.com**

