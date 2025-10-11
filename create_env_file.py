"""
Script to create .env file for EduVision
Run this script to create your own .env file with custom settings
"""

def create_env_file():
    env_content = """# Django Settings
SECRET_KEY=MySecretKey123!
DEBUG=True
ALLOWED_HOSTS=*

# Database Configuration (Supabase PostgreSQL)
DB_ENGINE=django.db.backends.postgresql
DB_NAME=postgres
DB_USER=postgres.yqwszaekwucrnnjuadtp
DB_PASSWORD=oiXsUCnflSlzH7zH
DB_HOST=aws-1-ap-south-1.pooler.supabase.com
DB_PORT=6543
DB_SSL_MODE=require

# Email Configuration (Gmail SMTP for OTP)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=23404.cms@gmail.com
EMAIL_HOST_PASSWORD=tqocekqesdmzgjnx
DEFAULT_FROM_EMAIL=EduVision <23404.cms@gmail.com>

# Optional: Database URL (for deployment)
# DATABASE_URL=postgresql://postgres.yqwszaekwucrnnjuadtp:oiXsUCnflSlzH7zH@aws-1-ap-south-1.pooler.supabase.com:6543/postgres
"""
    
    try:
        with open('.env', 'w') as f:
            f.write(env_content)
        print("✅ .env file created successfully!")
        print("\n📧 Gmail SMTP Configuration:")
        print("   Email: 23404.cms@gmail.com")
        print("   Status: Configured and ready")
        print("\n🔐 OTP Authentication:")
        print("   OTP emails will be sent from: 23404.cms@gmail.com")
        print("\n⚠️  Note: .env file is in .gitignore and won't be committed to Git")
    except Exception as e:
        print(f"❌ Error creating .env file: {e}")

if __name__ == '__main__':
    create_env_file()

