# Supabase Storage Setup Guide for EduVision

This guide will help you set up Supabase storage for student document uploads.

## Prerequisites

- A Supabase account (sign up at https://supabase.com)
- Python environment with the EduVision project

## Step 1: Create a Supabase Project

1. Go to https://supabase.com and sign in
2. Click "New Project"
3. Fill in:
   - **Name**: EduVision Documents (or any name you prefer)
   - **Database Password**: Choose a strong password
   - **Region**: Select the closest region to your users
4. Click "Create New Project" and wait for setup to complete

## Step 2: Get Your Supabase Credentials

1. Once your project is created, go to **Project Settings** (gear icon on the left sidebar)
2. Click on **API** in the settings menu
3. You'll find:
   - **Project URL**: Copy this (e.g., `https://xxxxx.supabase.co`)
   - **Project API keys**: 
     - Copy the `anon` `public` key (for client-side access)
     - OR copy the `service_role` `secret` key (for full access - recommended for this project)

## Step 3: Configure Your Environment

1. Open or create a `.env` file in your project root
2. Add the following variables:

```env
# Supabase Storage Configuration
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=your-service-role-key-here
SUPABASE_BUCKET=student-documents
```

Replace:
- `your-project-id` with your actual Supabase project URL
- `your-service-role-key-here` with your actual service role key

## Step 4: Create the Storage Bucket

### Option A: Automatic (Recommended)
The application will automatically create the bucket when you first upload a document.

### Option B: Manual
1. Go to your Supabase dashboard
2. Click on **Storage** in the left sidebar
3. Click "Create a new bucket"
4. Fill in:
   - **Name**: `student-documents`
   - **Public bucket**: Leave unchecked (private bucket)
5. Click "Create bucket"

## Step 5: Install Required Package

Make sure the supabase package is installed:

```bash
pip install supabase==2.3.0
```

Or install all requirements:

```bash
pip install -r requirements.txt
```

## Step 6: Test the Setup

1. Start your Django development server:
```bash
python manage.py runserver
```

2. Try adding a new student with document uploads
3. Check the Supabase Storage dashboard to see if files are being uploaded

## Folder Structure in Supabase

Documents will be organized as follows:

```
student-documents/
├── photo/
│   └── student_123/
│       └── 20241024_123456_abc123.jpg
├── signature/
│   └── student_123/
│       └── 20241024_123456_def456.jpg
├── aadhaar-card/
│   └── student_123/
│       └── 20241024_123456_ghi789.pdf
├── income-certificate/
├── transfer-certificate/
└── tenth-certificate/
```

## Security Best Practices

1. **Never commit `.env` file** - It's already in `.gitignore`
2. **Use Service Role Key** - For backend operations with full access
3. **Keep Keys Secret** - Don't share your API keys publicly
4. **Regular Backups** - Supabase provides automatic backups, but consider additional backups for critical data

## Troubleshooting

### Issue: "supabase-py not installed"
**Solution**: Run `pip install supabase`

### Issue: "Supabase configuration missing"
**Solution**: Check that your `.env` file has the correct `SUPABASE_URL` and `SUPABASE_KEY` values

### Issue: "Failed to upload document"
**Solutions**:
- Verify your Supabase credentials are correct
- Check that the bucket exists
- Ensure the file size is within limits (2MB for images, 5MB for PDFs)
- Check file type is allowed (JPG, PNG, GIF for images; PDF for documents)

### Issue: "Bucket does not exist"
**Solution**: The app will try to create it automatically, but if it fails:
1. Go to Supabase dashboard → Storage
2. Manually create a bucket named `student-documents`
3. Set it as private (uncheck "Public bucket")

## File Access

To access uploaded files:

1. **For Admins/Staff**: Files are accessed via signed URLs with expiration
2. **For Students**: Files are accessed through the Django backend with permission checks

## Migration from Local Storage

If you have existing files in local storage, you'll need to:

1. Upload them manually to Supabase
2. Update the database records with new Supabase paths
3. Or keep old files locally and only use Supabase for new uploads

## Support

For Supabase-specific issues, refer to:
- Supabase Documentation: https://supabase.com/docs
- Supabase Community: https://github.com/supabase/supabase/discussions

For EduVision-specific issues, check the main README or contact your system administrator.



