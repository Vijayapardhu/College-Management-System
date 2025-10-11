# EduVision Setup Guide

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- Git

### Installation Steps

1. **Clone the repository**
   ```bash
   git clone https://github.com/Vijayapardhu/College-Management-System.git
   cd College-Management-System
   ```

2. **Create a virtual environment (recommended)**
   ```bash
   python -m venv venv
   
   # On Windows:
   venv\Scripts\activate
   
   # On Mac/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Configuration (Optional)**
   
   The application works out-of-the-box with default settings, but you can customize by creating a `.env` file:
   
   ```bash
   # Copy the template
   cp env_template.txt .env
   
   # Edit .env with your preferred settings
   ```
   
   See `env_template.txt` for all available configuration options.

5. **Run migrations** (Only needed if using a fresh database)
   ```bash
   python manage.py migrate
   ```

6. **Start the development server**
   ```bash
   python manage.py runserver
   ```

7. **Access the application**
   
   Open your browser and navigate to: `http://127.0.0.1:8000/`

## 🔐 Default Admin Credentials

```
📧 Email: admin@eduvision.com
🔑 Password: admin123
```

**⚠️ IMPORTANT:** Change the default password immediately after first login!

## 🗄️ Database Configuration

### Current Setup: Supabase PostgreSQL (Cloud Database)

The application is currently configured to use **Supabase PostgreSQL** cloud database. This means:
- ✅ Your data is stored securely in the cloud
- ✅ Database is accessible from anywhere
- ✅ Automatic backups and scaling
- ✅ No local database setup required

### Switching to SQLite (Local Development)

If you prefer to use a local SQLite database for development:

1. Create a `.env` file (or edit existing one)
2. Add this line:
   ```
   DB_ENGINE=django.db.backends.sqlite3
   ```
3. Run migrations:
   ```bash
   python manage.py migrate
   ```
4. Create a new admin user:
   ```bash
   python manage.py createsuperuser
   ```

### Using Your Own PostgreSQL Database

To use a different PostgreSQL database, update these values in your `.env` file:

```env
DB_ENGINE=django.db.backends.postgresql
DB_NAME=your_database_name
DB_USER=your_username
DB_PASSWORD=your_password
DB_HOST=your_host
DB_PORT=5432
DB_SSL_MODE=require  # or 'disable' for local databases
```

## 📧 Email Configuration

To enable email notifications, configure these settings in `.env`:

```env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

**For Gmail:**
1. Enable 2-Factor Authentication
2. Generate an App Password: https://myaccount.google.com/apppasswords
3. Use the App Password (not your regular password)

## 🛠️ Common Commands

### Create a new admin user
```bash
python manage.py shell
```
Then in the Python shell:
```python
from main_app.models import CustomUser, Admin
user = CustomUser.objects.create_user(
    email='newemail@example.com',
    password='yourpassword',
    user_type=1,
    first_name='Admin',
    last_name='User'
)
admin = Admin.objects.create(admin=user)
print(f"Admin created: {user.email}")
exit()
```

### Reset admin password
```bash
python manage.py shell
```
Then:
```python
from main_app.models import CustomUser
user = CustomUser.objects.get(email='admin@eduvision.com')
user.set_password('newpassword')
user.save()
print("Password updated!")
exit()
```

### Collect static files (for production)
```bash
python manage.py collectstatic
```

### Check for issues
```bash
python manage.py check
```

### View database migrations
```bash
python manage.py showmigrations
```

## 🌐 Production Deployment

### Environment Variables for Production

Create a `.env` file with production settings:

```env
DEBUG=False
SECRET_KEY=your-super-secret-key-here-change-this
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Database (Use your production database credentials)
DB_ENGINE=django.db.backends.postgresql
DB_NAME=production_db
DB_USER=prod_user
DB_PASSWORD=strong_password
DB_HOST=your-db-host
DB_PORT=5432
DB_SSL_MODE=require

# Email
EMAIL_HOST_USER=notifications@yourdomain.com
EMAIL_HOST_PASSWORD=app-specific-password
```

### Security Checklist

Before deploying to production:

- [ ] Set `DEBUG=False`
- [ ] Change `SECRET_KEY` to a strong random string
- [ ] Set `ALLOWED_HOSTS` to your domain
- [ ] Change default admin password
- [ ] Configure proper email settings
- [ ] Set up HTTPS/SSL certificate
- [ ] Configure proper database backups
- [ ] Review and restrict database access
- [ ] Set up monitoring and logging

### Deployment Platforms

The application can be deployed to:
- **Heroku**: Use the included `Procfile` (if present)
- **Railway**: Supports automatic deployment
- **Render**: Easy PostgreSQL integration
- **DigitalOcean App Platform**: Full control
- **AWS/GCP/Azure**: For enterprise deployments

## 🔧 Troubleshooting

### Database Connection Errors

If you see database connection errors:

1. Check your database credentials in `.env`
2. Ensure the database server is running
3. Verify network connectivity to the database host
4. Check if SSL is required: set `DB_SSL_MODE=require` or `disable`

### Migration Errors

If migrations fail:

```bash
# View migration status
python manage.py showmigrations

# Try migrating specific app
python manage.py migrate main_app

# Reset migrations (⚠️ DATA LOSS - dev only)
python manage.py migrate main_app zero
python manage.py migrate
```

### Static Files Not Loading

```bash
# Collect static files
python manage.py collectstatic --noinput

# Check STATIC_ROOT setting
python manage.py check
```

### Import Errors

If you see `ModuleNotFoundError`:

```bash
# Reinstall all dependencies
pip install -r requirements.txt --upgrade
```

## 📞 Support

For issues or questions:
- Check the main README.md for feature documentation
- Review the codebase documentation
- Contact the development team

## 🎯 Next Steps After Setup

1. **Login** with default admin credentials
2. **Change the password** immediately
3. **Add Departments** (required for courses)
4. **Add Courses** 
5. **Add Subjects**
6. **Add Staff** members
7. **Add Students**
8. **Start using the system!**

---

**Happy Managing! 🎓**

