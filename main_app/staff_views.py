import json
from datetime import datetime

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse, JsonResponse
from django.shortcuts import (HttpResponseRedirect, get_object_or_404,redirect, render)
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt

from .forms import *
from .models import *


def staff_home(request):
    staff = get_object_or_404(Staff, admin=request.user)
    total_students = Student.objects.filter(course=staff.course).count()
    total_leave = LeaveReportStaff.objects.filter(staff=staff).count()
    subjects = Subject.objects.filter(staff=staff)
    total_subject = subjects.count()
    attendance_list = Attendance.objects.filter(subject__in=subjects)
    total_attendance = attendance_list.count()
    attendance_list = []
    subject_list = []
    for subject in subjects:
        attendance_count = Attendance.objects.filter(subject=subject).count()
        subject_list.append(subject.name)
        attendance_list.append(attendance_count)
    
    # Proctor-specific data
    total_mentees = 0
    low_attendance_mentees = 0
    if staff.is_proctor:
        total_mentees = ProctorAssignment.objects.filter(staff=staff, is_active=True).count()
        # Get students with low attendance
        mentees = ProctorAssignment.objects.filter(staff=staff, is_active=True)
        for mentee in mentees:
            total_att = AttendanceReport.objects.filter(student=mentee.student).count()
            if total_att > 0:
                present = AttendanceReport.objects.filter(student=mentee.student, status=True).count()
                if (present / total_att) * 100 < 75:
                    low_attendance_mentees += 1
    
    # Unread messages
    unread_messages = Message.objects.filter(receiver=request.user, is_read=False).count()
    
    # Pending assignments
    pending_assignments = Assignment.objects.filter(staff=staff, due_date__gte=datetime.now()).count()
    
    context = {
        'page_title': 'Staff Panel - ' + str(staff.admin.last_name) + ' (' + str(staff.course) + ')',
        'total_students': total_students,
        'total_attendance': total_attendance,
        'total_leave': total_leave,
        'total_subject': total_subject,
        'subject_list': subject_list,
        'attendance_list': attendance_list,
        'is_proctor': staff.is_proctor,
        'total_mentees': total_mentees,
        'low_attendance_mentees': low_attendance_mentees,
        'unread_messages': unread_messages,
        'pending_assignments': pending_assignments,
    }
    return render(request, 'staff_template/home_content.html', context)


def staff_take_attendance(request):
    staff = get_object_or_404(Staff, admin=request.user)
    subjects = Subject.objects.filter(staff_id=staff)
    sessions = Session.objects.all()
    context = {
        'subjects': subjects,
        'sessions': sessions,
        'page_title': 'Take Attendance'
    }

    return render(request, 'staff_template/staff_take_attendance.html', context)


@csrf_exempt
def get_students(request):
    subject_id = request.POST.get('subject')
    session_id = request.POST.get('session')
    try:
        subject = get_object_or_404(Subject, id=subject_id)
        session = get_object_or_404(Session, id=session_id)
        students = Student.objects.filter(
            course_id=subject.course.id, session=session)
        student_data = []
        for student in students:
            data = {
                    "id": student.id,
                    "name": student.admin.last_name + " " + student.admin.first_name
                    }
            student_data.append(data)
        return JsonResponse(json.dumps(student_data), content_type='application/json', safe=False)
    except Exception as e:
        return e


@csrf_exempt
def save_attendance(request):
    student_data = request.POST.get('student_ids')
    date = request.POST.get('date')
    subject_id = request.POST.get('subject')
    session_id = request.POST.get('session')
    students = json.loads(student_data)
    try:
        session = get_object_or_404(Session, id=session_id)
        subject = get_object_or_404(Subject, id=subject_id)
        attendance = Attendance(session=session, subject=subject, date=date)
        attendance.save()

        for student_dict in students:
            student = get_object_or_404(Student, id=student_dict.get('id'))
            attendance_report = AttendanceReport(student=student, attendance=attendance, status=student_dict.get('status'))
            attendance_report.save()
    except Exception as e:
        return None

    return HttpResponse("OK")


def staff_update_attendance(request):
    staff = get_object_or_404(Staff, admin=request.user)
    subjects = Subject.objects.filter(staff_id=staff)
    sessions = Session.objects.all()
    context = {
        'subjects': subjects,
        'sessions': sessions,
        'page_title': 'Update Attendance'
    }

    return render(request, 'staff_template/staff_update_attendance.html', context)


@csrf_exempt
def get_student_attendance(request):
    attendance_date_id = request.POST.get('attendance_date_id')
    try:
        date = get_object_or_404(Attendance, id=attendance_date_id)
        attendance_data = AttendanceReport.objects.filter(attendance=date)
        student_data = []
        for attendance in attendance_data:
            data = {"id": attendance.student.admin.id,
                    "name": attendance.student.admin.last_name + " " + attendance.student.admin.first_name,
                    "status": attendance.status}
            student_data.append(data)
        return JsonResponse(json.dumps(student_data), content_type='application/json', safe=False)
    except Exception as e:
        return e


@csrf_exempt
def update_attendance(request):
    student_data = request.POST.get('student_ids')
    date = request.POST.get('date')
    students = json.loads(student_data)
    try:
        attendance = get_object_or_404(Attendance, id=date)

        for student_dict in students:
            student = get_object_or_404(
                Student, admin_id=student_dict.get('id'))
            attendance_report = get_object_or_404(AttendanceReport, student=student, attendance=attendance)
            attendance_report.status = student_dict.get('status')
            attendance_report.save()
    except Exception as e:
        return None

    return HttpResponse("OK")


def staff_apply_leave(request):
    form = LeaveReportStaffForm(request.POST or None)
    staff = get_object_or_404(Staff, admin_id=request.user.id)
    context = {
        'form': form,
        'leave_history': LeaveReportStaff.objects.filter(staff=staff),
        'page_title': 'Apply for Leave'
    }
    if request.method == 'POST':
        if form.is_valid():
            try:
                obj = form.save(commit=False)
                obj.staff = staff
                obj.save()
                messages.success(
                    request, "Application for leave has been submitted for review")
                return redirect(reverse('staff_apply_leave'))
            except Exception:
                messages.error(request, "Could not apply!")
        else:
            messages.error(request, "Form has errors!")
    return render(request, "staff_template/staff_apply_leave.html", context)


def staff_feedback(request):
    form = FeedbackStaffForm(request.POST or None)
    staff = get_object_or_404(Staff, admin_id=request.user.id)
    context = {
        'form': form,
        'feedbacks': FeedbackStaff.objects.filter(staff=staff),
        'page_title': 'Add Feedback'
    }
    if request.method == 'POST':
        if form.is_valid():
            try:
                obj = form.save(commit=False)
                obj.staff = staff
                obj.save()
                messages.success(request, "Feedback submitted for review")
                return redirect(reverse('staff_feedback'))
            except Exception:
                messages.error(request, "Could not Submit!")
        else:
            messages.error(request, "Form has errors!")
    return render(request, "staff_template/staff_feedback.html", context)


def staff_view_profile(request):
    staff = get_object_or_404(Staff, admin=request.user)
    form = StaffEditForm(request.POST or None, request.FILES or None,instance=staff)
    context = {'form': form, 'page_title': 'View/Update Profile'}
    if request.method == 'POST':
        try:
            if form.is_valid():
                first_name = form.cleaned_data.get('first_name')
                last_name = form.cleaned_data.get('last_name')
                password = form.cleaned_data.get('password') or None
                address = form.cleaned_data.get('address')
                gender = form.cleaned_data.get('gender')
                passport = request.FILES.get('profile_pic') or None
                admin = staff.admin
                if password != None:
                    admin.set_password(password)
                if passport != None:
                    fs = FileSystemStorage()
                    filename = fs.save(passport.name, passport)
                    passport_url = fs.url(filename)
                    admin.profile_pic = passport_url
                admin.first_name = first_name
                admin.last_name = last_name
                admin.address = address
                admin.gender = gender
                admin.save()
                staff.save()
                messages.success(request, "Profile Updated!")
                return redirect(reverse('staff_view_profile'))
            else:
                messages.error(request, "Invalid Data Provided")
                return render(request, "staff_template/staff_view_profile.html", context)
        except Exception as e:
            messages.error(
                request, "Error Occured While Updating Profile " + str(e))
            return render(request, "staff_template/staff_view_profile.html", context)

    return render(request, "staff_template/staff_view_profile.html", context)


@csrf_exempt
def staff_fcmtoken(request):
    token = request.POST.get('token')
    try:
        staff_user = get_object_or_404(CustomUser, id=request.user.id)
        staff_user.fcm_token = token
        staff_user.save()
        return HttpResponse("True")
    except Exception as e:
        return HttpResponse("False")


def staff_view_notification(request):
    staff = get_object_or_404(Staff, admin=request.user)
    notifications = NotificationStaff.objects.filter(staff=staff)
    context = {
        'notifications': notifications,
        'page_title': "View Notifications"
    }
    return render(request, "staff_template/staff_view_notification.html", context)


def staff_add_result(request):
    staff = get_object_or_404(Staff, admin=request.user)
    subjects = Subject.objects.filter(staff=staff)
    sessions = Session.objects.all()
    context = {
        'page_title': 'Result Upload',
        'subjects': subjects,
        'sessions': sessions
    }
    if request.method == 'POST':
        try:
            student_id = request.POST.get('student_list')
            subject_id = request.POST.get('subject')
            test = request.POST.get('test')
            exam = request.POST.get('exam')
            student = get_object_or_404(Student, id=student_id)
            subject = get_object_or_404(Subject, id=subject_id)
            try:
                data = StudentResult.objects.get(
                    student=student, subject=subject)
                data.exam = exam
                data.test = test
                data.save()
                messages.success(request, "Scores Updated")
            except:
                result = StudentResult(student=student, subject=subject, test=test, exam=exam)
                result.save()
                messages.success(request, "Scores Saved")
        except Exception as e:
            messages.warning(request, "Error Occured While Processing Form")
    return render(request, "staff_template/staff_add_result.html", context)


@csrf_exempt
def fetch_student_result(request):
    try:
        subject_id = request.POST.get('subject')
        student_id = request.POST.get('student')
        student = get_object_or_404(Student, id=student_id)
        subject = get_object_or_404(Subject, id=subject_id)
        result = StudentResult.objects.get(student=student, subject=subject)
        result_data = {
            'exam': result.exam,
            'test': result.test
        }
        return HttpResponse(json.dumps(result_data))
    except Exception as e:
        return HttpResponse('False')


# ==================== FACULTY TIMETABLE ====================

def staff_view_timetable(request):
    """View my weekly teaching timetable"""
    staff = get_object_or_404(Staff, admin=request.user)
    
    # Get all timetable slots assigned to this staff
    timetable = Timetable.objects.filter(staff=staff).order_by('weekday', 'period')
    
    # Organize by weekday
    weekdays = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday']
    organized_timetable = {}
    
    for day in weekdays:
        organized_timetable[day] = timetable.filter(weekday=day)
    
    context = {
        'page_title': 'My Teaching Timetable',
        'timetable': organized_timetable,
        'staff': staff
    }
    return render(request, 'staff_template/view_timetable.html', context)


# ==================== FACULTY EXAM DUTIES ====================

def staff_my_exam_duties(request):
    """View my invigilation duties"""
    staff = get_object_or_404(Staff, admin=request.user)
    
    # Get all invigilation assignments
    duties = Invigilator.objects.filter(staff=staff).order_by('exam_schedule__exam_date')
    
    context = {
        'page_title': 'My Exam Duties',
        'duties': duties,
        'staff': staff
    }
    return render(request, 'staff_template/my_exam_duties.html', context)


def staff_upload_question_paper(request, schedule_id):
    """Upload question paper for exam"""
    staff = get_object_or_404(Staff, admin=request.user)
    schedule = get_object_or_404(ExamSchedule, id=schedule_id)
    
    # Check if staff teaches this subject
    if schedule.subject.staff != staff:
        messages.error(request, "You are not authorized to upload question paper for this subject!")
        return redirect('staff_my_exam_duties')
    
    if request.method == 'POST' and request.FILES.get('question_paper'):
        schedule.question_paper = request.FILES['question_paper']
        schedule.save()
        messages.success(request, "Question paper uploaded successfully!")
        return redirect('staff_my_exam_duties')
    
    context = {
        'page_title': 'Upload Question Paper',
        'schedule': schedule,
        'staff': staff
    }
    return render(request, 'staff_template/upload_question_paper.html', context)


def staff_upload_answer_key(request, schedule_id):
    """Upload answer key for exam"""
    staff = get_object_or_404(Staff, admin=request.user)
    schedule = get_object_or_404(ExamSchedule, id=schedule_id)
    
    # Check if staff teaches this subject
    if schedule.subject.staff != staff:
        messages.error(request, "You are not authorized to upload answer key for this subject!")
        return redirect('staff_my_exam_duties')
    
    if request.method == 'POST' and request.FILES.get('answer_key'):
        schedule.answer_key = request.FILES['answer_key']
        schedule.save()
        messages.success(request, "Answer key uploaded successfully!")
        return redirect('staff_my_exam_duties')
    
    context = {
        'page_title': 'Upload Answer Key',
        'schedule': schedule,
        'staff': staff
    }
    return render(request, 'staff_template/upload_answer_key.html', context)


# ==================== FACULTY RESULT ENTRY ====================

def staff_enter_marks(request):
    """Enter semester results"""
    staff = get_object_or_404(Staff, admin=request.user)
    
    # Get subjects taught by this staff
    subjects = Subject.objects.filter(staff=staff)
    
    if request.method == 'POST':
        semester_result_id = request.POST.get('semester_result')
        subject_id = request.POST.get('subject')
        internal_marks = request.POST.get('internal_marks')
        external_marks = request.POST.get('external_marks')
        max_marks = request.POST.get('max_marks', 100)
        grade = request.POST.get('grade')
        credits = request.POST.get('credits', 3)
        
        semester_result = get_object_or_404(SemesterResult, id=semester_result_id)
        subject = get_object_or_404(Subject, id=subject_id)
        
        # Create or update subject result
        subject_result, created = SubjectResult.objects.update_or_create(
            semester_result=semester_result,
            subject=subject,
            defaults={
                'internal_marks': internal_marks,
                'external_marks': external_marks,
                'max_marks': max_marks,
                'grade': grade,
                'credits': credits
            }
        )
        
        messages.success(request, f"Marks entered for {subject.name} successfully!")
        return redirect('staff_enter_marks')
    
    # Get all semester results for students in staff's subjects
    students_in_subjects = Student.objects.filter(course__in=[s.course for s in subjects]).distinct()
    semester_results = SemesterResult.objects.filter(student__in=students_in_subjects, is_published=False)
    
    context = {
        'page_title': 'Enter Marks',
        'subjects': subjects,
        'semester_results': semester_results,
        'staff': staff
    }
    return render(request, 'staff_template/enter_marks.html', context)


def staff_view_results(request):
    """View entered results"""
    staff = get_object_or_404(Staff, admin=request.user)
    
    # Get all subject results for subjects taught by this staff
    subjects = Subject.objects.filter(staff=staff)
    subject_results = SubjectResult.objects.filter(subject__in=subjects).order_by('-semester_result__session', '-semester_result__semester')
    
    context = {
        'page_title': 'View Results',
        'subject_results': subject_results,
        'staff': staff
    }
    return render(request, 'staff_template/view_results.html', context)


# ==================== FACULTY LIBRARY MANAGEMENT ====================

def staff_library_issue_return(request):
    """Issue/Return library books (for librarians)"""
    staff = get_object_or_404(Staff, admin=request.user)
    
    # Check permission
    if not staff.can_manage_library:
        messages.error(request, "You don't have permission to manage library!")
        return redirect('staff_home')
    
    # Get active issues
    active_issues = LibraryIssue.objects.filter(status__in=['issued', 'overdue']).order_by('-issue_date')
    
    context = {
        'page_title': 'Library Issue/Return',
        'active_issues': active_issues,
        'staff': staff
    }
    return render(request, 'staff_template/library_issue_return.html', context)


# ==================== FACULTY PLACEMENT COORDINATION ====================

def staff_manage_placements(request):
    """Manage placement drives (for placement coordinators)"""
    staff = get_object_or_404(Staff, admin=request.user)
    
    # Check permission
    if not staff.can_manage_placement:
        messages.error(request, "You don't have permission to manage placements!")
        return redirect('staff_home')
    
    # Get drives coordinated by this staff
    drives = PlacementDrive.objects.filter(coordinator=staff).order_by('-created_at')
    
    context = {
        'page_title': 'Manage Placement Drives',
        'drives': drives,
        'staff': staff
    }
    return render(request, 'staff_template/manage_placements.html', context)


# ==================== FACULTY GRIEVANCE HANDLING ====================

def staff_my_assigned_grievances(request):
    """View grievances assigned to me"""
    staff = get_object_or_404(Staff, admin=request.user)
    
    grievances = Grievance.objects.filter(assigned_to=staff).order_by('-submitted_at')
    
    # Statistics
    pending = grievances.filter(status='in_progress').count()
    resolved = grievances.filter(status='resolved').count()
    
    context = {
        'page_title': 'My Assigned Grievances',
        'grievances': grievances,
        'pending': pending,
        'resolved': resolved,
        'staff': staff
    }
    return render(request, 'staff_template/my_assigned_grievances.html', context)


def staff_resolve_grievance(request, grievance_id):
    """Resolve assigned grievance"""
    staff = get_object_or_404(Staff, admin=request.user)
    grievance = get_object_or_404(Grievance, id=grievance_id, assigned_to=staff)
    
    if request.method == 'POST':
        resolution = request.POST.get('resolution')
        
        from django.utils import timezone
        grievance.resolution = resolution
        grievance.status = 'resolved'
        grievance.resolved_at = timezone.now()
        grievance.save()
        
        messages.success(request, "Grievance resolved successfully!")
        return redirect('staff_my_assigned_grievances')
    
    context = {
        'page_title': 'Resolve Grievance',
        'grievance': grievance,
        'staff': staff
    }
    return render(request, 'staff_template/resolve_grievance.html', context)


# ============================================================================
# NEW ECAP FEATURES - STAFF VIEWS
# ============================================================================

# Online Examination
@login_required
def staff_my_online_exams(request):
    """Staff view their created online exams"""
    staff = get_object_or_404(Staff, admin=request.user)
    from main_app.models import OnlineExam
    
    context = {
        'page_title': 'My Online Exams',
        'exams': OnlineExam.objects.filter(created_by=staff).select_related('subject', 'course').order_by('-created_at')
    }
    return render(request, 'staff_template/my_online_exams.html', context)


@login_required
def staff_create_online_exam(request):
    """Staff create online exam for their subjects"""
    staff = get_object_or_404(Staff, admin=request.user)
    from main_app.models import OnlineExam
    from main_app.forms import OnlineExamForm
    
    if request.method == 'POST':
        form = OnlineExamForm(request.POST)
        if form.is_valid():
            exam = form.save(commit=False)
            exam.created_by = staff
            exam.save()
            messages.success(request, "Online exam created successfully!")
            return redirect('staff_my_online_exams')
    else:
        # Filter subjects taught by this staff
        form = OnlineExamForm()
        form.fields['subject'].queryset = Subject.objects.filter(staff=staff)
    
    context = {
        'page_title': 'Create Online Exam',
        'form': form
    }
    return render(request, 'staff_template/create_online_exam.html', context)


# Research & Publications
@login_required
def staff_my_research(request):
    """Staff view their research publications"""
    staff = get_object_or_404(Staff, admin=request.user)
    from main_app.models import Research
    
    context = {
        'page_title': 'My Publications',
        'publications': Research.objects.filter(staff=staff).order_by('-publication_date')
    }
    return render(request, 'staff_template/my_research.html', context)


@login_required
def staff_add_research(request):
    """Staff add research publication"""
    staff = get_object_or_404(Staff, admin=request.user)
    from main_app.models import Research
    from main_app.forms import ResearchForm
    
    if request.method == 'POST':
        form = ResearchForm(request.POST, request.FILES)
        if form.is_valid():
            research = form.save(commit=False)
            research.staff = staff
            research.save()
            messages.success(request, "Publication added successfully!")
            return redirect('staff_my_research')
    else:
        form = ResearchForm()
    
    context = {
        'page_title': 'Add Publication',
        'form': form
    }
    return render(request, 'staff_template/add_research.html', context)


# Gate Pass Approvals
@login_required
def staff_gate_pass_approvals(request):
    """Staff view and approve gate pass requests"""
    from main_app.models import GatePass
    
    if request.method == 'POST':
        pass_id = request.POST.get('pass_id')
        action = request.POST.get('action')
        gate_pass = get_object_or_404(GatePass, id=pass_id)
        
        if action == 'approve':
            gate_pass.status = 'approved'
            gate_pass.approved_by = request.user.staff
            from datetime import datetime
            gate_pass.approval_date = datetime.now()
            messages.success(request, "Gate pass approved!")
        elif action == 'reject':
            gate_pass.status = 'rejected'
            messages.success(request, "Gate pass rejected!")
        gate_pass.save()
        return redirect('staff_gate_pass_approvals')
    
    context = {
        'page_title': 'Gate Pass Requests',
        'gate_passes': GatePass.objects.filter(status='pending').select_related('student').order_by('-created_at')
    }
    return render(request, 'staff_template/gate_pass_approvals.html', context)
