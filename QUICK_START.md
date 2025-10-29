# 🚀 Quick Start - Deploy to Render in 10 Minutes

## Step 1: Clean Up (Optional)
```bash
# Remove duplicate directory if exists
Remove-Item -Recurse -Force "student-management-using-django"
```

## Step 2: Commit to GitHub
```bash
git add .
git commit -m "Ready for Render deployment"
git push origin main
```

## Step 3: Create Render Account
1. Go to https://render.com
2. Sign up with GitHub

## Step 4: Create PostgreSQL Database
1. Dashboard → **New +** → **PostgreSQL**
2. Name: `eduvision-db`
3. Click **Create Database**
4. Copy the **Internal Database URL**

## Step 5: Create Web Service
1. Dashboard → **New +** → **Web Service**
2. Connect your GitHub repo
3. Settings:
   - **Name**: `eduvision-cms`
   - **Build Command**: 
     ```
     pip install -r requirements.txt && python manage.py collectstatic --noinput
     ```
   - **Start Command**: 
     ```
     gunicorn student_management_system.wsgi:application
     ```

## Step 6: Add Environment Variables
Click **Environment** tab and add:

```
DEBUG=False
SECRET_KEY=(auto-generated - leave as is)
ALLOWED_HOSTS=your-app-name.onrender.com
CSRF_TRUSTED_ORIGINS=https://your-app-name.onrender.com
```

## Step 7: Link Database
1. Go to **Environment** tab
2. Click **Add from Database**
3. Select your PostgreSQL database
4. Variable name: `DATABASE_URL`

## Step 8: Deploy!
1. Click **Create Web Service**
2. Wait 5-7 minutes for deployment
3. Your app will be live at: `https://your-app-name.onrender.com`

## Step 9: Run Migrations
1. Go to your Web Service dashboard
2. Click **Shell** tab
3. Run:
```bash
python manage.py migrate
python manage.py createsuperuser
```

## ✅ Done!
Access your app at: `https://your-app-name.onrender.com`

---

**Detailed Guide:** See `RENDER_DEPLOYMENT.md`  
**Requirements Help:** See `REQUIREMENTS_GUIDE.md`  
**Troubleshooting:** Check deployment logs in Render dashboard

