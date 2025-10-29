# Render Deployment Guide for EduVision College Management System

## 🚀 Quick Start

This guide will help you deploy EduVision CMS to Render.com.

## Prerequisites

- GitHub repository with your code pushed
- Render account (sign up at https://render.com)

## Requirements Files

Choose one based on your needs:
- **`requirements.txt`** (Full) - All features including AI, analytics (~5-7 min build)
- **`requirements.minimal.txt`** (Minimal) - Essential features only (~2-3 min build)

See `REQUIREMENTS_GUIDE.md` for details.

## Deployment Steps

### 1. Create PostgreSQL Database on Render

1. Go to your Render Dashboard
2. Click **"New +"** → **"PostgreSQL"**
3. Configure:
   - **Name**: `eduvision-postgres`
   - **Database**: `eduvision`
   - **User**: `eduvision_user`
   - **Region**: Choose closest to your users
   - **Plan**: Free tier is fine to start
4. Click **"Create Database"**
5. Copy the **Internal Database URL** (format: `postgresql://user:password@hostname:port/database`)

### 2. Create Web Service on Render

1. Go to Render Dashboard
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repository
4. Configure:
   - **Name**: `eduvision-college-management`
   - **Environment**: `Python 3`
   - **Region**: Same as your database
   - **Branch**: `main` (or `development`)
   - **Root Directory**: Leave empty (root)
   - **Build Command**: 
     ```bash
     pip install -r requirements.txt && python manage.py collectstatic --noinput
     ```
   - **Start Command**: 
     ```bash
     gunicorn student_management_system.wsgi:application
     ```

### 3. Configure Environment Variables

In your Web Service settings, add these environment variables:

#### Required Variables:
```
DEBUG=False
SECRET_KEY=your-secret-key-here (generate a strong random key)
DATABASE_URL=(automatically set if database is linked)
ALLOWED_HOSTS=your-app-name.onrender.com,www.yourdomain.com
```

#### Optional Variables (for Supabase file storage):
```
SUPABASE_URL=your-supabase-url
SUPABASE_KEY=your-supabase-key
SUPABASE_BUCKET=media
```

#### Email Configuration:
```
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
EMAIL_USE_TLS=True
DEFAULT_FROM_EMAIL=EduVision <your-email@gmail.com>
```

#### CSRF Trusted Origins:
```
CSRF_TRUSTED_ORIGINS=https://your-app-name.onrender.com,https://www.yourdomain.com
```

### 4. Link Database to Web Service

1. In your Web Service settings
2. Go to **"Connections"** tab
3. Click **"Connect"** next to your PostgreSQL database
4. Render will automatically add `DATABASE_URL` environment variable

### 5. Run Migrations

After deployment, run migrations:

1. Go to your Web Service dashboard
2. Open **"Shell"** tab
3. Run:
   ```bash
   python manage.py migrate
   ```
4. (Optional) Create superuser:
   ```bash
   python manage.py createsuperuser
   ```

### 6. Create Persistent Disk for Media (Optional)

If you need persistent file storage:

1. Go to **"Disks"** section
2. Click **"Create Disk"**
3. Configure:
   - **Name**: `eduvision-media-disk`
   - **Mount Path**: `/opt/render/project/src/media`
   - **Size**: 1GB (free tier max)
4. Attach to your Web Service in **"Connections"**

## File Structure for Render

```
College-Management-System/
├── render.yaml              # Render configuration (optional)
├── Procfile                 # Process file (optional if using render.yaml)
├── build.sh                # Build script
├── requirements.txt         # Python dependencies
├── manage.py
├── student_management_system/
│   └── settings.py         # Updated for Render
└── main_app/
```

## Important Notes

1. **Static Files**: WhiteNoise is configured to serve static files in production
2. **Media Files**: Use Supabase Storage or Render Persistent Disk for file uploads
3. **Database**: Render PostgreSQL is automatically configured via `DATABASE_URL`
4. **SSL**: Render provides free SSL certificates automatically
5. **Environment**: `DEBUG=False` in production for security

## Troubleshooting

### Build Fails
- Check `requirements.txt` is correct
- Verify Python version (3.11+)
- Review build logs in Render dashboard

### Database Connection Issues
- Verify `DATABASE_URL` is set correctly
- Check database is running and accessible
- Ensure database is linked to web service

### Static Files Not Loading
- Verify `collectstatic` ran during build
- Check `STATIC_ROOT` setting
- Ensure WhiteNoise is installed

### Media Files Not Saving
- Configure Supabase Storage OR
- Create and mount persistent disk
- Update `MEDIA_ROOT` if needed

## Support

For issues:
1. Check Render build/deploy logs
2. Review Django logs in Render dashboard
3. Test locally with production settings

---

**Happy Deploying! 🎓**

