import json
from datetime import datetime

from django.contrib import messages
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse, JsonResponse
from django.shortcuts import (HttpResponseRedirect, get_object_or_404,redirect, render)
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt

from .forms import *
from .models import *


def staff_home(request):
    from datetime import datetime
    
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
    
    # Today's timetable
    today = datetime.now()
    weekday_name = today.strftime('%A').lower()
    today_timetable = Timetable.objects.filter(
        staff=staff,
        weekday=weekday_name
    ).select_related('subject', 'course').order_by('period')
    
    # Pending assignments
    pending_assignments = Assignment.objects.filter(staff=staff, due_date__gte=datetime.now()).count()
    
    # Get current date
    from django.utils import timezone
    current_date = timezone.now()
    
    context = {
        'page_title': 'Staff Panel - ' + str(staff.admin.last_name) + ' (' + str(staff.course) + ')',
        'staff': staff,
        'subjects': subjects,
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
        'current_date': current_date,
        'today_timetable': today_timetable,
        'subject_count': total_subject,
        'pending_count': unread_messages,
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


@login_required(login_url='/')
def bulk_attendance_import(request):
    """Bulk import attendance from Excel/CSV file"""
    staff = get_object_or_404(Staff, admin=request.user)
    
    if request.method == 'POST' and request.FILES.get('attendance_file'):
        import pandas as pd
        from datetime import datetime
        
        try:
            file = request.FILES['attendance_file']
            subject_id = request.POST.get('subject')
            session_id = request.POST.get('session')
            attendance_date = request.POST.get('date')
            
            # Validate inputs
            if not all([subject_id, session_id, attendance_date]):
                messages.error(request, 'Please provide subject, session, and date')
                return redirect('bulk_attendance_import')
            
            subject = get_object_or_404(Subject, id=subject_id)
            session = get_object_or_404(Session, id=session_id)
            
            # Read Excel/CSV file
            if file.name.endswith('.csv'):
                df = pd.read_csv(file)
            else:
                df = pd.read_excel(file)
            
            # Expected columns: roll_number, status (Present/Absent or 1/0)
            if 'roll_number' not in df.columns or 'status' not in df.columns:
                messages.error(request, 'File must contain "roll_number" and "status" columns')
                return redirect('bulk_attendance_import')
            
            # Create or get attendance record
            attendance, created = Attendance.objects.get_or_create(
                session=session,
                subject=subject,
                date=attendance_date
            )
            
            # Process each row
            success_count = 0
            error_count = 0
            
            for _, row in df.iterrows():
                try:
                    student = Student.objects.get(
                        roll_number=row['roll_number'],
                        course=subject.course,
                        session=session
                    )
                    
                    # Parse status (Present/Absent or 1/0)
                    status_value = str(row['status']).strip().lower()
                    if status_value in ['present', '1', 'p', 'yes']:
                        status = True
                    elif status_value in ['absent', '0', 'a', 'no']:
                        status = False
                    else:
                        error_count += 1
                        continue
                    
                    # Create or update attendance report
                    attendance_report, created = AttendanceReport.objects.update_or_create(
                        student=student,
                        attendance=attendance,
                        defaults={'status': status}
                    )
                    success_count += 1
                    
                except Student.DoesNotExist:
                    error_count += 1
                    continue
                except Exception as e:
                    error_count += 1
                    continue
            
            messages.success(request, f'Attendance imported successfully! {success_count} records processed, {error_count} errors')
            return redirect('staff_take_attendance')
            
        except Exception as e:
            messages.error(request, f'Error processing file: {str(e)}')
            return redirect('bulk_attendance_import')
    
    # GET request - show form
    subjects = Subject.objects.filter(staff_id=staff)
    sessions = Session.objects.all()
    context = {
        'subjects': subjects,
        'sessions': sessions,
        'page_title': 'Bulk Import Attendance'
    }
    return render(request, 'staff_template/bulk_attendance_import.html', context)


@login_required(login_url='/')
def generate_attendance_qr(request):
    """Generate QR code for attendance session"""
    import qrcode
    from io import BytesIO
    import base64
    from django.core.files.base import ContentFile
    
    staff = get_object_or_404(Staff, admin=request.user)
    
    if request.method == 'POST':
        subject_id = request.POST.get('subject')
        session_id = request.POST.get('session')
        date = request.POST.get('date')
        
        try:
            subject = get_object_or_404(Subject, id=subject_id)
            session = get_object_or_404(Session, id=session_id)
            
            # Create or get attendance record
            attendance, created = Attendance.objects.get_or_create(
                session=session,
                subject=subject,
                date=date
            )
            
            # Generate QR code data (attendance ID + verification code)
            import hashlib
            verification_code = hashlib.md5(f"{attendance.id}{date}{subject.id}".encode()).hexdigest()[:8]
            qr_data = f"ATTENDANCE:{attendance.id}:{verification_code}"
            
            # Generate QR code
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(qr_data)
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")
            
            # Convert to base64 for display
            buffer = BytesIO()
            img.save(buffer, format='PNG')
            img_str = base64.b64encode(buffer.getvalue()).decode()
            
            context = {
                'qr_code': img_str,
                'attendance': attendance,
                'subject': subject,
                'date': date,
                'verification_code': verification_code,
                'page_title': 'Attendance QR Code'
            }
            return render(request, 'staff_template/attendance_qr.html', context)
            
        except Exception as e:
            messages.error(request, f'Error generating QR code: {str(e)}')
    
    # GET request - show form
    subjects = Subject.objects.filter(staff_id=staff)
    sessions = Session.objects.all()
    context = {
        'subjects': subjects,
        'sessions': sessions,
        'page_title': 'Generate Attendance QR Code'
    }
    return render(request, 'staff_template/generate_qr.html', context)


@login_required(login_url='/')
def attendance_analytics(request):
    """Comprehensive attendance analytics dashboard"""
    from django.db.models import Count, Q, Avg
    from datetime import datetime, timedelta
    
    staff = get_object_or_404(Staff, admin=request.user)
    subjects = Subject.objects.filter(staff_id=staff)
    
    # Get selected filters
    subject_id = request.GET.get('subject')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    # Default to current month
    if not start_date:
        start_date = datetime.now().replace(day=1).strftime('%Y-%m-%d')
    if not end_date:
        end_date = datetime.now().strftime('%Y-%m-%d')
    
    # Build query
    attendance_query = AttendanceReport.objects.all()
    
    if subject_id:
        attendance_query = attendance_query.filter(attendance__subject_id=subject_id)
    else:
        # Filter by staff's subjects
        attendance_query = attendance_query.filter(attendance__subject__in=subjects)
    
    attendance_query = attendance_query.filter(
        attendance__date__gte=start_date,
        attendance__date__lte=end_date
    )
    
    # Calculate statistics
    total_classes = attendance_query.values('attendance').distinct().count()
    total_records = attendance_query.count()
    present_count = attendance_query.filter(status=True).count()
    absent_count = total_records - present_count
    attendance_percentage = round((present_count / total_records * 100), 2) if total_records > 0 else 0
    
    # Subject-wise breakdown
    subject_stats = []
    for subject in subjects:
        subject_attendance = AttendanceReport.objects.filter(
            attendance__subject=subject,
            attendance__date__gte=start_date,
            attendance__date__lte=end_date
        )
        total = subject_attendance.count()
        present = subject_attendance.filter(status=True).count()
        percentage = round((present / total * 100), 2) if total > 0 else 0
        
        subject_stats.append({
            'subject': subject.name,
            'total_classes': subject_attendance.values('attendance').distinct().count(),
            'total_records': total,
            'present': present,
            'absent': total - present,
            'percentage': percentage
        })
    
    # Low attendance students (<75%)
    low_attendance_students = []
    all_students = Student.objects.filter(course__in=subjects.values_list('course', flat=True).distinct())
    
    for student in all_students[:50]:  # Limit to 50 for performance
        student_attendance = AttendanceReport.objects.filter(
            student=student,
            attendance__date__gte=start_date,
            attendance__date__lte=end_date
        )
        total = student_attendance.count()
        if total > 0:
            present = student_attendance.filter(status=True).count()
            percentage = round((present / total * 100), 2)
            if percentage < 75:
                low_attendance_students.append({
                    'student': student,
                    'percentage': percentage,
                    'total': total,
                    'present': present,
                    'absent': total - present
                })
    
    # Sort by percentage (lowest first)
    low_attendance_students = sorted(low_attendance_students, key=lambda x: x['percentage'])
    
    # Daily attendance trend (last 30 days)
    daily_trend = []
    for i in range(30):
        date = (datetime.now() - timedelta(days=29-i)).date()
        day_attendance = AttendanceReport.objects.filter(
            attendance__subject__in=subjects,
            attendance__date=date
        )
        total = day_attendance.count()
        present = day_attendance.filter(status=True).count()
        percentage = round((present / total * 100), 2) if total > 0 else 0
        
        daily_trend.append({
            'date': date.strftime('%Y-%m-%d'),
            'percentage': percentage
        })
    
    context = {
        'subjects': subjects,
        'selected_subject': subject_id,
        'start_date': start_date,
        'end_date': end_date,
        'total_classes': total_classes,
        'total_records': total_records,
        'present_count': present_count,
        'absent_count': absent_count,
        'attendance_percentage': attendance_percentage,
        'subject_stats': subject_stats,
        'low_attendance_students': low_attendance_students,
        'daily_trend': daily_trend,
        'page_title': 'Attendance Analytics'
    }
    
    return render(request, 'staff_template/attendance_analytics.html', context)


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
            
            # Validate marks
            try:
                test_marks = float(test) if test else 0
                exam_marks = float(exam) if exam else 0
                
                if test_marks < 0 or test_marks > 30:
                    messages.error(request, "Internal marks must be between 0 and 30")
                    return render(request, "staff_template/staff_add_result.html", context)
                
                if exam_marks < 0 or exam_marks > 70:
                    messages.error(request, "External marks must be between 0 and 70")
                    return render(request, "staff_template/staff_add_result.html", context)
                    
            except ValueError:
                messages.error(request, "Please enter valid numbers for marks")
                return render(request, "staff_template/staff_add_result.html", context)
            
            student = get_object_or_404(Student, id=student_id)
            subject = get_object_or_404(Subject, id=subject_id)
            
            try:
                data = StudentResult.objects.get(
                    student=student, subject=subject)
                data.exam = exam_marks
                data.test = test_marks
                data.save()
                messages.success(request, f"Scores Updated for {student.admin.first_name} {student.admin.last_name}")
            except:
                result = StudentResult(student=student, subject=subject, test=test_marks, exam=exam_marks)
                result.save()
                messages.success(request, f"Scores Saved for {student.admin.first_name} {student.admin.last_name}")
        except Exception as e:
            messages.error(request, f"Error occurred while processing form: {str(e)}")
    return render(request, "staff_template/staff_add_result.html", context)


@login_required(login_url='/')
def bulk_marks_import(request):
    """Bulk import marks from Excel/CSV file"""
    staff = get_object_or_404(Staff, admin=request.user)
    
    if request.method == 'POST' and request.FILES.get('marks_file'):
        import pandas as pd
        
        try:
            file = request.FILES['marks_file']
            subject_id = request.POST.get('subject')
            exam_type = request.POST.get('exam_type')  # internal or external
            
            if not all([subject_id, exam_type]):
                messages.error(request, 'Please provide subject and exam type')
                return redirect('bulk_marks_import')
            
            subject = get_object_or_404(Subject, id=subject_id, staff=staff)
            
            # Read file
            if file.name.endswith('.csv'):
                df = pd.read_csv(file)
            else:
                df = pd.read_excel(file)
            
            # Expected columns: roll_number, marks
            if 'roll_number' not in df.columns or 'marks' not in df.columns:
                messages.error(request, 'File must contain "roll_number" and "marks" columns')
                return redirect('bulk_marks_import')
            
            # Process each row
            success_count = 0
            error_count = 0
            errors_list = []
            
            for _, row in df.iterrows():
                try:
                    student = Student.objects.get(
                        roll_number=row['roll_number'],
                        course=subject.course
                    )
                    
                    marks = float(row['marks'])
                    
                    # Validate marks based on exam type
                    if exam_type == 'internal' and (marks < 0 or marks > 30):
                        errors_list.append(f"{row['roll_number']}: Internal marks must be 0-30")
                        error_count += 1
                        continue
                    elif exam_type == 'external' and (marks < 0 or marks > 70):
                        errors_list.append(f"{row['roll_number']}: External marks must be 0-70")
                        error_count += 1
                        continue
                    
                    # Update or create result
                    result, created = StudentResult.objects.get_or_create(
                        student=student,
                        subject=subject
                    )
                    
                    if exam_type == 'internal':
                        result.test = marks
                    else:
                        result.exam = marks
                    
                    result.save()
                    success_count += 1
                    
                except Student.DoesNotExist:
                    errors_list.append(f"{row['roll_number']}: Student not found")
                    error_count += 1
                except ValueError:
                    errors_list.append(f"{row['roll_number']}: Invalid marks value")
                    error_count += 1
                except Exception as e:
                    errors_list.append(f"{row['roll_number']}: {str(e)}")
                    error_count += 1
            
            if errors_list:
                error_msg = f'{success_count} marks imported. {error_count} errors: ' + '; '.join(errors_list[:5])
                if len(errors_list) > 5:
                    error_msg += f' ...and {len(errors_list) - 5} more'
                messages.warning(request, error_msg)
            else:
                messages.success(request, f'All marks imported successfully! {success_count} records processed')
            
            return redirect('staff_add_result')
            
        except Exception as e:
            messages.error(request, f'Error processing file: {str(e)}')
            return redirect('bulk_marks_import')
    
    # GET request
    subjects = Subject.objects.filter(staff=staff)
    context = {
        'subjects': subjects,
        'page_title': 'Bulk Import Marks'
    }
    return render(request, 'staff_template/bulk_marks_import.html', context)


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
            'test': result.test,
            'total': result.test + result.exam,
            'grade': calculate_grade(result.test + result.exam)
        }
        return HttpResponse(json.dumps(result_data))
    except Exception as e:
        return HttpResponse('False')


def calculate_grade(marks):
    """Calculate grade based on marks"""
    if marks >= 90:
        return 'A+'
    elif marks >= 80:
        return 'A'
    elif marks >= 70:
        return 'B+'
    elif marks >= 60:
        return 'B'
    elif marks >= 50:
        return 'C+'
    elif marks >= 40:
        return 'C'
    else:
        return 'F'


def calculate_grade_point(marks):
    """Calculate grade point for CGPA calculation"""
    if marks >= 90:
        return 10.0
    elif marks >= 80:
        return 9.0
    elif marks >= 70:
        return 8.0
    elif marks >= 60:
        return 7.0
    elif marks >= 50:
        return 6.0
    elif marks >= 40:
        return 5.0
    else:
        return 0.0


@login_required(login_url='/')
def calculate_student_cgpa(request, student_id):
    """Calculate and display student CGPA"""
    student = get_object_or_404(Student, id=student_id)
    
    # Get all results for student
    results = StudentResult.objects.filter(student=student).select_related('subject')
    
    if not results.exists():
        messages.warning(request, 'No results found for CGPA calculation')
        return redirect('staff_view_results')
    
    # Calculate semester-wise and overall CGPA
    semester_data = {}
    total_credits = 0
    total_grade_points = 0
    
    for result in results:
        total_marks = result.test + result.exam
        grade = calculate_grade(total_marks)
        grade_point = calculate_grade_point(total_marks)
        
        # Assume 3 credits per subject (can be made configurable)
        credits = getattr(result.subject, 'credits', 3)
        
        semester = getattr(result, 'semester', 1)
        if semester not in semester_data:
            semester_data[semester] = {
                'results': [],
                'total_credits': 0,
                'total_points': 0
            }
        
        semester_data[semester]['results'].append({
            'subject': result.subject,
            'internal': result.test,
            'external': result.exam,
            'total': total_marks,
            'grade': grade,
            'grade_point': grade_point,
            'credits': credits
        })
        
        semester_data[semester]['total_credits'] += credits
        semester_data[semester]['total_points'] += (grade_point * credits)
        total_credits += credits
        total_grade_points += (grade_point * credits)
    
    # Calculate SGPA for each semester
    for semester in semester_data:
        if semester_data[semester]['total_credits'] > 0:
            semester_data[semester]['sgpa'] = round(
                semester_data[semester]['total_points'] / semester_data[semester]['total_credits'], 2
            )
        else:
            semester_data[semester]['sgpa'] = 0.0
    
    # Calculate overall CGPA
    cgpa = round(total_grade_points / total_credits, 2) if total_credits > 0 else 0.0
    
    context = {
        'student': student,
        'semester_data': semester_data,
        'cgpa': cgpa,
        'total_credits': total_credits,
        'page_title': f'CGPA Report - {student.admin.first_name} {student.admin.last_name}'
    }
    
    return render(request, 'staff_template/student_cgpa.html', context)


@login_required(login_url='/')
def generate_marksheet_pdf(request, student_id):
    """Generate digital marksheet PDF"""
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
    from io import BytesIO
    from django.http import HttpResponse
    from datetime import datetime
    
    student = get_object_or_404(Student, id=student_id)
    results = StudentResult.objects.filter(student=student).select_related('subject')
    
    if not results.exists():
        messages.error(request, 'No results found to generate marksheet')
        return redirect('staff_view_results')
    
    # Create PDF
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4,
                           rightMargin=30, leftMargin=30,
                           topMargin=30, bottomMargin=18)
    
    # Container for elements
    elements = []
    
    # Styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#003d82'),
        spaceAfter=12,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor('#1a202c'),
        spaceAfter=12,
        alignment=TA_CENTER
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=10,
        alignment=TA_LEFT
    )
    
    # Header
    elements.append(Paragraph("EDUVISION COLLEGE", title_style))
    elements.append(Paragraph("DIGITAL MARKSHEET", heading_style))
    elements.append(Spacer(1, 0.3*inch))
    
    # Student Details
    student_data = [
        ['Student Name:', f"{student.admin.first_name} {student.admin.last_name}"],
        ['Roll Number:', student.roll_number],
        ['Course:', student.course.name if student.course else 'N/A'],
        ['Session:', str(student.session) if student.session else 'N/A'],
        ['Date of Issue:', datetime.now().strftime('%d-%m-%Y')]
    ]
    
    student_table = Table(student_data, colWidths=[2*inch, 4*inch])
    student_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f5f5f5')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)
    ]))
    
    elements.append(student_table)
    elements.append(Spacer(1, 0.4*inch))
    
    # Results Table
    elements.append(Paragraph("Academic Performance", heading_style))
    elements.append(Spacer(1, 0.2*inch))
    
    # Calculate results with grades
    results_data = [['S.No', 'Subject', 'Internal (30)', 'External (70)', 'Total (100)', 'Grade']]
    
    total_credits = 0
    total_grade_points = 0
    
    for idx, result in enumerate(results, 1):
        total_marks = result.test + result.exam
        grade = calculate_grade(total_marks)
        grade_point = calculate_grade_point(total_marks)
        credits = getattr(result.subject, 'credits', 3)
        
        results_data.append([
            str(idx),
            result.subject.name,
            f"{result.test:.1f}",
            f"{result.exam:.1f}",
            f"{total_marks:.1f}",
            grade
        ])
        
        total_credits += credits
        total_grade_points += (grade_point * credits)
    
    # Calculate CGPA
    cgpa = round(total_grade_points / total_credits, 2) if total_credits > 0 else 0.0
    
    results_table = Table(results_data, colWidths=[0.5*inch, 2.5*inch, 1*inch, 1*inch, 1*inch, 0.8*inch])
    results_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#003d82')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('TOPPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('ALIGN', (1, 1), (1, -1), 'LEFT'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9fafb')])
    ]))
    
    elements.append(results_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # CGPA Section
    cgpa_data = [
        ['Total Credits Earned:', str(total_credits)],
        ['Cumulative Grade Point Average (CGPA):', f"{cgpa:.2f}"]
    ]
    
    cgpa_table = Table(cgpa_data, colWidths=[3.5*inch, 2*inch])
    cgpa_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#e6f2ff')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)
    ]))
    
    elements.append(cgpa_table)
    elements.append(Spacer(1, 0.5*inch))
    
    # Grade Scale
    elements.append(Paragraph("Grading Scale", normal_style))
    elements.append(Spacer(1, 0.1*inch))
    
    grade_scale_data = [
        ['Grade', 'Marks Range', 'Grade Point'],
        ['A+', '90-100', '10.0'],
        ['A', '80-89', '9.0'],
        ['B+', '70-79', '8.0'],
        ['B', '60-69', '7.0'],
        ['C+', '50-59', '6.0'],
        ['C', '40-49', '5.0'],
        ['F', 'Below 40', '0.0']
    ]
    
    grade_table = Table(grade_scale_data, colWidths=[1*inch, 1.5*inch, 1.5*inch])
    grade_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f5f5f5')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9fafb')])
    ]))
    
    elements.append(grade_table)
    elements.append(Spacer(1, 0.7*inch))
    
    # Footer
    footer_data = [
        ['Date: ' + datetime.now().strftime('%d-%m-%Y'), 'Authorized Signatory']
    ]
    footer_table = Table(footer_data, colWidths=[3*inch, 3*inch])
    footer_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (0, 0), 'LEFT'),
        ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('TOPPADDING', (0, 0), (-1, -1), 15)
    ]))
    
    elements.append(footer_table)
    
    # Build PDF
    doc.build(elements)
    
    # Return PDF response
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Marksheet_{student.roll_number}.pdf"'
    
    return response


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

@login_required(login_url='login')
def upload_material(request):
    """Staff upload study material"""
    staff = get_object_or_404(Staff, admin=request.user)
    if request.method == 'POST':
        form = StudyMaterialForm(request.POST, request.FILES)
        if form.is_valid():
            material = form.save(commit=False)
            material.uploaded_by = staff
            material.save()
            messages.success(request, "Study material uploaded successfully!")
            return redirect('view_materials')
    else:
        form = StudyMaterialForm()
    
    context = {
        'page_title': 'Upload Study Material',
        'form': form,
        'staff': staff
    }
    return render(request, 'staff_template/upload_material.html', context)


@login_required(login_url='login')
def view_materials(request):
    """Staff view study materials"""
    staff = get_object_or_404(Staff, admin=request.user)
    materials = StudyMaterial.objects.filter(uploaded_by=staff).order_by('-created_at')
    
    context = {
        'page_title': 'Study Materials',
        'materials': materials,
        'staff': staff
    }
    return render(request, 'staff_template/view_materials.html', context)


@login_required(login_url='login')
def create_assignment(request):
    """Staff create assignment"""
    staff = get_object_or_404(Staff, admin=request.user)
    if request.method == 'POST':
        form = AssignmentForm(request.POST)
        if form.is_valid():
            assignment = form.save(commit=False)
            assignment.staff = staff
            assignment.save()
            messages.success(request, "Assignment created successfully!")
            return redirect('view_assignments')
    else:
        form = AssignmentForm()
    
    context = {
        'page_title': 'Create Assignment',
        'form': form,
        'staff': staff
    }
    return render(request, 'staff_template/create_assignment.html', context)


@login_required(login_url='login')
def view_assignments(request):
    """Staff view assignments"""
    staff = get_object_or_404(Staff, admin=request.user)
    assignments = Assignment.objects.filter(staff=staff).order_by('-created_at')
    
    context = {
        'page_title': 'Assignments',
        'assignments': assignments,
        'staff': staff
    }
    return render(request, 'staff_template/view_assignments.html', context)


@login_required(login_url='login')
def view_submissions(request):
    """Staff view assignment submissions"""
    staff = get_object_or_404(Staff, admin=request.user)
    submissions = AssignmentSubmission.objects.filter(assignment__staff=staff).order_by('-submitted_at')
    
    context = {
        'page_title': 'Assignment Submissions',
        'submissions': submissions,
        'staff': staff
    }
    return render(request, 'staff_template/view_submissions.html', context)


@login_required(login_url='login')
def grade_assignment(request, submission_id):
    """Grade an assignment submission"""
    staff = get_object_or_404(Staff, admin=request.user)
    submission = get_object_or_404(AssignmentSubmission, id=submission_id, assignment__staff=staff)
    
    if request.method == 'POST':
        marks_obtained = request.POST.get('marks_obtained')
        feedback = request.POST.get('feedback', '')
        
        if marks_obtained:
            try:
                submission.marks_obtained = float(marks_obtained)
                submission.feedback = feedback
                submission.status = 'graded'
                submission.graded_by = staff
                submission.graded_at = timezone.now()
                submission.save()
                
                messages.success(request, f'Assignment graded successfully for {submission.student.admin.get_full_name()}')
                return redirect('view_submissions')
            except ValueError:
                messages.error(request, 'Invalid marks value')
        else:
            messages.error(request, 'Please enter marks')
    
    context = {
        'page_title': 'Grade Assignment',
        'submission': submission,
        'staff': staff
    }
    return render(request, 'staff_template/grade_assignment.html', context)


@login_required(login_url='login')
def create_online_exam(request):
    """Staff create online exam"""
    staff = get_object_or_404(Staff, admin=request.user)
    if request.method == 'POST':
        form = QuizForm(request.POST)
        if form.is_valid():
            quiz = form.save(commit=False)
            quiz.created_by = staff
            quiz.save()
            messages.success(request, "Online exam created successfully!")
            return redirect('my_online_exams')
    else:
        form = QuizForm()
    
    context = {
        'page_title': 'Create Online Exam',
        'form': form,
        'staff': staff
    }
    return render(request, 'staff_template/create_online_exam.html', context)


@login_required(login_url='login')
def my_online_exams(request):
    """Staff view their online exams"""
    staff = get_object_or_404(Staff, admin=request.user)
    from main_app.models import Quiz
    quizzes = Quiz.objects.filter(created_by=staff).order_by('-created_at')
    
    context = {
        'page_title': 'My Online Exams',
        'quizzes': quizzes,
        'staff': staff
    }
    return render(request, 'staff_template/my_online_exams.html', context)

@login_required(login_url='login')
def view_students(request):
    """View all students in staff's classes"""
    staff = get_object_or_404(Staff, admin=request.user)
    
    # Get filter parameters
    selected_subject = request.GET.get('subject', '')
    search_query = request.GET.get('search', '')
    
    # Get subjects taught by staff
    subjects = Subject.objects.filter(staff=staff)
    
    # Get students based on filters
    students = Student.objects.filter(course=staff.course)
    
    if selected_subject:
        students = students.filter(course__subjects__id=selected_subject)
    
    if search_query:
        from django.db.models import Q
        students = students.filter(
            Q(admin__first_name__icontains=search_query) |
            Q(admin__last_name__icontains=search_query) |
            Q(roll_number__icontains=search_query)
        )
    
    students = students.select_related('admin', 'course', 'session').distinct()
    
    # Calculate additional stats for each student
    from django.utils import timezone
    today = timezone.now().date()
    
    for student in students:
        # Calculate attendance percentage
        total_attendance = AttendanceReport.objects.filter(student=student).count()
        if total_attendance > 0:
            present = AttendanceReport.objects.filter(student=student, status=True).count()
            student.attendance_percentage = round((present / total_attendance) * 100, 1)
        else:
            student.attendance_percentage = 0
        
        # Count assignments submitted
        student.assignments_submitted = AssignmentSubmission.objects.filter(student=student).count()
    
    # Summary stats
    total_students = students.count()
    total_present_today = AttendanceReport.objects.filter(
        student__in=students, 
        attendance__date=today,
        status=True
    ).count()
    low_attendance_count = sum(1 for s in students if s.attendance_percentage < 75)
    
    context = {
        'page_title': 'My Students',
        'staff': staff,
        'subjects': subjects,
        'students': students,
        'total_students': total_students,
        'total_present_today': total_present_today,
        'low_attendance_count': low_attendance_count,
        'selected_subject': selected_subject,
        'search_query': search_query,
    }
    
    return render(request, 'staff_template/view_students.html', context)


@login_required(login_url='login')
def staff_attendance_history(request):
    """View staff's own attendance history"""
    staff = get_object_or_404(Staff, admin=request.user)
    
    # Get filter parameters
    month = request.GET.get('month', '')
    year = request.GET.get('year', '')
    
    from django.utils import timezone
    current_date = timezone.now()
    
    # Get attendance records
    from main_app.models import StaffAttendance
    attendance_records = StaffAttendance.objects.filter(staff=staff).order_by('-date')
    
    if month and year:
        attendance_records = attendance_records.filter(date__month=month, date__year=year)
    
    # Calculate stats
    total_days = attendance_records.count()
    present_days = attendance_records.filter(status=True).count()
    absent_days = total_days - present_days
    
    if total_days > 0:
        attendance_percentage = round((present_days / total_days) * 100, 1)
    else:
        attendance_percentage = 0
    
    context = {
        'page_title': 'My Attendance History',
        'staff': staff,
        'attendance_records': attendance_records,
        'total_days': total_days,
        'present_days': present_days,
        'absent_days': absent_days,
        'attendance_percentage': attendance_percentage,
        'current_date': current_date,
    }
    
    return render(request, 'staff_template/staff_attendance_history.html', context)


