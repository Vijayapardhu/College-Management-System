"""
Digital Locker System - Document Storage & Management
Like DigiLocker but for college documents
"""

from django.db import models
from django.core.exceptions import ValidationError
import os
from datetime import datetime


# Allowed file types for each category
DOCUMENT_CATEGORIES = {
    'academic': {
        'name': 'Academic Certificates',
        'icon': 'fas fa-graduation-cap',
        'allowed_types': ['.pdf', '.jpg', '.jpeg', '.png'],
        'max_size_mb': 5,
        'examples': ['10th Certificate', '12th Marksheet', 'Degree Certificate']
    },
    'fee_receipts': {
        'name': 'Fee Receipts',
        'icon': 'fas fa-receipt',
        'allowed_types': ['.pdf', '.jpg', '.jpeg', '.png'],
        'max_size_mb': 2,
        'examples': ['Semester Fee Receipt', 'Admission Fee Receipt']
    },
    'identity': {
        'name': 'Identity Documents',
        'icon': 'fas fa-id-card',
        'allowed_types': ['.pdf', '.jpg', '.jpeg', '.png'],
        'max_size_mb': 3,
        'examples': ['Aadhar Card', 'PAN Card', 'College ID Card']
    },
    'certificates': {
        'name': 'Course Certificates',
        'icon': 'fas fa-certificate',
        'allowed_types': ['.pdf', '.jpg', '.jpeg', '.png'],
        'max_size_mb': 5,
        'examples': ['Participation Certificate', 'Achievement Certificate']
    },
    'medical': {
        'name': 'Medical Documents',
        'icon': 'fas fa-file-medical',
        'allowed_types': ['.pdf', '.jpg', '.jpeg', '.png'],
        'max_size_mb': 3,
        'examples': ['Medical Certificate', 'Vaccination Records']
    },
    'study_materials': {
        'name': 'Study Materials',
        'icon': 'fas fa-book',
        'allowed_types': ['.pdf', '.doc', '.docx', '.ppt', '.pptx', '.txt'],
        'max_size_mb': 10,
        'examples': ['Lecture Notes', 'Previous Year Papers', 'Reference Books']
    },
    'assignments': {
        'name': 'Assignments',
        'icon': 'fas fa-file-alt',
        'allowed_types': ['.pdf', '.doc', '.docx', '.zip'],
        'max_size_mb': 10,
        'examples': ['Completed Assignments', 'Project Reports']
    },
    'bonafide': {
        'name': 'Bonafide & Official',
        'icon': 'fas fa-stamp',
        'allowed_types': ['.pdf'],
        'max_size_mb': 2,
        'examples': ['Bonafide Certificate', 'Transfer Certificate', 'NOC']
    },
    'other': {
        'name': 'Other Documents',
        'icon': 'fas fa-folder',
        'allowed_types': ['.pdf', '.jpg', '.jpeg', '.png', '.doc', '.docx'],
        'max_size_mb': 5,
        'examples': ['Miscellaneous Documents']
    }
}


def validate_file_extension(file, category):
    """Validate file extension based on category"""
    ext = os.path.splitext(file.name)[1].lower()
    allowed = DOCUMENT_CATEGORIES.get(category, {}).get('allowed_types', [])
    
    if ext not in allowed:
        raise ValidationError(
            f'File type {ext} not allowed for {category}. Allowed types: {", ".join(allowed)}'
        )
    
    return True


def validate_file_size(file, category):
    """Validate file size based on category"""
    max_size_mb = DOCUMENT_CATEGORIES.get(category, {}).get('max_size_mb', 5)
    max_size_bytes = max_size_mb * 1024 * 1024
    
    if file.size > max_size_bytes:
        raise ValidationError(
            f'File size exceeds {max_size_mb}MB limit for {category}'
        )
    
    return True


def get_upload_path(instance, filename):
    """Generate secure upload path for documents"""
    # Format: documents/{student_id}/{category}/{year}/{filename}
    year = datetime.now().year
    student_id = instance.student.id if hasattr(instance, 'student') else instance.user.id
    
    # Sanitize filename
    name, ext = os.path.splitext(filename)
    safe_name = "".join(c for c in name if c.isalnum() or c in (' ', '-', '_')).strip()
    safe_filename = f"{safe_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}{ext}"
    
    return f'documents/{student_id}/{instance.category}/{year}/{safe_filename}'


def get_document_stats(user):
    """Get storage statistics for a user"""
    from main_app.models import StudentDocument
    
    docs = StudentDocument.objects.filter(student__admin=user)
    
    total_size = sum(doc.file.size for doc in docs if doc.file)
    total_count = docs.count()
    
    category_stats = {}
    for category_key, category_info in DOCUMENT_CATEGORIES.items():
        count = docs.filter(category=category_key).count()
        size = sum(doc.file.size for doc in docs.filter(category=category_key) if doc.file)
        
        category_stats[category_key] = {
            'name': category_info['name'],
            'icon': category_info['icon'],
            'count': count,
            'size_mb': round(size / (1024 * 1024), 2) if size > 0 else 0
        }
    
    return {
        'total_documents': total_count,
        'total_size_mb': round(total_size / (1024 * 1024), 2),
        'total_size_gb': round(total_size / (1024 * 1024 * 1024), 3),
        'category_stats': category_stats,
        'storage_limit_gb': 1.0,  # 1GB per student
        'storage_used_percent': min(round((total_size / (1024 * 1024 * 1024)) / 1.0 * 100, 2), 100)
    }


def search_documents(user, query, category=None, date_from=None, date_to=None):
    """Search documents with filters"""
    from main_app.models import StudentDocument
    
    docs = StudentDocument.objects.filter(student__admin=user)
    
    if query:
        docs = docs.filter(
            models.Q(title__icontains=query) |
            models.Q(description__icontains=query) |
            models.Q(tags__icontains=query)
        )
    
    if category:
        docs = docs.filter(category=category)
    
    if date_from:
        docs = docs.filter(uploaded_at__gte=date_from)
    
    if date_to:
        docs = docs.filter(uploaded_at__lte=date_to)
    
    return docs.order_by('-uploaded_at')


def share_document(document, shared_with_emails, expires_days=7):
    """Generate shareable link for document"""
    import uuid
    from datetime import timedelta
    from django.utils import timezone
    
    # Generate unique share token
    share_token = str(uuid.uuid4())
    expiry_date = timezone.now() + timedelta(days=expires_days)
    
    # Store share information
    share_data = {
        'token': share_token,
        'document_id': document.id,
        'shared_with': shared_with_emails,
        'expires_at': expiry_date.isoformat(),
        'created_at': timezone.now().isoformat()
    }
    
    return share_token, expiry_date


def verify_document_integrity(document):
    """Verify document hasn't been tampered with"""
    import hashlib
    
    if not document.file:
        return False, "No file found"
    
    try:
        # Calculate current hash
        file_hash = hashlib.sha256()
        for chunk in document.file.chunks():
            file_hash.update(chunk)
        current_hash = file_hash.hexdigest()
        
        # Compare with stored hash
        if hasattr(document, 'file_hash') and document.file_hash:
            if current_hash == document.file_hash:
                return True, "Document verified"
            else:
                return False, "Document has been modified"
        else:
            # Store hash for future verification
            document.file_hash = current_hash
            document.save()
            return True, "Hash stored for future verification"
    
    except Exception as e:
        return False, f"Verification error: {str(e)}"


def generate_document_qr(document):
    """Generate QR code for document verification"""
    import qrcode
    from io import BytesIO
    import base64
    
    # QR data includes document ID and hash for verification
    qr_data = f"DOC:{document.id}:VERIFY:{getattr(document, 'file_hash', 'NOHASH')}"
    
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(qr_data)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    qr_code_base64 = base64.b64encode(buffer.getvalue()).decode()
    
    return qr_code_base64


def bulk_download_documents(documents):
    """Create ZIP file of multiple documents"""
    import zipfile
    from io import BytesIO
    from django.http import HttpResponse
    
    zip_buffer = BytesIO()
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for doc in documents:
            if doc.file:
                try:
                    # Read file content
                    file_content = doc.file.read()
                    
                    # Add to zip with organized folder structure
                    zip_path = f"{doc.category}/{doc.title}_{doc.id}{os.path.splitext(doc.file.name)[1]}"
                    zip_file.writestr(zip_path, file_content)
                except Exception as e:
                    print(f"Error adding {doc.title} to zip: {str(e)}")
    
    zip_buffer.seek(0)
    
    response = HttpResponse(zip_buffer, content_type='application/zip')
    response['Content-Disposition'] = f'attachment; filename="documents_{datetime.now().strftime("%Y%m%d_%H%M%S")}.zip"'
    
    return response


def get_recent_activity(user, limit=10):
    """Get recent document activities"""
    from main_app.models import StudentDocument
    
    recent_docs = StudentDocument.objects.filter(
        student__admin=user
    ).order_by('-uploaded_at')[:limit]
    
    activities = []
    for doc in recent_docs:
        activities.append({
            'type': 'upload',
            'document': doc,
            'timestamp': doc.uploaded_at,
            'description': f"Uploaded {doc.title}"
        })
    
    return activities


def organize_documents_by_year(user):
    """Organize documents by academic year"""
    from main_app.models import StudentDocument
    from collections import defaultdict
    
    docs = StudentDocument.objects.filter(student__admin=user).order_by('-uploaded_at')
    
    organized = defaultdict(list)
    
    for doc in docs:
        year = doc.uploaded_at.year
        organized[year].append(doc)
    
    return dict(organized)
















