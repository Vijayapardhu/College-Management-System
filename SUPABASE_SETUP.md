# Supabase Storage Setup Guide

## Overview
Your Django application is now configured to upload files to **Supabase Storage** instead of the local filesystem. This provides cloud storage for chat attachments, student certificates, and other documents.

## Step 1: Create Supabase Project (if you haven't already)

1. Go to [https://supabase.com](https://supabase.com) and sign up/login
2. Click "New Project"
3. Fill in your project details:
   - **Name**: College Management System (or any name)
   - **Database Password**: Choose a strong password
   - **Region**: Select closest to your users
4. Wait for the project to be created (~2 minutes)

## Step 2: Get Your Supabase Credentials

1. In your Supabase dashboard, click on **Settings** (gear icon)
2. Navigate to **API** section
3. You'll see:
   - **Project URL**: `https://xxxxxxxxxxxxx.supabase.co`
   - **API Keys**:
     - `anon` key (public) - Use this for client-side
     - `service_role` key (secret) - Use this for server-side

## Step 3: Create Storage Bucket

1. In Supabase dashboard, click on **Storage** in the left sidebar
2. Click **"New bucket"**
3. Configure:
   - **Name**: `student-documents` (or your preferred name)
   - **Public bucket**: Choose based on your needs:
     - ✅ **Public**: Files accessible via URL (good for public documents)
     - ❌ **Private**: Files require signed URLs (better for sensitive data)
4. Click **Create bucket**

## Step 4: Configure Your .env File

Create or edit the `.env` file in your project root:

```env
# Supabase Storage Configuration
SUPABASE_URL=https://xxxxxxxxxxxxx.supabase.co
SUPABASE_KEY=your-anon-or-service-role-key-here
SUPABASE_BUCKET=student-documents
```

**Important**:
- Replace `xxxxxxxxxxxxx` with your actual project ID
- Use the `anon` key for development
- For production, consider using the `service_role` key for better security
- The bucket name should match what you created in Step 3

## Step 5: Verify Setup

Run your Django server:
```bash
python manage.py runserver
```

Check the console for warnings:
- ✅ No warnings = Supabase configured correctly
- ⚠️ Warning about missing credentials = Check your .env file

## Step 6: Test File Upload

1. Login to your application
2. Go to the **Messages/Chat** section
3. Try uploading a file (image or document)
4. Check your Supabase dashboard → Storage → student-documents
5. You should see the uploaded file there!

## Folder Structure in Supabase

Files will be organized as:
```
student-documents/
├── uploads/
│   └── 20250129_143022_abc123.pdf
├── chat_attachments/
│   └── 2025/01/29/
│       └── document.pdf
└── chat_thumbnails/
    └── 2025/01/29/
        └── thumb_image.jpg
```

## Troubleshooting

### Error: "Could not find backend 'main_app.storage_backends.SupabaseStorage'"
✅ **Fixed!** - The storage backend is now properly created

### Error: "Supabase storage not available"
- Check if `SUPABASE_URL` and `SUPABASE_KEY` are set in `.env`
- Restart Django server after adding credentials
- Verify the credentials are correct in Supabase dashboard

### Files still saving locally
- Ensure `.env` file has the correct Supabase credentials
- Check that `DEFAULT_FILE_STORAGE` is set to `'main_app.storage_backends.SupabaseStorage'` in settings.py
- Restart the Django server

### Cannot access uploaded files
- **For public buckets**: Files accessible directly via URL
- **For private buckets**: URLs are signed and expire after 1 hour
- Check bucket permissions in Supabase dashboard

## Security Best Practices

1. **Never commit .env file to git** - It's already in .gitignore
2. **Use service_role key only on server-side** - Never expose in frontend
3. **Set appropriate bucket policies**:
   - Public bucket: Anyone can read
   - Private bucket: Only authenticated users can access
4. **Enable Row Level Security (RLS)** in Supabase if needed
5. **Rotate keys periodically** for production environments

## Features Now Using Supabase Storage

✅ Chat attachments (images, videos, documents)
✅ Chat thumbnails (auto-generated for images)
✅ Student certificates
✅ Any FileField in your Django models

## Benefits

- 📦 **Unlimited storage** (within your Supabase plan)
- 🚀 **Fast CDN delivery** globally
- 🔒 **Secure** with signed URLs for private files
- 💰 **Cost-effective** compared to local storage
- 📊 **Easy monitoring** via Supabase dashboard

## Support

If you encounter issues:
1. Check the Django console for error messages
2. Verify your Supabase credentials
3. Check Supabase dashboard logs
4. Ensure the bucket exists and has correct permissions

---

**Your application is now configured for Supabase storage! 🎉**


