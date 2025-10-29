# 🚀 Deployment Steps - Render + Supabase

## Quick Checklist

- [ ] Supabase project created
- [ ] Supabase credentials ready
- [ ] GitHub repository pushed
- [ ] Render account created
- [ ] Ready to deploy!

---

## 📝 Step-by-Step Guide

### 1️⃣ Prepare Supabase

#### A. Get Database URL
1. Go to https://supabase.com/dashboard
2. Select your project
3. Go to **Settings** → **Database**
4. Scroll to **Connection String**
5. Copy the **URI** (with pooler):
   ```
   postgresql://postgres.[PROJECT]:[PASSWORD]@aws-0-[REGION].pooler.supabase.com:6543/postgres
   ```
   **Important:** Replace `[PASSWORD]` with your actual database password

#### B. Get Storage Credentials
1. Go to **Settings** → **API**
2. Copy:
   - **Project URL** (e.g., `https://abcdefgh.supabase.co`)
   - **anon public** key

#### C. Create Media Bucket
1. Go to **Storage** → **Buckets**
2. Click **New Bucket**
3. Name: `media`
4. Make it **Public** (or configure policies)
5. Click **Create Bucket**

---

### 2️⃣ Push to GitHub

```bash
# Make sure all files are committed
git add .
git commit -m "Ready for Render deployment with Supabase"
git push origin main
```

---

### 3️⃣ Deploy to Render

#### A. Create Web Service
1. Go to https://render.com/dashboard
2. Click **New +** → **Web Service**
3. Click **Connect GitHub** (if first time)
4. Select your repository: `College-Management-System`

#### B. Configure Service
Fill in these settings:

| Setting | Value |
|---------|-------|
| **Name** | `eduvision` |
| **Region** | Choose closest to you |
| **Branch** | `main` |
| **Root Directory** | (leave empty) |
| **Environment** | `Python 3` |
| **Build Command** | `pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate --noinput` |
| **Start Command** | `gunicorn student_management_system.wsgi:application --bind 0.0.0.0:$PORT` |

#### C. Add Environment Variables

Click **Advanced** → **Add Environment Variable**

**Copy these from `.env.render` file and paste your actual values:**

```
DEBUG=False
ALLOWED_HOSTS=eduvision.onrender.com
CSRF_TRUSTED_ORIGINS=https://eduvision.onrender.com

DATABASE_URL=postgresql://postgres.[YOUR-PROJECT]:[YOUR-PASSWORD]@aws-0-[REGION].pooler.supabase.com:6543/postgres
DB_ENGINE=django.db.backends.postgresql

SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_KEY=your-supabase-anon-key
SUPABASE_BUCKET=media
```

**Leave SECRET_KEY empty** - Render will auto-generate it

#### D. Deploy!
1. Click **Create Web Service**
2. Wait 3-5 minutes for build and deployment
3. Watch the logs for any errors

---

### 4️⃣ First-Time Setup

Once deployment is complete:

#### A. Create Superuser
1. Go to your service dashboard on Render
2. Click **Shell** tab (top right)
3. Wait for shell to connect
4. Run:
   ```bash
   python manage.py createsuperuser
   ```
5. Enter:
   - Username (e.g., `admin`)
   - Email
   - Password (twice)

#### B. Test Your App
1. Visit: `https://eduvision.onrender.com`
2. Should see the login page
3. Try logging in with superuser credentials

---

## 🔍 Verification Checklist

After deployment, verify:

- [ ] ✅ App loads at `https://eduvision.onrender.com`
- [ ] ✅ No error messages on homepage
- [ ] ✅ Static files (CSS/JS) are loading
- [ ] ✅ Can login to admin panel (`/admin`)
- [ ] ✅ Can create a test student
- [ ] ✅ File uploads work (test profile picture)
- [ ] ✅ Database is working (data persists after page reload)

---

## 🐛 Common Issues & Fixes

### Issue 1: "DisallowedHost" Error
**Fix:** Add to environment variables:
```
ALLOWED_HOSTS=eduvision.onrender.com,.onrender.com
```

### Issue 2: Database Connection Failed
**Fix:** 
- Verify DATABASE_URL has correct format
- Check password doesn't contain special characters
- Use connection pooler URL (port 6543)
- Verify Supabase project is active

### Issue 3: Static Files Not Loading (404)
**Fix:**
- Check build logs for `collectstatic` success
- Make sure `whitenoise` is in requirements.txt
- Clear browser cache (Ctrl+Shift+R)

### Issue 4: File Uploads Failing
**Fix:**
- Verify SUPABASE_URL and SUPABASE_KEY
- Check bucket name is exactly `media`
- Ensure bucket is public or has correct policies
- Test Supabase credentials in their dashboard

### Issue 5: App Sleeping/Slow First Load
**Explanation:** Render free tier sleeps after inactivity
**Fix:** 
- First request takes 30-60 seconds (normal)
- Upgrade to paid plan for always-on
- Or use cron-job.org to ping your app every 10 minutes

---

## 📊 Monitor Your App

### View Logs
1. Go to your service dashboard
2. Click **Logs** tab
3. Watch real-time logs

### Check Metrics
1. Go to your service dashboard
2. Click **Metrics** tab
3. See CPU, Memory, Request stats

### Supabase Monitoring
1. Go to Supabase dashboard
2. Click **Database** → **Reports**
3. Monitor database size and connections

---

## 🔄 Update Deployment

When you push new code:

1. Commit and push to GitHub:
   ```bash
   git add .
   git commit -m "Your update message"
   git push origin main
   ```

2. Render auto-deploys (wait 2-3 minutes)

3. Check logs for successful deployment

---

## 💡 Pro Tips

1. **Auto-Deploy**: Enabled by default - push to main = auto deploy
2. **Manual Deploy**: Dashboard → **Manual Deploy** → **Deploy latest commit**
3. **Environment Variables**: Can update anytime without rebuild
4. **Logs**: Download logs from dashboard for debugging
5. **Shell Access**: Use for running management commands
6. **Free Tier**: 750 hours/month = one app running 24/7

---

## 📞 Get Help

- **Render Docs**: https://render.com/docs
- **Supabase Docs**: https://supabase.com/docs
- **Django Docs**: https://docs.djangoproject.com

---

## ✅ You're Done!

Your app is live at: **https://eduvision.onrender.com**

Enjoy your deployment! 🎉

