# EduVision - Render Deployment Guide

## 🎯 Your Configuration
- **URL:** `https://eduvision.onrender.com`
- **Database:** Supabase PostgreSQL
- **Storage:** Supabase Storage
- **Platform:** Render Free Tier

---

## 📚 Documentation Files

| File | Purpose |
|------|---------|
| **`DEPLOYMENT_STEPS.md`** | ⭐ **START HERE** - Complete step-by-step guide |
| `RENDER_SETUP_SUPABASE.md` | Detailed Supabase + Render setup |
| `render-env-template.txt` | Environment variables template |
| `render.yaml` | Render configuration (auto-used) |
| `build.sh` | Build script |
| `requirements.txt` | Python dependencies |

---

## ⚡ Quick Start (5 minutes)

### 1. Get Supabase Credentials
```
✅ Database URL from Supabase → Settings → Database
✅ Project URL from Supabase → Settings → API  
✅ Anon Key from Supabase → Settings → API
✅ Create 'media' bucket in Supabase → Storage
```

### 2. Push to GitHub
```bash
git add .
git commit -m "Deploy to Render"
git push origin main
```

### 3. Deploy on Render
```
1. Go to render.com/dashboard
2. New + → Web Service
3. Connect GitHub repo
4. Name: eduvision
5. Add environment variables (see render-env-template.txt)
6. Click Create Web Service
7. Wait 3-5 minutes
```

### 4. Create Admin User
```bash
# In Render Shell:
python manage.py createsuperuser
```

### 5. Done! 🎉
Visit: `https://eduvision.onrender.com`

---

## 📋 Environment Variables Needed

Copy these to Render (replace with your values):

```
DEBUG=False
ALLOWED_HOSTS=eduvision.onrender.com
CSRF_TRUSTED_ORIGINS=https://eduvision.onrender.com
DATABASE_URL=postgresql://postgres.[YOUR-PROJECT]:[PASSWORD]@aws-0-[REGION].pooler.supabase.com:6543/postgres
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_KEY=your-supabase-anon-key
SUPABASE_BUCKET=media
```

See `render-env-template.txt` for complete list.

---

## ✅ Deployment Checklist

- [ ] Supabase project created
- [ ] Database URL copied
- [ ] Storage bucket 'media' created
- [ ] Code pushed to GitHub
- [ ] Render service created
- [ ] Environment variables added
- [ ] Deployment successful
- [ ] Superuser created
- [ ] App accessible at eduvision.onrender.com

---

## 🆘 Need Help?

### Build Failing?
→ Check `requirements.txt` is correct  
→ Review build logs in Render dashboard

### Database Error?
→ Verify DATABASE_URL format  
→ Check Supabase project is active  
→ Use connection pooler (port 6543)

### Static Files Missing?
→ Clear browser cache (Ctrl+Shift+R)  
→ Check build logs for `collectstatic` success

### File Uploads Not Working?
→ Verify SUPABASE_URL and KEY  
→ Check bucket name is exactly `media`  
→ Ensure bucket is public

---

## 📖 Full Documentation

For detailed instructions, see:
- **`DEPLOYMENT_STEPS.md`** - Step-by-step walkthrough
- **`RENDER_SETUP_SUPABASE.md`** - Comprehensive guide

---

## 🚀 Deploy Now!

**Ready?** Follow `DEPLOYMENT_STEPS.md` to deploy in 10 minutes!

Your app will be live at: **https://eduvision.onrender.com**

