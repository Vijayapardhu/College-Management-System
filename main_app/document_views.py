"""
Document Management Views - Digital Locker System
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, FileResponse, JsonResponse
from django.db.models import Q
from django.core.paginator import Paginator
from django.utils import timezone
from datetime import datetime, timedelta

from main_app.models import Student, StudentDocument, CustomUser
from main_app.document_locker import (
    DOCUMENT_CATEGORIES,
    validate_file_extension,
    validate_file_size,
    get_document_stats,
    search_documents,
    verify_document_integrity,
    generate_document_qr,
    bulk_download_documents,
    get_recent_activity,
    organize_documents_by_year
)


# ==================== STUDENT DIGITAL LOCKER ====================

@login_required(login_url='/')
def student_document_locker(request):
    """Main digital locker dashboard for students"""
    try:
        student = Student.objects.get(admin=request.user)
    except Student.DoesNotExist:
        messages.error(request, 'Student profile not found')
        return redirect('student_home')
    
    # Get statistics
    stats = get_document_stats(request.user)
    
    # Get recent documents
    recent_docs = StudentDocument.objects.filter(student=student).order_by('-uploaded_at')[:5]
    
    # Get documents by category
    category_counts = {}
    for category_key in DOCUMENT_CATEGORIES.keys():
        count = StudentDocument.objects.filter(student=student, category=category_key).count()
        category_counts[category_key] = count
    
    # Get recent activity
    activities = get_recent_activity(request.user, limit=5)
    
    context = {
        'page_title': 'My Digital Locker',
        'student': student,
        'stats': stats,
        'recent_docs': recent_docs,
        'categories': DOCUMENT_CATEGORIES,
        'category_counts': category_counts,
        'activities': activities
    }
    
    return render(request, 'student_template/document_locker/dashboard.html', context)


@login_required(login_url='/')
def view_documents_by_category(request, category):
    """View all documents in a specific category"""
    try:
        student = Student.objects.get(admin=request.user)
    except Student.DoesNotExist:
        messages.error(request, 'Student profile not found')
        return redirect('student_home')
    
    if category not in DOCUMENT_CATEGORIES:
        messages.error(request, 'Invalid category')
        return redirect('student_document_locker')
    
    # Get documents in category
    documents = StudentDocument.objects.filter(
        student=student,
        category=category
    ).order_by('-uploaded_at')
    
    # Pagination
    paginator = Paginator(documents, 12)  # 12 documents per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    category_info = DOCUMENT_CATEGORIES[category]
    
    context = {
        'page_title': f'{category_info["name"]} - Digital Locker',
        'student': student,
        'category': category,
        'category_info': category_info,
        'documents': page_obj,
        'total_docs': documents.count()
    }
    
    return render(request, 'student_template/document_locker/category_view.html', context)


@login_required(login_url='/')
def upload_document(request):
    """Upload a new document to digital locker"""
    try:
        student = Student.objects.get(admin=request.user)
    except Student.DoesNotExist:
        messages.error(request, 'Student profile not found')
        return redirect('student_home')
    
    if request.method == 'POST':
        try:
            title = request.POST.get('title')
            description = request.POST.get('description', '')
            category = request.POST.get('category')
            tags = request.POST.get('tags', '')
            file = request.FILES.get('file')
            is_important = request.POST.get('is_important') == 'on'
            
            # Validation
            if not all([title, category, file]):
                messages.error(request, 'Please provide title, category, and file')
                return redirect('upload_document')
            
            if category not in DOCUMENT_CATEGORIES:
                messages.error(request, 'Invalid category selected')
                return redirect('upload_document')
            
            # Validate file
            try:
                validate_file_extension(file, category)
                validate_file_size(file, category)
            except Exception as e:
                messages.error(request, str(e))
                return redirect('upload_document')
            
            # Check storage limit (1GB per student)
            stats = get_document_stats(request.user)
            if stats['total_size_gb'] >= 1.0:
                messages.error(request, 'Storage limit exceeded! Please delete some documents.')
                return redirect('student_document_locker')
            
            # Create document
            import hashlib
            file_hash = hashlib.sha256()
            for chunk in file.chunks():
                file_hash.update(chunk)
            
            doc = StudentDocument.objects.create(
                student=student,
                title=title,
                description=description,
                category=category,
                file=file,
                tags=tags,
                is_important=is_important,
                file_hash=file_hash.hexdigest()
            )
            
            messages.success(request, f'Document "{title}" uploaded successfully!')
            return redirect('view_documents_by_category', category=category)
            
        except Exception as e:
            messages.error(request, f'Error uploading document: {str(e)}')
            return redirect('upload_document')
    
    # GET request - show form
    context = {
        'page_title': 'Upload Document',
        'student': student,
        'categories': DOCUMENT_CATEGORIES
    }
    
    return render(request, 'student_template/document_locker/upload.html', context)


@login_required(login_url='/')
def view_document_detail(request, document_id):
    """View detailed information about a document"""
    try:
        student = Student.objects.get(admin=request.user)
        document = get_object_or_404(StudentDocument, id=document_id, student=student)
    except Student.DoesNotExist:
        messages.error(request, 'Student profile not found')
        return redirect('student_home')
    
    # Verify document integrity
    is_verified, verify_message = verify_document_integrity(document)
    
    # Generate QR code
    qr_code = generate_document_qr(document)
    
    # Get file info
    file_size_mb = round(document.file.size / (1024 * 1024), 2) if document.file else 0
    file_extension = document.file.name.split('.')[-1].upper() if document.file else 'N/A'
    
    context = {
        'page_title': f'Document Details - {document.title}',
        'student': student,
        'document': document,
        'is_verified': is_verified,
        'verify_message': verify_message,
        'qr_code': qr_code,
        'file_size_mb': file_size_mb,
        'file_extension': file_extension,
        'category_info': DOCUMENT_CATEGORIES.get(document.category, {})
    }
    
    return render(request, 'student_template/document_locker/detail.html', context)


@login_required(login_url='/')
def download_document(request, document_id):
    """Download a document"""
    try:
        student = Student.objects.get(admin=request.user)
        document = get_object_or_404(StudentDocument, id=document_id, student=student)
    except Student.DoesNotExist:
        messages.error(request, 'Access denied')
        return redirect('student_home')
    
    if not document.file:
        messages.error(request, 'File not found')
        return redirect('student_document_locker')
    
    try:
        response = FileResponse(document.file.open('rb'))
        response['Content-Type'] = 'application/octet-stream'
        response['Content-Disposition'] = f'attachment; filename="{document.title}.{document.file.name.split(".")[-1]}"'
        return response
    except Exception as e:
        messages.error(request, f'Error downloading file: {str(e)}')
        return redirect('student_document_locker')


@login_required(login_url='/')
def delete_document(request, document_id):
    """Delete a document"""
    try:
        student = Student.objects.get(admin=request.user)
        document = get_object_or_404(StudentDocument, id=document_id, student=student)
    except Student.DoesNotExist:
        messages.error(request, 'Access denied')
        return redirect('student_home')
    
    if request.method == 'POST':
        category = document.category
        title = document.title
        
        # Delete file from storage
        if document.file:
            document.file.delete()
        
        # Delete database entry
        document.delete()
        
        messages.success(request, f'Document "{title}" deleted successfully')
        return redirect('view_documents_by_category', category=category)
    
    context = {
        'page_title': 'Delete Document',
        'student': student,
        'document': document
    }
    
    return render(request, 'student_template/document_locker/delete_confirm.html', context)


@login_required(login_url='/')
def search_my_documents(request):
    """Search documents with filters"""
    try:
        student = Student.objects.get(admin=request.user)
    except Student.DoesNotExist:
        messages.error(request, 'Student profile not found')
        return redirect('student_home')
    
    query = request.GET.get('q', '')
    category = request.GET.get('category', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    
    # Parse dates
    date_from_obj = datetime.strptime(date_from, '%Y-%m-%d').date() if date_from else None
    date_to_obj = datetime.strptime(date_to, '%Y-%m-%d').date() if date_to else None
    
    # Search
    documents = search_documents(
        user=request.user,
        query=query,
        category=category if category else None,
        date_from=date_from_obj,
        date_to=date_to_obj
    )
    
    # Pagination
    paginator = Paginator(documents, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_title': 'Search Documents',
        'student': student,
        'documents': page_obj,
        'query': query,
        'selected_category': category,
        'date_from': date_from,
        'date_to': date_to,
        'categories': DOCUMENT_CATEGORIES,
        'total_results': documents.count()
    }
    
    return render(request, 'student_template/document_locker/search.html', context)


@login_required(login_url='/')
def bulk_download_my_documents(request):
    """Download multiple documents as ZIP"""
    try:
        student = Student.objects.get(admin=request.user)
    except Student.DoesNotExist:
        messages.error(request, 'Access denied')
        return redirect('student_home')
    
    if request.method == 'POST':
        document_ids = request.POST.getlist('document_ids')
        
        if not document_ids:
            messages.error(request, 'No documents selected')
            return redirect('student_document_locker')
        
        documents = StudentDocument.objects.filter(
            id__in=document_ids,
            student=student
        )
        
        if not documents.exists():
            messages.error(request, 'No valid documents found')
            return redirect('student_document_locker')
        
        return bulk_download_documents(documents)
    
    return redirect('student_document_locker')


@login_required(login_url='/')
def view_important_documents(request):
    """View documents marked as important"""
    try:
        student = Student.objects.get(admin=request.user)
    except Student.DoesNotExist:
        messages.error(request, 'Student profile not found')
        return redirect('student_home')
    
    documents = StudentDocument.objects.filter(
        student=student,
        is_important=True
    ).order_by('-uploaded_at')
    
    context = {
        'page_title': 'Important Documents',
        'student': student,
        'documents': documents
    }
    
    return render(request, 'student_template/document_locker/important.html', context)


@login_required(login_url='/')
def toggle_important(request, document_id):
    """Toggle important flag on document"""
    try:
        student = Student.objects.get(admin=request.user)
        document = get_object_or_404(StudentDocument, id=document_id, student=student)
    except Student.DoesNotExist:
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    document.is_important = not document.is_important
    document.save()
    
    return JsonResponse({
        'success': True,
        'is_important': document.is_important
    })


# ==================== ADMIN/HOD DOCUMENT MANAGEMENT ====================

@login_required(login_url='/')
def admin_view_all_documents(request):
    """HOD/Admin view all student documents"""
    if request.user.user_type != '1':
        messages.error(request, 'Access denied')
        return redirect('admin_home')
    
    # Get filter parameters
    student_id = request.GET.get('student')
    category = request.GET.get('category')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    
    # Base query
    documents = StudentDocument.objects.all().select_related('student', 'student__admin')
    
    # Apply filters
    if student_id:
        documents = documents.filter(student_id=student_id)
    if category:
        documents = documents.filter(category=category)
    if date_from:
        documents = documents.filter(uploaded_at__gte=date_from)
    if date_to:
        documents = documents.filter(uploaded_at__lte=date_to)
    
    documents = documents.order_by('-uploaded_at')
    
    # Pagination
    paginator = Paginator(documents, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get all students for filter
    students = Student.objects.all().select_related('admin')
    
    # Statistics
    total_documents = StudentDocument.objects.count()
    total_size_bytes = sum(doc.file.size for doc in StudentDocument.objects.all() if doc.file)
    total_size_gb = round(total_size_bytes / (1024 * 1024 * 1024), 2)
    
    context = {
        'page_title': 'All Student Documents',
        'documents': page_obj,
        'students': students,
        'categories': DOCUMENT_CATEGORIES,
        'selected_student': student_id,
        'selected_category': category,
        'date_from': date_from,
        'date_to': date_to,
        'total_documents': total_documents,
        'total_size_gb': total_size_gb
    }
    
    return render(request, 'hod_template/documents/all_documents.html', context)


@login_required(login_url='/')
def admin_document_statistics(request):
    """Document storage statistics dashboard"""
    if request.user.user_type != '1':
        messages.error(request, 'Access denied')
        return redirect('admin_home')
    
    # Overall statistics
    total_students = Student.objects.count()
    students_with_docs = StudentDocument.objects.values('student').distinct().count()
    total_documents = StudentDocument.objects.count()
    
    # Category statistics
    category_stats = {}
    for category_key, category_info in DOCUMENT_CATEGORIES.items():
        count = StudentDocument.objects.filter(category=category_key).count()
        size_bytes = sum(doc.file.size for doc in StudentDocument.objects.filter(category=category_key) if doc.file)
        
        category_stats[category_key] = {
            'name': category_info['name'],
            'icon': category_info['icon'],
            'count': count,
            'size_mb': round(size_bytes / (1024 * 1024), 2)
        }
    
    # Storage usage
    total_size_bytes = sum(doc.file.size for doc in StudentDocument.objects.all() if doc.file)
    total_size_gb = round(total_size_bytes / (1024 * 1024 * 1024), 3)
    
    # Recent uploads
    recent_uploads = StudentDocument.objects.all().select_related('student', 'student__admin').order_by('-uploaded_at')[:10]
    
    context = {
        'page_title': 'Document Statistics',
        'total_students': total_students,
        'students_with_docs': students_with_docs,
        'total_documents': total_documents,
        'total_size_gb': total_size_gb,
        'category_stats': category_stats,
        'recent_uploads': recent_uploads
    }
    
    return render(request, 'hod_template/documents/statistics.html', context)









