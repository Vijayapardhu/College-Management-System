from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, FileResponse, Http404
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q, Avg, Count
from django.core.files.storage import FileSystemStorage
import os

from .models import *


# ==================== STAFF VIEWS ====================

def staff_upload_material(request):
    """Staff upload study materials"""
    staff = get_object_or_404(Staff, admin=request.user)
    
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        material_type = request.POST.get('material_type')
        subject_id = request.POST.get('subject')
        course_id = request.POST.get('course')
        url = request.POST.get('url')
        tags = request.POST.get('tags', '')
        file = request.FILES.get('file')
        
        try:
            subject = Subject.objects.get(id=subject_id)
            course = Course.objects.get(id=course_id)
            
            material = StudyMaterial.objects.create(
                title=title,
                description=description,
                material_type=material_type,
                subject=subject,
                course=course,
                uploaded_by=staff,
                url=url,
                tags=tags,
                file=file
            )
            
            messages.success(request, "Study material uploaded successfully!")
            return redirect('staff_view_materials')
        except Exception as e:
            messages.error(request, f"Failed to upload material: {str(e)}")
    
    # Get subjects taught by this staff
    subjects = Subject.objects.filter(staff=staff)
    courses = Course.objects.all()
    
    context = {
        'page_title': 'Upload Study Material',
        'subjects': subjects,
        'courses': courses,
    }
    
    return render(request, 'staff_template/upload_material.html', context)


def staff_view_materials(request):
    """View all materials uploaded by staff"""
    staff = get_object_or_404(Staff, admin=request.user)
    materials = StudyMaterial.objects.filter(uploaded_by=staff, is_archived=False).order_by('-created_at')
    
    context = {
        'page_title': 'My Study Materials',
        'materials': materials,
    }
    
    return render(request, 'staff_template/view_materials.html', context)


def staff_create_assignment(request):
    """Create assignment for students"""
    staff = get_object_or_404(Staff, admin=request.user)
    
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        subject_id = request.POST.get('subject')
        course_id = request.POST.get('course')
        due_date = request.POST.get('due_date')
        max_marks = request.POST.get('max_marks', 100)
        attachment = request.FILES.get('attachment')
        
        try:
            subject = Subject.objects.get(id=subject_id)
            course = Course.objects.get(id=course_id)
            
            assignment = Assignment.objects.create(
                title=title,
                description=description,
                subject=subject,
                course=course,
                staff=staff,
                due_date=due_date,
                max_marks=int(max_marks),
                attachment=attachment
            )
            
            messages.success(request, "Assignment created successfully!")
            return redirect('staff_view_assignments')
        except Exception as e:
            messages.error(request, f"Failed to create assignment: {str(e)}")
    
    subjects = Subject.objects.filter(staff=staff)
    courses = Course.objects.all()
    
    context = {
        'page_title': 'Create Assignment',
        'subjects': subjects,
        'courses': courses,
    }
    
    return render(request, 'staff_template/create_assignment.html', context)


def staff_view_assignments(request):
    """View all assignments created by staff"""
    staff = get_object_or_404(Staff, admin=request.user)
    assignments = Assignment.objects.filter(staff=staff).order_by('-due_date')
    
    # Get submission stats for each assignment
    assignment_data = []
    for assignment in assignments:
        total_students = Student.objects.filter(course=assignment.course).count()
        submitted = assignment.submissions.count()
        graded = assignment.submissions.filter(status='graded').count()
        
        assignment_data.append({
            'assignment': assignment,
            'total_students': total_students,
            'submitted': submitted,
            'graded': graded,
            'pending': total_students - submitted,
        })
    
    context = {
        'page_title': 'My Assignments',
        'assignment_data': assignment_data,
    }
    
    return render(request, 'staff_template/view_assignments.html', context)


def staff_view_submissions(request, assignment_id):
    """View submissions for a specific assignment"""
    staff = get_object_or_404(Staff, admin=request.user)
    assignment = get_object_or_404(Assignment, id=assignment_id, staff=staff)
    
    submissions = AssignmentSubmission.objects.filter(
        assignment=assignment
    ).select_related('student', 'student__admin').order_by('-submitted_at')
    
    context = {
        'page_title': f'Submissions: {assignment.title}',
        'assignment': assignment,
        'submissions': submissions,
    }
    
    return render(request, 'staff_template/view_submissions.html', context)


@csrf_exempt
def staff_grade_submission(request):
    """Grade a student's assignment submission"""
    if request.method == 'POST':
        submission_id = request.POST.get('submission_id')
        marks = request.POST.get('marks')
        feedback = request.POST.get('feedback')
        
        try:
            submission = AssignmentSubmission.objects.get(id=submission_id)
            
            # Verify this staff created the assignment
            if submission.assignment.staff.admin != request.user:
                return JsonResponse({'status': 'error', 'message': 'Unauthorized'})
            
            submission.marks_obtained = float(marks)
            submission.feedback = feedback
            submission.graded_by = Staff.objects.get(admin=request.user)
            submission.graded_at = datetime.now()
            submission.status = 'graded'
            submission.save()
            
            return JsonResponse({'status': 'success', 'message': 'Graded successfully!'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    
    return JsonResponse({'status': 'error'})


# ==================== STUDENT VIEWS ====================

def student_view_resources(request):
    """Student view all study materials"""
    student = get_object_or_404(Student, admin=request.user)
    
    # Filter by course
    materials = StudyMaterial.objects.filter(
        course=student.course,
        is_archived=False
    ).select_related('subject', 'uploaded_by', 'uploaded_by__admin').order_by('-created_at')
    
    # Get bookmarks for this student
    bookmarked_ids = ResourceBookmark.objects.filter(
        student=student
    ).values_list('material_id', flat=True)
    
    # Search and filter
    search_query = request.GET.get('search', '')
    subject_filter = request.GET.get('subject', '')
    material_type_filter = request.GET.get('type', '')
    
    if search_query:
        materials = materials.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(tags__icontains=search_query)
        )
    
    if subject_filter:
        materials = materials.filter(subject_id=subject_filter)
    
    if material_type_filter:
        materials = materials.filter(material_type=material_type_filter)
    
    # Get subjects for filter dropdown
    subjects = Subject.objects.filter(course=student.course)
    
    context = {
        'page_title': 'Resource Library',
        'materials': materials,
        'bookmarked_ids': list(bookmarked_ids),
        'subjects': subjects,
        'search_query': search_query,
    }
    
    return render(request, 'student_template/view_resources.html', context)


def student_view_bookmarks(request):
    """View bookmarked resources"""
    student = get_object_or_404(Student, admin=request.user)
    bookmarks = ResourceBookmark.objects.filter(
        student=student
    ).select_related('material', 'material__subject', 'material__uploaded_by').order_by('-created_at')
    
    context = {
        'page_title': 'My Bookmarks',
        'bookmarks': bookmarks,
    }
    
    return render(request, 'student_template/bookmarks.html', context)


@csrf_exempt
def toggle_bookmark(request):
    """Add or remove bookmark"""
    if request.method == 'POST':
        material_id = request.POST.get('material_id')
        
        try:
            student = Student.objects.get(admin=request.user)
            material = StudyMaterial.objects.get(id=material_id)
            
            # Check if already bookmarked
            bookmark = ResourceBookmark.objects.filter(student=student, material=material).first()
            
            if bookmark:
                bookmark.delete()
                return JsonResponse({'status': 'success', 'action': 'removed'})
            else:
                ResourceBookmark.objects.create(student=student, material=material)
                return JsonResponse({'status': 'success', 'action': 'added'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    
    return JsonResponse({'status': 'error'})


@csrf_exempt
def rate_material(request):
    """Rate a study material"""
    if request.method == 'POST':
        material_id = request.POST.get('material_id')
        rating = request.POST.get('rating')
        comment = request.POST.get('comment', '')
        
        try:
            student = Student.objects.get(admin=request.user)
            material = StudyMaterial.objects.get(id=material_id)
            
            # Update or create rating
            obj, created = ResourceRating.objects.update_or_create(
                material=material,
                student=student,
                defaults={'rating': int(rating), 'comment': comment}
            )
            
            return JsonResponse({'status': 'success', 'average': material.average_rating})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    
    return JsonResponse({'status': 'error'})


def download_material(request, material_id):
    """Download a study material and log it"""
    try:
        material = StudyMaterial.objects.get(id=material_id)
        
        # Log download
        ResourceDownloadLog.objects.create(
            material=material,
            user=request.user,
            ip_address=request.META.get('REMOTE_ADDR')
        )
        
        # Increment download count
        material.download_count += 1
        material.save()
        
        # Return file
        if material.file:
            return FileResponse(material.file.open(), as_attachment=True, filename=os.path.basename(material.file.name))
        else:
            messages.error(request, "No file attached to this material")
            return redirect('student_view_resources')
    except StudyMaterial.DoesNotExist:
        raise Http404("Material not found")
    except Exception as e:
        messages.error(request, f"Error downloading file: {str(e)}")
        return redirect('student_view_resources')


def student_view_assignments(request):
    """View all assignments for student's course"""
    student = get_object_or_404(Student, admin=request.user)
    
    # Get all assignments for student's course
    assignments = Assignment.objects.filter(
        course=student.course
    ).select_related('subject', 'staff', 'staff__admin').order_by('-due_date')
    
    # Get student's submissions
    submissions = AssignmentSubmission.objects.filter(
        student=student
    ).select_related('assignment')
    
    submission_dict = {sub.assignment_id: sub for sub in submissions}
    
    # Add submission status to assignments
    assignment_data = []
    for assignment in assignments:
        submission = submission_dict.get(assignment.id)
        assignment_data.append({
            'assignment': assignment,
            'submission': submission,
            'is_overdue': assignment.is_overdue and not submission,
        })
    
    context = {
        'page_title': 'Assignments',
        'assignment_data': assignment_data,
    }
    
    return render(request, 'student_template/view_assignments.html', context)


def student_submit_assignment(request, assignment_id):
    """Submit an assignment"""
    student = get_object_or_404(Student, admin=request.user)
    assignment = get_object_or_404(Assignment, id=assignment_id)
    
    # Check if assignment is for student's course
    if assignment.course != student.course:
        messages.error(request, "This assignment is not for your course")
        return redirect('student_view_assignments')
    
    if request.method == 'POST':
        submission_file = request.FILES.get('submission_file')
        remarks = request.POST.get('remarks', '')
        
        if not submission_file:
            messages.error(request, "Please select a file to submit")
            return redirect('student_submit_assignment', assignment_id=assignment_id)
        
        try:
            # Check if already submitted
            existing = AssignmentSubmission.objects.filter(
                assignment=assignment,
                student=student
            ).first()
            
            if existing:
                # Update submission
                existing.submission_file = submission_file
                existing.remarks = remarks
                existing.save()
                messages.success(request, "Assignment re-submitted successfully!")
            else:
                # Create new submission
                submission = AssignmentSubmission.objects.create(
                    assignment=assignment,
                    student=student,
                    submission_file=submission_file,
                    remarks=remarks
                )
                messages.success(request, "Assignment submitted successfully!")
            
            return redirect('student_view_assignments')
        except Exception as e:
            messages.error(request, f"Failed to submit assignment: {str(e)}")
    
    # Check if already submitted
    existing_submission = AssignmentSubmission.objects.filter(
        assignment=assignment,
        student=student
    ).first()
    
    context = {
        'page_title': f'Submit: {assignment.title}',
        'assignment': assignment,
        'existing_submission': existing_submission,
    }
    
    return render(request, 'student_template/submit_assignment.html', context)


# ==================== ADMIN VIEWS ====================

def admin_view_resources(request):
    """HOD view all study materials"""
    materials = StudyMaterial.objects.select_related(
        'subject', 'course', 'uploaded_by', 'uploaded_by__admin'
    ).order_by('-created_at')
    
    # Statistics
    total_materials = materials.count()
    total_downloads = materials.aggregate(total=Count('download_logs'))['total'] or 0
    avg_rating = ResourceRating.objects.aggregate(avg=Avg('rating'))['avg'] or 0
    
    context = {
        'page_title': 'Resource Library Management',
        'materials': materials,
        'total_materials': total_materials,
        'total_downloads': total_downloads,
        'avg_rating': round(avg_rating, 2),
    }
    
    return render(request, 'hod_template/view_resources.html', context)


def admin_resource_stats(request):
    """View resource usage statistics"""
    # Top downloaded materials
    top_materials = StudyMaterial.objects.order_by('-download_count')[:10]
    
    # Top rated materials
    top_rated = StudyMaterial.objects.annotate(
        avg_rating=Avg('ratings__rating')
    ).order_by('-avg_rating')[:10]
    
    # Most active uploaders
    top_uploaders = Staff.objects.annotate(
        upload_count=Count('uploaded_materials')
    ).order_by('-upload_count')[:10]
    
    # Recent downloads
    recent_downloads = ResourceDownloadLog.objects.select_related(
        'material', 'user'
    ).order_by('-downloaded_at')[:20]
    
    context = {
        'page_title': 'Resource Usage Statistics',
        'top_materials': top_materials,
        'top_rated': top_rated,
        'top_uploaders': top_uploaders,
        'recent_downloads': recent_downloads,
    }
    
    return render(request, 'hod_template/resource_stats.html', context)


def admin_view_all_assignments(request):
    """HOD view all assignments across courses"""
    assignments = Assignment.objects.select_related(
        'subject', 'course', 'staff', 'staff__admin'
    ).order_by('-due_date')
    
    # Get submission statistics
    assignment_data = []
    for assignment in assignments:
        total_students = Student.objects.filter(course=assignment.course).count()
        submitted = assignment.submissions.count()
        graded = assignment.submissions.filter(status='graded').count()
        avg_marks = assignment.submissions.filter(
            status='graded'
        ).aggregate(avg=Avg('marks_obtained'))['avg']
        
        assignment_data.append({
            'assignment': assignment,
            'total_students': total_students,
            'submitted': submitted,
            'graded': graded,
            'avg_marks': round(avg_marks, 2) if avg_marks else 0,
        })
    
    context = {
        'page_title': 'All Assignments',
        'assignment_data': assignment_data,
    }
    
    return render(request, 'hod_template/view_all_assignments.html', context)


# ==================== ANNOUNCEMENT VIEWS ====================

def admin_create_announcement(request):
    """Create announcement"""
    if request.method == 'POST':
        title = request.POST.get('title')
        message = request.POST.get('message')
        priority = request.POST.get('priority')
        target_audience = request.POST.get('target_audience')
        course_id = request.POST.get('course')
        expires_at = request.POST.get('expires_at')
        attachment = request.FILES.get('attachment')
        
        try:
            course = Course.objects.get(id=course_id) if course_id else None
            
            announcement = Announcement.objects.create(
                title=title,
                message=message,
                priority=priority,
                target_audience=target_audience,
                course=course,
                posted_by=request.user,
                expires_at=expires_at if expires_at else None,
                attachment=attachment
            )
            
            messages.success(request, "Announcement posted successfully!")
            return redirect('admin_view_announcements')
        except Exception as e:
            messages.error(request, f"Failed to create announcement: {str(e)}")
    
    courses = Course.objects.all()
    context = {
        'page_title': 'Create Announcement',
        'courses': courses,
    }
    
    return render(request, 'hod_template/create_announcement.html', context)


def view_announcements(request):
    """View announcements (for all user types)"""
    from django.utils import timezone
    
    # Get active announcements
    announcements = Announcement.objects.filter(
        Q(is_active=True) &
        (Q(expires_at__isnull=True) | Q(expires_at__gte=timezone.now()))
    )
    
    # Filter based on user type
    if request.user.user_type == '2':  # Staff
        announcements = announcements.filter(
            Q(target_audience='all') | Q(target_audience='staff')
        )
    elif request.user.user_type == '3':  # Student
        student = Student.objects.get(admin=request.user)
        announcements = announcements.filter(
            Q(target_audience='all') |
            Q(target_audience='students') |
            Q(target_audience='course', course=student.course)
        )
    
    announcements = announcements.select_related('posted_by', 'course').order_by('-priority', '-created_at')
    
    # Determine template
    if request.user.user_type == '1':
        template = 'hod_template/announcements.html'
    elif request.user.user_type == '2':
        template = 'staff_template/announcements.html'
    else:
        template = 'student_template/announcements.html'
    
    context = {
        'page_title': 'Announcements',
        'announcements': announcements,
    }
    
    return render(request, template, context)


# ==================== DISCUSSION FORUM ====================

def view_discussions(request, subject_id):
    """View discussions for a subject"""
    subject = get_object_or_404(Subject, id=subject_id)
    discussions = Discussion.objects.filter(
        subject=subject
    ).select_related('created_by').annotate(
        reply_count=Count('replies')
    ).order_by('-is_pinned', '-updated_at')
    
    # Determine template
    if request.user.user_type == '1':
        template = 'hod_template/discussions.html'
    elif request.user.user_type == '2':
        template = 'staff_template/discussions.html'
    else:
        template = 'student_template/discussions.html'
    
    context = {
        'page_title': f'Discussions: {subject.name}',
        'subject': subject,
        'discussions': discussions,
    }
    
    return render(request, template, context)


def create_discussion(request, subject_id):
    """Create a new discussion"""
    subject = get_object_or_404(Subject, id=subject_id)
    
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        material_id = request.POST.get('material_id')
        
        try:
            material = StudyMaterial.objects.get(id=material_id) if material_id else None
            
            discussion = Discussion.objects.create(
                title=title,
                content=content,
                subject=subject,
                material=material,
                created_by=request.user
            )
            
            messages.success(request, "Discussion created successfully!")
            return redirect('view_discussion', discussion_id=discussion.id)
        except Exception as e:
            messages.error(request, f"Failed to create discussion: {str(e)}")
    
    # Get materials for this subject
    materials = StudyMaterial.objects.filter(subject=subject, is_archived=False)
    
    context = {
        'page_title': f'Create Discussion: {subject.name}',
        'subject': subject,
        'materials': materials,
    }
    
    # Determine template
    if request.user.user_type == '2':
        template = 'staff_template/create_discussion.html'
    else:
        template = 'student_template/create_discussion.html'
    
    return render(request, template, context)


def view_discussion(request, discussion_id):
    """View a discussion and its replies"""
    discussion = get_object_or_404(Discussion, id=discussion_id)
    replies = discussion.replies.select_related('created_by').order_by('created_at')
    
    # Determine template
    if request.user.user_type == '1':
        template = 'hod_template/view_discussion.html'
    elif request.user.user_type == '2':
        template = 'staff_template/view_discussion.html'
    else:
        template = 'student_template/view_discussion.html'
    
    context = {
        'page_title': discussion.title,
        'discussion': discussion,
        'replies': replies,
    }
    
    return render(request, template, context)


@csrf_exempt
def reply_discussion(request):
    """Reply to a discussion"""
    if request.method == 'POST':
        discussion_id = request.POST.get('discussion_id')
        content = request.POST.get('content')
        
        try:
            discussion = Discussion.objects.get(id=discussion_id)
            
            # Check if locked
            if discussion.is_locked:
                return JsonResponse({'status': 'error', 'message': 'Discussion is locked'})
            
            DiscussionReply.objects.create(
                discussion=discussion,
                content=content,
                created_by=request.user
            )
            
            # Update discussion timestamp
            discussion.save()
            
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    
    return JsonResponse({'status': 'error'})


