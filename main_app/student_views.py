import json
import math
from datetime import datetime

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse, JsonResponse
from django.shortcuts import (HttpResponseRedirect, get_object_or_404,
                              redirect, render)
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q

from .forms import *
from .models import *
from collections import defaultdict


def student_home(request):
    student = get_object_or_404(Student, admin=request.user)
    total_subject = Subject.objects.filter(course=student.course).count()
    total_attendance = AttendanceReport.objects.filter(student=student).count()
    total_present = AttendanceReport.objects.filter(student=student, status=True).count()
    if total_attendance == 0:  # Don't divide. DivisionByZero
        percent_absent = percent_present = 0
    else:
        percent_present = math.floor((total_present/total_attendance) * 100)
        percent_absent = math.ceil(100 - percent_present)
    subject_name = []
    data_present = []
    data_absent = []
    subjects = Subject.objects.filter(course=student.course)
    for subject in subjects:
        attendance = Attendance.objects.filter(subject=subject)
        present_count = AttendanceReport.objects.filter(
            attendance__in=attendance, status=True, student=student).count()
        absent_count = AttendanceReport.objects.filter(
            attendance__in=attendance, status=False, student=student).count()
        subject_name.append(subject.name)
        data_present.append(present_count)
        data_absent.append(absent_count)
    # Get public links for dashboard
    public_links = PublicLink.objects.filter(is_active=True).order_by('display_order', 'title')
    featured_links = public_links.filter(is_featured=True)
    
    # Categorize links
    categorized_links = defaultdict(list)
    for link in public_links:
        categorized_links[link.category].append(link)
    
    context = {
        'student': student,
        'total_attendance': total_attendance,
        'total_present': total_present,
        'percent_present': percent_present,
        'percent_absent': percent_absent,
        'total_subject': total_subject,
        'subjects': subjects,
        'subject_name': subject_name,
        'data_present': data_present,
        'data_absent': data_absent,
        'public_links': public_links,
        'featured_links': featured_links,
        'categorized_links': dict(categorized_links),
        'current_date': datetime.now(),
        'page_title': 'Student Homepage'
    }
    return render(request, 'student_template/home_content.html', context)


@ csrf_exempt
def student_view_attendance(request):
    student = get_object_or_404(Student, admin=request.user)
    if request.method != 'POST':
        course = get_object_or_404(Course, id=student.course.id)
        # Calculate attendance statistics
        from main_app.models import AttendanceReport
        
        total_present = 0
        total_absent = 0
        data_present = []
        data_absent = []
        subject_attendance_data = []
        
        subjects_list = Subject.objects.filter(course=course)
        
        for subject in subjects_list:
            try:
                attendance_reports = AttendanceReport.objects.filter(
                    student_id=student,
                    attendance_id__subject_id=subject
                )
                
                present_count = attendance_reports.filter(status=True).count()
                absent_count = attendance_reports.filter(status=False).count()
                total_classes = attendance_reports.count()
                
                total_present += present_count
                total_absent += absent_count
                
                if total_classes > 0:
                    percentage = round((present_count / total_classes) * 100, 2)
                else:
                    percentage = 0
                
                data_present.append(percentage)
                data_absent.append(absent_count)
                
                # Create structured data for each subject
                subject_attendance_data.append({
                    'subject': subject,
                    'present': present_count,
                    'absent': absent_count,
                    'total': total_classes,
                    'percentage': percentage
                })
            except:
                data_present.append(0)
                data_absent.append(0)
                subject_attendance_data.append({
                    'subject': subject,
                    'present': 0,
                    'absent': 0,
                    'total': 0,
                    'percentage': 0
                })
        
        total_classes_overall = total_present + total_absent
        percentage_present = round((total_present / total_classes_overall) * 100, 2) if total_classes_overall > 0 else 0
        
        context = {
            'subjects': Subject.objects.filter(course=course),
            'subject_attendance_data': subject_attendance_data,
            'total_present': total_present,
            'total_absent': total_absent,
            'percentage_present': percentage_present,
            'data_present': data_present,
            'data_absent': data_absent,
            'page_title': 'View Attendance'
        }
        return render(request, 'student_template/student_view_attendance.html', context)
    else:
        subject_id = request.POST.get('subject')
        start = request.POST.get('start_date')
        end = request.POST.get('end_date')
        try:
            subject = get_object_or_404(Subject, id=subject_id)
            start_date = datetime.strptime(start, "%Y-%m-%d")
            end_date = datetime.strptime(end, "%Y-%m-%d")
            attendance = Attendance.objects.filter(
                date__range=(start_date, end_date), subject=subject)
            attendance_reports = AttendanceReport.objects.filter(
                attendance__in=attendance, student=student)
            json_data = []
            for report in attendance_reports:
                data = {
                    "date":  str(report.attendance.date),
                    "status": report.status
                }
                json_data.append(data)
            return JsonResponse(json.dumps(json_data), safe=False)
        except Exception as e:
            return None


def student_apply_leave(request):
    form = LeaveReportStudentForm(request.POST or None)
    student = get_object_or_404(Student, admin_id=request.user.id)
    context = {
        'form': form,
        'leave_history': LeaveReportStudent.objects.filter(student=student),
        'page_title': 'Apply for leave'
    }
    if request.method == 'POST':
        if form.is_valid():
            try:
                obj = form.save(commit=False)
                obj.student = student
                obj.save()
                messages.success(
                    request, "Application for leave has been submitted for review")
                return redirect(reverse('student_apply_leave'))
            except Exception:
                messages.error(request, "Could not submit")
        else:
            messages.error(request, "Form has errors!")
    return render(request, "student_template/student_apply_leave.html", context)


def student_feedback(request):
    form = FeedbackStudentForm(request.POST or None)
    student = get_object_or_404(Student, admin_id=request.user.id)
    
    if request.method == 'POST':
        if form.is_valid():
            try:
                obj = form.save(commit=False)
                obj.student = student
                # Get additional fields from POST data
                obj.rating = request.POST.get('rating', 0)
                obj.category = request.POST.get('category', 'general')
                obj.save()
                messages.success(request, "Feedback submitted successfully! We'll review it shortly.")
                return redirect(reverse('student_feedback'))
            except Exception as e:
                messages.error(request, f"Could not submit feedback: {str(e)}")
        else:
            messages.error(request, "Please fill all required fields!")
    
    # Get feedback data
    feedbacks = FeedbackStudent.objects.filter(student=student).order_by('-created_at')
    
    # Calculate statistics
    total_feedbacks = feedbacks.count()
    replied_feedbacks = feedbacks.exclude(reply='').count()
    pending_feedbacks = feedbacks.filter(reply='').count()
    
    context = {
        'form': form,
        'feedbacks': feedbacks,
        'page_title': 'Student Feedback',
        'total_feedbacks': total_feedbacks,
        'replied_feedbacks': replied_feedbacks,
        'pending_feedbacks': pending_feedbacks,
    }
    return render(request, "student_template/student_feedback.html", context)


def student_view_profile(request):
    student = get_object_or_404(Student, admin=request.user)
    
    if request.method == 'POST':
        try:
            password = request.POST.get('password')
            confirm_password = request.POST.get('confirm_password')
            
            # Validate passwords match
            if password != confirm_password:
                messages.error(request, "Passwords do not match!")
                return redirect(reverse('student_view_profile'))
            
            # Validate password length
            if len(password) < 6:
                messages.error(request, "Password must be at least 6 characters long!")
                return redirect(reverse('student_view_profile'))
            
            # Update password
            admin = student.admin
            admin.set_password(password)
            admin.save()
            
            messages.success(request, "Password updated successfully! Please login again with your new password.")
            
            # Logout user after password change
            from django.contrib.auth import logout
            logout(request)
            return redirect('login_page')
            
        except Exception as e:
            messages.error(request, "Error occurred while updating password: " + str(e))
            return redirect(reverse('student_view_profile'))
    
    context = {
        'student': student,
        'page_title': 'My Profile'
    }
    return render(request, "student_template/student_view_profile.html", context)


@csrf_exempt
def student_fcmtoken(request):
    token = request.POST.get('token')
    student_user = get_object_or_404(CustomUser, id=request.user.id)
    try:
        student_user.fcm_token = token
        student_user.save()
        return HttpResponse("True")
    except Exception as e:
        return HttpResponse("False")


def student_view_notification(request):
    student = get_object_or_404(Student, admin=request.user)
    notifications = NotificationStudent.objects.filter(student=student)
    
    # Calculate statistics
    total_notifications = notifications.count()
    unread_notifications = notifications.filter(is_read=False).count()
    important_notifications = notifications.filter(is_important=True).count()
    read_notifications = notifications.filter(is_read=True).count()
    
    context = {
        'notifications': notifications,
        'page_title': "Notifications",
        'total_notifications': total_notifications,
        'unread_notifications': unread_notifications,
        'important_notifications': important_notifications,
        'read_notifications': read_notifications,
    }
    return render(request, "student_template/student_view_notification.html", context)


def student_view_result(request):
    student = get_object_or_404(Student, admin=request.user)
    results = StudentResult.objects.filter(student=student).select_related('subject')
    
    # Get assignment marks
    assignment_submissions = AssignmentSubmission.objects.filter(
        student=student,
        status='graded'
    ).select_related('assignment', 'assignment__subject', 'graded_by')
    
    # Calculate statistics
    cgpa = 0
    average_marks = 0
    rank = "N/A"
    
    if results.exists():
        total_marks = 0
        total_subjects = results.count()
        
        for result in results:
            subject_total = result.test + result.exam
            total_marks += subject_total
        
        # Calculate average and CGPA
        average_marks = round(total_marks / total_subjects, 2) if total_subjects > 0 else 0
        cgpa = round(average_marks / 10, 2)  # Assuming 100 marks total, CGPA on 10 scale
    
    context = {
        'results': results,
        'assignment_submissions': assignment_submissions,
        'cgpa': cgpa,
        'average_marks': average_marks,
        'rank': rank,
        'page_title': "View Results"
    }
    return render(request, "student_template/student_view_result.html", context)

# ==================== NEW STUDENT PORTAL VIEWS ====================

def student_view_timetable(request):
    """View weekly timetable"""
    student = get_object_or_404(Student, admin=request.user)
    
    # Get timetable for student's course and semester
    timetable_entries = Timetable.objects.filter(
        course=student.course,
        semester=student.current_semester,
        session=student.session
    ).select_related('subject', 'staff').order_by('weekday', 'period')
    
    # Organize by weekday and period - Create a simple list structure
    weekdays = [
        {'key': 'monday', 'name': 'Monday'},
        {'key': 'tuesday', 'name': 'Tuesday'},
        {'key': 'wednesday', 'name': 'Wednesday'},
        {'key': 'thursday', 'name': 'Thursday'},
        {'key': 'friday', 'name': 'Friday'},
        {'key': 'saturday', 'name': 'Saturday'}
    ]
    
    periods = [
        {'key': '1', 'type': 'class'},
        {'key': '2', 'type': 'class'},
        {'key': '3', 'type': 'class'},
        {'key': '4', 'type': 'class'},
        {'key': 'lunch', 'type': 'break', 'name': 'Lunch'},
        {'key': '5', 'type': 'class'},
        {'key': '6', 'type': 'class'},
        {'key': '7', 'type': 'class'}
    ]
    
    # Build timetable structure
    for day in weekdays:
        day['periods'] = []
        for period in periods:
            if period['type'] == 'break':
                day['periods'].append(period)
            else:
                # Find class for this day and period
                entry = timetable_entries.filter(weekday=day['key'], period=period['key']).first()
                day['periods'].append({
                    'key': period['key'],
                    'type': 'class',
                    'class_data': entry
                })
    
    context = {
        'page_title': 'My Timetable',
        'weekdays': weekdays,
        'has_timetable': timetable_entries.exists(),
        'student': student
    }
    return render(request, 'student_template/view_timetable.html', context)


def student_view_exam_schedule(request):
    """View exam schedule"""
    student = get_object_or_404(Student, admin=request.user)
    
    # Get active exams for student's session and semester
    exams = Exam.objects.filter(
        session=student.session,
        semester=student.current_semester
    ).order_by('-start_date')
    
    # Get exam schedules for subjects in student's course
    subjects = Subject.objects.filter(course=student.course)
    schedules = []
    
    for exam in exams:
        exam_schedules = ExamSchedule.objects.filter(
            exam=exam,
            subject__in=subjects
        ).order_by('exam_date', 'start_time')
        
        if exam_schedules.exists():
            schedules.append({
                'exam': exam,
                'schedules': exam_schedules
            })
    
    context = {
        'page_title': 'Exam Schedule',
        'schedules': schedules,
        'student': student
    }
    return render(request, 'student_template/view_exam_schedule.html', context)


def student_download_admit_card(request, exam_id):
    """Download admit card for an exam"""
    student = get_object_or_404(Student, admin=request.user)
    exam = get_object_or_404(Exam, id=exam_id)
    
    # Get or create admit card
    admit_card, created = AdmitCard.objects.get_or_create(
        exam=exam,
        student=student,
        defaults={
            'admit_card_number': f"{exam.id}-{student.id}-{exam.session.start_year.year}",
            'is_generated': True
        }
    )
    
    # Mark as downloaded
    if not admit_card.is_downloaded:
        from django.utils import timezone
        admit_card.is_downloaded = True
        admit_card.downloaded_at = timezone.now()
        admit_card.save()
    
    # Get exam schedules for this exam
    subjects = Subject.objects.filter(course=student.course)
    schedules = ExamSchedule.objects.filter(
        exam=exam,
        subject__in=subjects
    ).order_by('exam_date', 'start_time')
    
    context = {
        'page_title': 'Admit Card',
        'admit_card': admit_card,
        'student': student,
        'exam': exam,
        'schedules': schedules
    }
    return render(request, 'student_template/download_admit_card.html', context)


def student_view_semester_results(request):
    """View semester-wise results"""
    student = get_object_or_404(Student, admin=request.user)
    
    # Get all published semester results
    semester_results = SemesterResult.objects.filter(
        student=student,
        is_published=True
    ).order_by('-session', '-semester')
    
    context = {
        'page_title': 'My Results',
        'semester_results': semester_results,
        'student': student
    }
    return render(request, 'student_template/view_results.html', context)


def student_view_semester_detail(request, result_id):
    """View detailed subject-wise results for a semester"""
    student = get_object_or_404(Student, admin=request.user)
    semester_result = get_object_or_404(SemesterResult, id=result_id, student=student, is_published=True)
    
    # Get subject-wise results
    subject_results = SubjectResult.objects.filter(semester_result=semester_result)
    
    context = {
        'page_title': f'Semester {semester_result.semester} Results',
        'semester_result': semester_result,
        'subject_results': subject_results,
        'student': student
    }
    return render(request, 'student_template/view_semester_detail.html', context)


def student_view_placement_drives(request):
    """View available placement drives"""
    student = get_object_or_404(Student, admin=request.user)
    
    # Get active placement drives eligible for student's course
    from django.utils import timezone
    now = timezone.now()
    
    drives = PlacementDrive.objects.filter(
        is_active=True,
        registration_deadline__gte=now,
        eligible_courses=student.course
    ).order_by('registration_deadline')
    
    # Check eligibility based on CGPA and backlogs
    eligible_drives = []
    applied_drive_ids = PlacementApplication.objects.filter(student=student).values_list('placement_drive_id', flat=True)
    
    for drive in drives:
        # Get student's latest CGPA
        latest_result = SemesterResult.objects.filter(student=student).order_by('-semester').first()
        
        is_eligible = True
        reasons = []
        
        if latest_result:
            if latest_result.cgpa and latest_result.cgpa < drive.min_cgpa:
                is_eligible = False
                reasons.append(f"Min CGPA required: {drive.min_cgpa}, Your CGPA: {latest_result.cgpa}")
            
            if latest_result.number_of_backlogs > drive.allowed_backlogs:
                is_eligible = False
                reasons.append(f"Max backlogs allowed: {drive.allowed_backlogs}, You have: {latest_result.number_of_backlogs}")
        
        eligible_drives.append({
            'drive': drive,
            'is_eligible': is_eligible,
            'reasons': reasons,
            'has_applied': drive.id in applied_drive_ids
        })
    
    context = {
        'page_title': 'Placement Drives',
        'eligible_drives': eligible_drives,
        'student': student
    }
    return render(request, 'student_template/view_placement_drives.html', context)


def student_apply_placement(request, drive_id):
    """Apply for a placement drive"""
    student = get_object_or_404(Student, admin=request.user)
    drive = get_object_or_404(PlacementDrive, id=drive_id)
    
    # Check if already applied
    if PlacementApplication.objects.filter(placement_drive=drive, student=student).exists():
        messages.error(request, "You have already applied for this drive!")
        return redirect('student_view_placement_drives')
    
    form = PlacementApplicationForm(request.POST or None, request.FILES or None)
    
    if request.method == 'POST':
        if form.is_valid():
            application = form.save(commit=False)
            application.placement_drive = drive
            application.student = student
            application.status = 'registered'
            application.save()
            messages.success(request, "Application submitted successfully!")
            return redirect('student_my_placement_applications')
        else:
            messages.error(request, "Failed to submit application. Please check the form.")
    
    context = {
        'page_title': f'Apply for {drive.company.name}',
        'form': form,
        'drive': drive,
        'student': student
    }
    return render(request, 'student_template/apply_placement.html', context)


def student_my_placement_applications(request):
    """View my placement applications"""
    student = get_object_or_404(Student, admin=request.user)
    applications = PlacementApplication.objects.filter(student=student).order_by('-applied_at')
    
    context = {
        'page_title': 'My Placement Applications',
        'applications': applications,
        'student': student
    }
    return render(request, 'student_template/my_placement_applications.html', context)


def student_view_fee_structure(request):
    """View fee structure"""
    student = get_object_or_404(Student, admin=request.user)
    
    # Get fee structure for student's course, type, and current semester
    fee_structure = FeeStructure.objects.filter(
        course=student.course,
        course_type=student.course_type,
        semester=student.current_semester,
        session=student.session
    ).first()
    
    # Get payment history
    payments = FeePayment.objects.filter(student=student).order_by('-payment_date')
    
    # Calculate total paid and pending
    total_paid = sum([p.amount_paid for p in payments])
    total_due = 0
    
    if fee_structure:
        total_due = fee_structure.total_fee - total_paid
    
    context = {
        'page_title': 'Fee Structure',
        'fee_structure': fee_structure,
        'payments': payments,
        'total_paid': total_paid,
        'total_due': total_due,
        'student': student
    }
    return render(request, 'student_template/view_fee_structure.html', context)


def student_fee_receipts(request):
    """View and download fee receipts"""
    student = get_object_or_404(Student, admin=request.user)
    payments = FeePayment.objects.filter(student=student).order_by('-payment_date')
    
    context = {
        'page_title': 'Fee Receipts',
        'payments': payments,
        'student': student
    }
    return render(request, 'student_template/fee_receipts.html', context)


def student_submit_grievance(request):
    """Submit a grievance"""
    student = get_object_or_404(Student, admin=request.user)
    form = GrievanceForm(request.POST or None, request.FILES or None)
    
    if request.method == 'POST':
        if form.is_valid():
            grievance = form.save(commit=False)
            grievance.submitted_by = request.user
            
            # Generate unique grievance number
            from datetime import datetime
            grievance_number = f"GRV-{datetime.now().year}-{datetime.now().month:02d}-{student.id}-{Grievance.objects.count() + 1}"
            grievance.grievance_number = grievance_number
            grievance.status = 'submitted'
            
            grievance.save()
            messages.success(request, f"Grievance submitted successfully! Tracking Number: {grievance_number}")
            return redirect('student_my_grievances')
        else:
            messages.error(request, "Failed to submit grievance. Please check the form.")
    
    context = {
        'page_title': 'Submit Grievance',
        'form': form,
        'student': student
    }
    return render(request, 'student_template/submit_grievance.html', context)


def student_my_grievances(request):
    """View my grievances"""
    student = get_object_or_404(Student, admin=request.user)
    grievances = Grievance.objects.filter(submitted_by=request.user).order_by('-submitted_at')
    
    context = {
        'page_title': 'My Grievances',
        'grievances': grievances,
        'student': student
    }
    return render(request, 'student_template/my_grievances.html', context)


# ==================== LIBRARY FEATURES ====================

def student_search_books(request):
    """Search library books"""
    student = get_object_or_404(Student, admin=request.user)
    
    search_query = request.GET.get('search', '')
    category = request.GET.get('category', '')
    subject_id = request.GET.get('subject', '')
    
    books = Library.objects.all()
    
    if search_query:
        books = books.filter(
            Q(title__icontains=search_query) | 
            Q(author__icontains=search_query) | 
            Q(isbn__icontains=search_query)
        )
    
    if category:
        books = books.filter(category=category)
    
    if subject_id:
        books = books.filter(subject_id=subject_id)
    
    books = books.order_by('title')
    
    # Get subjects for filter
    subjects = Subject.objects.filter(course=student.course)
    
    context = {
        'page_title': 'Search Library Books',
        'books': books,
        'subjects': subjects,
        'search_query': search_query,
        'selected_category': category,
        'selected_subject': subject_id,
        'student': student
    }
    return render(request, 'student_template/search_books.html', context)


def student_my_library_issues(request):
    """View my library issues"""
    student = get_object_or_404(Student, admin=request.user)
    issues = LibraryIssue.objects.filter(student=student).order_by('-issue_date')
    
    # Count active issues
    active_issues = issues.filter(status='issued').count()
    overdue_issues = issues.filter(status='overdue').count()
    total_fines = sum([issue.fine_amount for issue in issues])
    
    context = {
        'page_title': 'My Library Books',
        'issues': issues,
        'active_issues': active_issues,
        'overdue_issues': overdue_issues,
        'total_fines': total_fines,
        'student': student
    }
    return render(request, 'student_template/my_library_issues.html', context)


# ==================== SCHOLARSHIP FEATURES ====================

def student_view_scholarships(request):
    """View available scholarships"""
    student = get_object_or_404(Student, admin=request.user)
    
    from django.utils import timezone
    now = timezone.now().date()
    
    # Get active scholarships with deadline not passed
    scholarships = Scholarship.objects.filter(
        is_active=True,
        application_deadline__gte=now
    ).order_by('application_deadline')
    
    # Check which scholarships student has applied for
    applied_ids = ScholarshipApplication.objects.filter(student=student).values_list('scholarship_id', flat=True)
    
    context = {
        'page_title': 'Available Scholarships',
        'scholarships': scholarships,
        'applied_ids': list(applied_ids),
        'student': student
    }
    return render(request, 'student_template/view_scholarships.html', context)


def student_apply_scholarship(request, scholarship_id):
    """Apply for scholarship"""
    student = get_object_or_404(Student, admin=request.user)
    scholarship = get_object_or_404(Scholarship, id=scholarship_id)
    
    # Check if already applied
    if ScholarshipApplication.objects.filter(scholarship=scholarship, student=student).exists():
        messages.error(request, "You have already applied for this scholarship!")
        return redirect('student_view_scholarships')
    
    form = ScholarshipApplicationForm(request.POST or None, request.FILES or None)
    
    if request.method == 'POST':
        if form.is_valid():
            application = form.save(commit=False)
            application.student = student
            application.status = 'applied'
            application.save()
            messages.success(request, "Scholarship application submitted successfully!")
            return redirect('student_my_scholarship_applications')
        else:
            messages.error(request, "Failed to submit application.")
    else:
        form.fields['scholarship'].initial = scholarship
        form.fields['scholarship'].widget = forms.HiddenInput()
    
    context = {
        'page_title': f'Apply for {scholarship.name}',
        'form': form,
        'scholarship': scholarship,
        'student': student
    }
    return render(request, 'student_template/apply_scholarship.html', context)


def student_my_scholarship_applications(request):
    """View my scholarship applications"""
    student = get_object_or_404(Student, admin=request.user)
    applications = ScholarshipApplication.objects.filter(student=student).order_by('-application_date')
    
    context = {
        'page_title': 'My Scholarship Applications',
        'applications': applications,
        'student': student
    }
    return render(request, 'student_template/my_scholarship_applications.html', context)


# ==================== TRANSPORT & HOSTEL FEATURES ====================

def student_my_transport(request):
    """View my transport details"""
    student = get_object_or_404(Student, admin=request.user)
    
    allocation = TransportAllocation.objects.filter(student=student, is_active=True).first()
    
    context = {
        'page_title': 'My Transport Details',
        'allocation': allocation,
        'student': student
    }
    return render(request, 'student_template/my_transport_details.html', context)


def student_my_hostel(request):
    """View my hostel details"""
    student = get_object_or_404(Student, admin=request.user)
    
    try:
        allocation = HostelAllocation.objects.get(student=student, is_active=True)
    except HostelAllocation.DoesNotExist:
        allocation = None
    
    context = {
        'page_title': 'My Hostel Details',
        'allocation': allocation,
        'student': student
    }
    return render(request, 'student_template/my_hostel_details.html', context)


# ============================================================================
# NEW ECAP FEATURES - STUDENT VIEWS
# ============================================================================

# Online Examination
@login_required
def student_online_exams(request):
    """Student view available online exams"""
    student = get_object_or_404(Student, admin=request.user)
    from main_app.models import OnlineExam
    from datetime import datetime
    
    # Get exams for student's course that are currently active
    available_exams = OnlineExam.objects.filter(
        course=student.course,
        is_published=True,
        start_datetime__lte=datetime.now(),
        end_datetime__gte=datetime.now()
    ).select_related('subject', 'created_by')
    
    context = {
        'page_title': 'Available Online Exams',
        'exams': available_exams,
        'student': student
    }
    return render(request, 'student_template/online_exams.html', context)


@login_required
def student_exam_results(request):
    """Student view their online exam results"""
    student = get_object_or_404(Student, admin=request.user)
    from main_app.models import OnlineExamAttempt
    
    context = {
        'page_title': 'My Exam Results',
        'attempts': OnlineExamAttempt.objects.filter(student=student).select_related('exam').order_by('-submit_time')
    }
    return render(request, 'student_template/exam_results.html', context)


# Certificates
@login_required
def student_my_certificates(request):
    """Student view their certificates"""
    student = get_object_or_404(Student, admin=request.user)
    from main_app.models import StudentCertificate
    
    # Get all certificates
    certificates = StudentCertificate.objects.filter(student=student).order_by('-uploaded_at')
    
    # Calculate statistics
    total_certificates = certificates.count()
    verified_certificates = 0  # Can be updated if you add a verification status field
    pending_requests = 0  # Can be updated if you add a pending status
    
    context = {
        'page_title': 'My Certificates',
        'certificates': certificates,
        'total_certificates': total_certificates,
        'verified_certificates': verified_certificates,
        'pending_requests': pending_requests,
    }
    return render(request, 'student_template/my_certificates.html', context)


@login_required
def student_request_certificate(request):
    """Student upload and manage certificates"""
    student = get_object_or_404(Student, admin=request.user)
    
    if request.method == 'POST':
        # Handle certificate upload
        certificate_type = request.POST.get('certificate_type')
        certificate_title = request.POST.get('certificate_title')
        issue_date = request.POST.get('issue_date')
        certificate_file = request.FILES.get('certificate_file')
        
        if certificate_file and certificate_type and certificate_title:
            try:
                from main_app.models import StudentCertificate
                cert = StudentCertificate.objects.create(
                    student=student,
                    certificate_type=certificate_type,
                    certificate_title=certificate_title,
                    certificate_file=certificate_file,
                    issue_date=issue_date if issue_date else None
                )
                messages.success(request, f"Certificate '{certificate_title}' uploaded successfully!")
            except Exception as e:
                messages.error(request, f"Error uploading certificate: {str(e)}")
        else:
            messages.error(request, "Please fill all required fields and select a file.")
        
        return redirect('my_certificates')
    
    # Get student's uploaded certificates
    from main_app.models import StudentCertificate
    certificates = StudentCertificate.objects.filter(student=student)
    
    context = {
        'page_title': 'My Certificates',
        'student': student,
        'certificates': certificates
    }
    return render(request, 'student_template/request_certificate.html', context)


# Internships
@login_required
def student_my_internships(request):
    """Student view their internships"""
    student = get_object_or_404(Student, admin=request.user)
    from main_app.models import Internship
    
    context = {
        'page_title': 'My Internships',
        'internships': Internship.objects.filter(student=student).order_by('-start_date')
    }
    return render(request, 'student_template/my_internships.html', context)


@login_required
def student_add_internship(request):
    """Student add internship details"""
    student = get_object_or_404(Student, admin=request.user)
    from main_app.models import Internship
    from main_app.forms import InternshipForm
    
    if request.method == 'POST':
        form = InternshipForm(request.POST, request.FILES)
        if form.is_valid():
            internship = form.save(commit=False)
            internship.student = student
            internship.status = 'applied'
            internship.save()
            messages.success(request, "Internship details added successfully!")
            return redirect('student_my_internships')
    else:
        form = InternshipForm()
    
    context = {
        'page_title': 'Add Internship',
        'form': form
    }
    return render(request, 'student_template/add_internship.html', context)


# Medical Records
@login_required
def student_medical_records(request):
    """Student view their medical records"""
    student = get_object_or_404(Student, admin=request.user)
    from main_app.models import MedicalRecord
    
    context = {
        'page_title': 'Medical Records',
        'records': MedicalRecord.objects.filter(student=student).order_by('-record_date')
    }
    return render(request, 'student_template/medical_records.html', context)


# Gate Pass
@login_required
def student_gate_pass(request):
    """Student apply for gate pass"""
    student = get_object_or_404(Student, admin=request.user)
    from main_app.models import GatePass
    from main_app.forms import GatePassForm
    
    if request.method == 'POST':
        form = GatePassForm(request.POST)
        if form.is_valid():
            gate_pass = form.save(commit=False)
            gate_pass.student = student
            gate_pass.status = 'pending'
            gate_pass.save()
            messages.success(request, "Gate pass request submitted successfully!")
            return redirect('student_gate_pass')
    else:
        form = GatePassForm()
    
    # Get gate pass statistics
    all_passes = GatePass.objects.filter(student=student)
    total_passes = all_passes.count()
    approved_passes = all_passes.filter(status='approved').count()
    pending_passes = all_passes.filter(status='pending').count()
    rejected_passes = all_passes.filter(status='rejected').count()
    
    # Get recent passes (last 5)
    recent_passes = all_passes.order_by('-created_at')[:5]
    
    context = {
        'page_title': 'Gate Pass Management',
        'form': form,
        'total_passes': total_passes,
        'approved_passes': approved_passes,
        'pending_passes': pending_passes,
        'rejected_passes': rejected_passes,
        'recent_passes': recent_passes,
    }
    return render(request, 'student_template/gate_pass.html', context)


@login_required
def student_my_gate_passes(request):
    """Student view their gate passes"""
    student = get_object_or_404(Student, admin=request.user)
    from main_app.models import GatePass
    
    context = {
        'page_title': 'My Gate Passes',
        'gate_passes': GatePass.objects.filter(student=student).order_by('-created_at')
    }
    return render(request, 'student_template/my_gate_passes.html', context)


# Sports & Activities
@login_required
def student_sports_activities(request):
    """Student view and register for activities"""
    student = get_object_or_404(Student, admin=request.user)
    from main_app.models import SportsActivity, ActivityParticipation
    from datetime import datetime
    
    # Handle registration
    if request.method == 'POST':
        activity_id = request.POST.get('activity_id')
        activity = get_object_or_404(SportsActivity, id=activity_id)
        
        # Check if already registered
        if not ActivityParticipation.objects.filter(activity=activity, student=student).exists():
            ActivityParticipation.objects.create(
                activity=activity,
                student=student,
                achievement_level='participated'
            )
            messages.success(request, f"Successfully registered for {activity.name}!")
        else:
            messages.warning(request, "You are already registered for this activity!")
        return redirect('student_sports_activities')
    
    # Get active activities
    activities = SportsActivity.objects.filter(
        is_active=True,
        registration_deadline__gte=datetime.now().date()
    ).select_related('coordinator')
    
    # Get student's registrations
    registered_ids = ActivityParticipation.objects.filter(student=student).values_list('activity_id', flat=True)
    
    context = {
        'page_title': 'Sports & Cultural Activities',
        'activities': activities,
        'registered_ids': list(registered_ids)
    }
    return render(request, 'student_template/sports_activities.html', context)


@login_required
def student_my_activities(request):
    """Student view their activity participations"""
    student = get_object_or_404(Student, admin=request.user)
    from main_app.models import ActivityParticipation
    
    context = {
        'page_title': 'My Participations',
        'participations': ActivityParticipation.objects.filter(student=student).select_related('activity').order_by('-registered_at')
    }
    return render(request, 'student_template/my_activities.html', context)


# Anti-Ragging
@login_required
def student_report_ragging(request):
    """Student report ragging incident"""
    student = get_object_or_404(Student, admin=request.user)
    from main_app.models import AntiRaggingCommittee
    from main_app.forms import AntiRaggingForm
    
    if request.method == 'POST':
        form = AntiRaggingForm(request.POST, request.FILES)
        if form.is_valid():
            incident = form.save(commit=False)
            if not incident.is_anonymous:
                incident.reporter = student
            incident.status = 'reported'
            incident.save()
            messages.success(request, "Incident reported successfully. The committee will investigate.")
            return redirect('student_home')
    else:
        import random
        incident_number = f"RAG{datetime.now().year}{random.randint(10000, 99999)}"
        form = AntiRaggingForm(initial={'incident_number': incident_number})
    
    context = {
        'page_title': 'Report Ragging Incident',
        'form': form
    }
    return render(request, 'student_template/report_ragging.html', context)


@login_required(login_url='login')
def view_materials(request):
    """Student view study materials"""
    student = get_object_or_404(Student, admin=request.user)
    materials = StudyMaterial.objects.filter(subject__course=student.course).order_by('-created_at')
    
    # Get all subjects for filter dropdown
    subjects = Subject.objects.filter(course=student.course)
    
    context = {
        'page_title': 'Study Materials',
        'materials': materials,
        'student': student,
        'subjects': subjects
    }
    return render(request, 'student_template/view_materials.html', context)


@login_required(login_url='login')
def view_assignments(request):
    """Student view assignments"""
    from django.utils import timezone
    
    student = get_object_or_404(Student, admin=request.user)
    assignments = Assignment.objects.filter(subject__course=student.course).order_by('-due_date')
    
    # Get all submissions for this student
    submissions = AssignmentSubmission.objects.filter(student=student)
    submission_dict = {sub.assignment_id: sub for sub in submissions}
    
    # Build assignment data with submission info
    assignment_data = []
    now = timezone.now()
    
    for assignment in assignments:
        submission = submission_dict.get(assignment.id)
        is_overdue = assignment.due_date < now if not submission else False
        
        # Calculate grade color and percentage if submitted
        grade_color = 'secondary'
        percentage = None
        
        if submission and submission.marks_obtained is not None:
            percentage = round((submission.marks_obtained / assignment.max_marks) * 100, 1)
            if percentage >= 75:
                grade_color = 'success'
            elif percentage >= 50:
                grade_color = 'warning'
            else:
                grade_color = 'danger'
        
        assignment_data.append({
            'assignment': assignment,
            'submission': submission,
            'is_overdue': is_overdue,
            'grade_color': grade_color,
            'percentage': percentage
        })
    
    context = {
        'page_title': 'Assignments',
        'assignment_data': assignment_data,
        'assignments': assignments,  # Keep for backward compatibility
        'student': student
    }
    return render(request, 'student_template/view_assignments.html', context)


@login_required(login_url='login')
def view_submissions(request):
    """Student view their assignment submissions"""
    student = get_object_or_404(Student, admin=request.user)
    submissions = AssignmentSubmission.objects.filter(student=student).order_by('-submitted_at')
    
    context = {
        'page_title': 'My Submissions',
        'submissions': submissions,
        'student': student
    }
    return render(request, 'student_template/view_submissions.html', context)


@login_required(login_url='login')
def view_online_exam(request):
    """Student view online exams"""
    student = get_object_or_404(Student, admin=request.user)
    from main_app.models import Quiz
    quizzes = Quiz.objects.filter(subject__course=student.course, is_active=True).order_by('-created_at')
    
    context = {
        'page_title': 'Online Exams',
        'quizzes': quizzes,
        'student': student
    }
    return render(request, 'student_template/view_online_exam.html', context)


@login_required(login_url='login')
def view_events(request):
    """Student view events"""
    student = get_object_or_404(Student, admin=request.user)
    events = Event.objects.filter(is_approved=True).order_by('-created_at')
    
    context = {
        'page_title': 'Events',
        'events': events,
        'student': student
    }
    return render(request, 'student_template/view_events.html', context)

    context = {
        'page_title': 'Assignments',
        'assignment_data': assignment_data,
        'assignments': assignments,  # Keep for backward compatibility
        'student': student
    }
    return render(request, 'student_template/view_assignments.html', context)


@login_required(login_url='login')
def view_submissions(request):
    """Student view their assignment submissions"""
    student = get_object_or_404(Student, admin=request.user)
    submissions = AssignmentSubmission.objects.filter(student=student).order_by('-submitted_at')
    
    context = {
        'page_title': 'My Submissions',
        'submissions': submissions,
        'student': student
    }
    return render(request, 'student_template/view_submissions.html', context)


@login_required(login_url='login')
def view_online_exam(request):
    """Student view online exams"""
    student = get_object_or_404(Student, admin=request.user)
    from main_app.models import Quiz
    quizzes = Quiz.objects.filter(subject__course=student.course, is_active=True).order_by('-created_at')
    
    context = {
        'page_title': 'Online Exams',
        'quizzes': quizzes,
        'student': student
    }
    return render(request, 'student_template/view_online_exam.html', context)


@login_required(login_url='login')
def view_events(request):
    """Student view events"""
    student = get_object_or_404(Student, admin=request.user)
    events = Event.objects.filter(is_approved=True).order_by('-created_at')
    
    context = {
        'page_title': 'Events',
        'events': events,
        'student': student
    }
    return render(request, 'student_template/view_events.html', context)
