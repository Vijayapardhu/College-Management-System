# Requirements Guide

## Which requirements file should I use?

### 📦 `requirements.txt` (Full Version) - **RECOMMENDED**
Use this for complete functionality including:
- ✅ All core features
- ✅ AI analytics (Google Gemini)
- ✅ Advanced data analysis (pandas, numpy, scikit-learn)
- ✅ QR code generation
- ✅ Caching with Redis
- ✅ API documentation (Swagger)
- ✅ Email notifications
- ✅ All file formats support

**Deploy time:** ~5-7 minutes  
**Best for:** Production deployment with all features

### ⚡ `requirements.minimal.txt` (Minimal Version)
Use this for faster deployment with essential features only:
- ✅ Core Django functionality
- ✅ Basic authentication
- ✅ PDF/Excel reports
- ✅ File uploads
- ✅ Database operations
- ❌ No AI features
- ❌ No advanced analytics
- ❌ No Redis caching

**Deploy time:** ~2-3 minutes  
**Best for:** Testing, demos, or if you don't need advanced features

---

## How to use

### For Full Version (Default)
No changes needed. Render will use `requirements.txt` by default.

### For Minimal Version
1. Rename files:
   ```bash
   mv requirements.txt requirements.full.txt
   mv requirements.minimal.txt requirements.txt
   ```
2. Commit and push to GitHub
3. Deploy to Render

---

## Installing Locally

### Full Version
```bash
pip install -r requirements.txt
```

### Minimal Version
```bash
pip install -r requirements.minimal.txt
```

---

## Dependencies Breakdown

### Critical Dependencies (Always Required)
- Django 4.2.11
- gunicorn (production server)
- psycopg2-binary (PostgreSQL)
- Pillow (image processing)
- reportlab (PDF generation)
- python-decouple (environment variables)

### Optional Dependencies (Can Remove if Not Needed)
- `google-generativeai` - Remove if not using AI features
- `pandas`, `numpy`, `scikit-learn` - Remove if not using analytics
- `redis`, `django-redis` - Remove if not using caching
- `django-anymail` - Remove if using basic email only
- `qrcode` - Remove if not generating QR codes

---

## Troubleshooting

### Build Too Slow on Render?
Switch to `requirements.minimal.txt`

### Missing Feature After Deployment?
Make sure you're using `requirements.txt` (full version)

### Out of Memory During Build?
Try `requirements.minimal.txt` or upgrade Render plan

---

**Need help?** Check `RENDER_DEPLOYMENT.md` for deployment guide.

