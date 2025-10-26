"""
Advanced Features for College Management System
- Bulk Operations
- Student Progression
- Smart Notifications
- Advanced Analytics
"""
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.db.models import Q, Avg, Count, Sum, F, Case, When, IntegerField
from django.utils import timezone
from datetime import datetime, timedelta
import csv
import io
import json

from .models import (
    Student, CustomUser, Course, Session, AcademicYear, Section, 
    Attendance, StudentResult, FeePayment, Staff, ClassGroup,
    NotificationStudent, LeaveReportStudent
)


# ============================================================================
# BULK OPERATIONS
# ============================================================================

@login_required
def bulk_student_upload(request):
    """
    Upload multiple students via CSV
    CSV Format: first_name, last_name, email, gender, course_id, session_id, 
                year_id, section_id, roll_number, mobile, father_name, mother_name
    """
    if request.method == 'POST' and request.FILES.get('csv_file'):
        csv_file = request.FILES['csv_file']
        
        if not csv_file.name.endswith('.csv'):
            messages.error(request, 'Please upload a CSV file')
            return redirect('bulk_student_upload')
        
        try:
            # Read CSV
            decoded_file = csv_file.read().decode('utf-8')
            io_string = io.StringIO(decoded_file)
            reader = csv.DictReader(io_string)
            
            success_count = 0
            error_count = 0
            errors = []
            
            for row_num, row in enumerate(reader, start=2):
                try:
                    # Create CustomUser
                    user = CustomUser.objects.create_user(
                        email=row['email'],
                        password=row.get('password', 'student123'),
                        first_name=row['first_name'],
                        last_name=row['last_name'],
                        user_type='3',
                        gender=row.get('gender', 'M')
                    )
                    
                    # Create Student
                    student = Student.objects.create(
                        admin=user,
                        course_id=row.get('course_id'),
                        session_id=row.get('session_id'),
                        academic_year_id=row.get('year_id'),
                        section_id=row.get('section_id'),
                        roll_number=row.get('roll_number'),
                        mobile_number=row.get('mobile'),
                        father_name=row.get('father_name', ''),
                        mother_name=row.get('mother_name', ''),
                    )
                    success_count += 1
                    
                except Exception as e:
                    error_count += 1
                    errors.append(f"Row {row_num}: {str(e)}")
            
            messages.success(request, f'Successfully added {success_count} students')
            if error_count > 0:
                messages.warning(request, f'{error_count} errors occurred. Check details.')
                for error in errors[:5]:  # Show first 5 errors
                    messages.error(request, error)
                    
        except Exception as e:
            messages.error(request, f'Error processing file: {str(e)}')
        
        return redirect('manage_student')
    
    context = {'page_title': 'Bulk Student Upload'}
    return render(request, 'hod_template/bulk_student_upload.html', context)


@login_required
def bulk_promote_students(request):
    """
    Promote students to next academic year
    """
    if request.method == 'POST':
        from_year_id = request.POST.get('from_year')
        to_year_id = request.POST.get('to_year')
        session_id = request.POST.get('session')
        
        if not all([from_year_id, to_year_id, session_id]):
            messages.error(request, 'Please select all fields')
            return redirect('bulk_promote_students')
        
        try:
            # Get students to promote
            students = Student.objects.filter(
                academic_year_id=from_year_id,
                session_id=session_id
            )
            
            promoted_count = students.update(academic_year_id=to_year_id)
            
            messages.success(request, f'Successfully promoted {promoted_count} students from {from_year_id} to {to_year_id}')
            
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
        
        return redirect('bulk_promote_students')
    
    years = AcademicYear.objects.all()
    sessions = Session.objects.all()
    
    context = {
        'years': years,
        'sessions': sessions,
        'page_title': 'Bulk Student Promotion'
    }
    return render(request, 'hod_template/bulk_promote_students.html', context)


@login_required
def bulk_transfer_section(request):
    """
    Transfer students between sections
    """
    if request.method == 'POST':
        student_ids = request.POST.getlist('student_ids')
        to_section_id = request.POST.get('to_section')
        
        if not student_ids or not to_section_id:
            messages.error(request, 'Please select students and target section')
            return redirect('bulk_transfer_section')
        
        try:
            updated = Student.objects.filter(id__in=student_ids).update(section_id=to_section_id)
            messages.success(request, f'Successfully transferred {updated} students')
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
        
        return redirect('manage_student')
    
    students = Student.objects.select_related('admin', 'course', 'academic_year', 'section').all()
    sections = Section.objects.all()
    
    context = {
        'students': students,
        'sections': sections,
        'page_title': 'Bulk Section Transfer'
    }
    return render(request, 'hod_template/bulk_transfer_section.html', context)


# ============================================================================
# ADVANCED ANALYTICS
# ============================================================================

@login_required
def student_analytics_dashboard(request):
    """
    Advanced analytics dashboard with multiple insights
    """
    from django.db import connection
    
    # Overall Statistics
    total_students = Student.objects.count()
    active_students = Student.objects.filter(student_status='active').count()
    
    # Year-wise distribution
    year_distribution = Student.objects.values(
        'academic_year__year_name'
    ).annotate(count=Count('id')).order_by('academic_year__year_number')
    
    # Section-wise distribution
    section_distribution = Student.objects.values(
        'section__name'
    ).annotate(count=Count('id')).order_by('section__name')
    
    # Course-wise distribution
    course_distribution = Student.objects.values(
        'course__name'
    ).annotate(count=Count('id'))
    
    # Attendance Analysis (last 30 days)
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT 
                CASE 
                    WHEN attendance_pct >= 90 THEN 'Excellent (≥90%)'
                    WHEN attendance_pct >= 75 THEN 'Good (75-90%)'
                    WHEN attendance_pct >= 60 THEN 'Average (60-75%)'
                    ELSE 'Poor (<60%)'
                END as category,
                COUNT(*) as student_count
            FROM (
                SELECT s.id,
                       COUNT(CASE WHEN a.status = TRUE THEN 1 END) * 100.0 / NULLIF(COUNT(*), 0) as attendance_pct
                FROM main_app_student s
                LEFT JOIN main_app_attendance a ON a.student_id = s.id
                WHERE a.date >= CURRENT_DATE - INTERVAL '30 days'
                GROUP BY s.id
            ) as attendance_stats
            GROUP BY category
            ORDER BY category DESC
        """)
        attendance_categories = [{'category': row[0], 'count': row[1]} for row in cursor.fetchall()]
    
    # Performance Analysis
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT 
                CASE 
                    WHEN avg_marks >= 90 THEN 'Outstanding (≥90%)'
                    WHEN avg_marks >= 75 THEN 'First Class (75-90%)'
                    WHEN avg_marks >= 60 THEN 'Second Class (60-75%)'
                    WHEN avg_marks >= 50 THEN 'Pass (50-60%)'
                    ELSE 'Fail (<50%)'
                END as grade,
                COUNT(*) as student_count
            FROM (
                SELECT s.id, AVG(sr.test + sr.exam) as avg_marks
                FROM main_app_student s
                LEFT JOIN main_app_studentresult sr ON sr.student_id = s.id
                GROUP BY s.id
                HAVING AVG(sr.test + sr.exam) IS NOT NULL
            ) as performance_stats
            GROUP BY grade
            ORDER BY grade DESC
        """)
        performance_categories = [{'grade': row[0], 'count': row[1]} for row in cursor.fetchall()]
    
    # At-risk students (low attendance + low marks)
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT COUNT(DISTINCT s.id)
            FROM main_app_student s
            LEFT JOIN main_app_attendance a ON a.student_id = s.id
            LEFT JOIN main_app_studentresult sr ON sr.student_id = s.id
            WHERE a.date >= CURRENT_DATE - INTERVAL '30 days'
            GROUP BY s.id
            HAVING 
                (COUNT(CASE WHEN a.status = TRUE THEN 1 END) * 100.0 / NULLIF(COUNT(*), 0) < 75)
                OR (AVG(sr.test + sr.exam) < 50)
        """)
        at_risk_count = cursor.fetchone()[0] if cursor.rowcount > 0 else 0
    
    context = {
        'total_students': total_students,
        'active_students': active_students,
        'year_distribution': year_distribution,
        'section_distribution': section_distribution,
        'course_distribution': course_distribution,
        'attendance_categories': attendance_categories,
        'performance_categories': performance_categories,
        'at_risk_count': at_risk_count,
        'page_title': 'Student Analytics Dashboard'
    }
    
    return render(request, 'hod_template/student_analytics_dashboard.html', context)


@login_required
def performance_trends(request):
    """
    Show performance trends over time
    """
    student_id = request.GET.get('student_id')
    
    if student_id:
        # Individual student trends
        results = StudentResult.objects.filter(
            student_id=student_id
        ).select_related('subject').order_by('created_at')
        
        trend_data = []
        for result in results:
            trend_data.append({
                'subject': result.subject.name,
                'test': result.test,
                'exam': result.exam,
                'total': result.test + result.exam,
                'date': result.created_at.strftime('%Y-%m-%d')
            })
        
        return JsonResponse({'trends': trend_data})
    
    # Overall trends by course
    from django.db import connection
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT 
                c.name as course,
                DATE_TRUNC('month', sr.created_at) as month,
                AVG(sr.test + sr.exam) as avg_marks
            FROM main_app_studentresult sr
            JOIN main_app_student s ON sr.student_id = s.id
            JOIN main_app_course c ON s.course_id = c.id
            WHERE sr.created_at >= CURRENT_DATE - INTERVAL '6 months'
            GROUP BY c.name, DATE_TRUNC('month', sr.created_at)
            ORDER BY month, course
        """)
        trends = [{'course': row[0], 'month': row[1].strftime('%Y-%m'), 'avg_marks': float(row[2])} 
                  for row in cursor.fetchall()]
    
    return JsonResponse({'trends': trends})


# ============================================================================
# SMART NOTIFICATIONS
# ============================================================================

@login_required
def send_bulk_notifications(request):
    """
    Send notifications to filtered students
    """
    if request.method == 'POST':
        filter_type = request.POST.get('filter_type')
        notification_title = request.POST.get('title')
        notification_message = request.POST.get('message')
        
        # Get filtered students
        students = Student.objects.all()
        
        if filter_type == 'absent':
            from django.db import connection
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT s.id
                    FROM main_app_student s
                    LEFT JOIN main_app_attendancereport ar ON ar.student_id = s.id
                    LEFT JOIN main_app_attendance a ON ar.attendance_id = a.id
                    WHERE a.date >= CURRENT_DATE - INTERVAL '30 days'
                    GROUP BY s.id
                    HAVING COUNT(CASE WHEN ar.status = FALSE THEN 1 END) * 100.0 / NULLIF(COUNT(*), 0) > 25
                """)
                student_ids = [row[0] for row in cursor.fetchall()]
            students = students.filter(id__in=student_ids)
        elif filter_type == 'fee_defaulters':
            paid_ids = FeePayment.objects.filter(payment_status='paid').values_list('student_id', flat=True)
            students = students.exclude(id__in=paid_ids)
        
        # Create notifications
        notification_count = 0
        for student in students:
            NotificationStudent.objects.create(
                student=student,
                message=f"{notification_title}\n\n{notification_message}"
            )
            notification_count += 1
        
        messages.success(request, f'Sent {notification_count} notifications successfully')
        return redirect('send_bulk_notifications')
    
    context = {'page_title': 'Bulk Notifications'}
    return render(request, 'hod_template/bulk_notifications.html', context)


@login_required
def auto_attendance_alerts(request):
    """
    Automatically send alerts to students with low attendance
    """
    from django.db import connection
    
    # Find students with < 75% attendance in last 30 days
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT s.id, s.admin_id,
                   COUNT(CASE WHEN a.status = FALSE THEN 1 END) * 100.0 / NULLIF(COUNT(*), 0) as absent_pct
            FROM main_app_student s
            LEFT JOIN main_app_attendance a ON a.student_id = s.id
            WHERE a.date >= CURRENT_DATE - INTERVAL '30 days'
            GROUP BY s.id, s.admin_id
            HAVING COUNT(CASE WHEN a.status = FALSE THEN 1 END) * 100.0 / NULLIF(COUNT(*), 0) > 25
        """)
        at_risk_students = cursor.fetchall()
    
    alert_count = 0
    for student_id, admin_id, absent_pct in at_risk_students:
        message = f"""
        ATTENDANCE ALERT
        
        Your attendance has fallen below 75% (Current: {100 - absent_pct:.1f}%)
        
        Minimum requirement: 75%
        Action Required: Improve attendance immediately
        
        Contact your class teacher for assistance.
        """
        
        NotificationStudent.objects.create(
            student_id=student_id,
            message=message
        )
        alert_count += 1
    
    messages.success(request, f'Sent {alert_count} attendance alerts')
    return redirect('student_analytics_dashboard')


# ============================================================================
# STUDENT PROGRESSION
# ============================================================================

@login_required
def student_progression_view(request):
    """
    Manage student year progression and graduation
    """
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'promote':
            # Promote all 1st year to 2nd year, 2nd to 3rd
            session_id = request.POST.get('session_id')
            
            # Promote 1st → 2nd
            count_1to2 = Student.objects.filter(
                academic_year__year_number=1,
                session_id=session_id
            ).update(academic_year=AcademicYear.objects.get(year_number=2))
            
            # Promote 2nd → 3rd
            count_2to3 = Student.objects.filter(
                academic_year__year_number=2,
                session_id=session_id
            ).update(academic_year=AcademicYear.objects.get(year_number=3))
            
            # Graduate 3rd years
            count_graduated = Student.objects.filter(
                academic_year__year_number=3,
                session_id=session_id
            ).update(
                student_status='graduated',
                date_of_graduation=timezone.now().date()
            )
            
            messages.success(request, f'Promoted: {count_1to2} (1→2), {count_2to3} (2→3), Graduated: {count_graduated}')
            
        return redirect('student_progression')
    
    # Get progression statistics
    sessions = Session.objects.all()
    years = AcademicYear.objects.all()
    
    progression_stats = []
    for session in sessions:
        for year in years:
            count = Student.objects.filter(
                session=session,
                academic_year=year
            ).count()
            if count > 0:
                progression_stats.append({
                    'session': session,
                    'year': year,
                    'count': count
                })
    
    context = {
        'progression_stats': progression_stats,
        'sessions': sessions,
        'years': years,
        'page_title': 'Student Progression'
    }
    return render(request, 'hod_template/student_progression.html', context)


# ============================================================================
# ADVANCED REPORTS
# ============================================================================

@login_required
def generate_custom_report(request):
    """
    Custom report generator with multiple parameters
    """
    if request.method == 'POST':
        # Get report parameters
        report_type = request.POST.get('report_type')
        course_id = request.POST.get('course')
        year_id = request.POST.get('year')
        section_id = request.POST.get('section')
        session_id = request.POST.get('session')
        date_from = request.POST.get('date_from')
        date_to = request.POST.get('date_to')
        
        # Build query
        students = Student.objects.select_related('admin', 'course', 'academic_year', 'section', 'session').all()
        
        if course_id:
            students = students.filter(course_id=course_id)
        if year_id:
            students = students.filter(academic_year_id=year_id)
        if section_id:
            students = students.filter(section_id=section_id)
        if session_id:
            students = students.filter(session_id=session_id)
        
        # Generate report based on type
        if report_type == 'attendance':
            return generate_attendance_report(students, date_from, date_to)
        elif report_type == 'performance':
            return generate_performance_report(students)
        elif report_type == 'fee_status':
            return generate_fee_status_report(students)
        elif report_type == 'complete':
            return generate_complete_report(students)
    
    courses = Course.objects.all()
    years = AcademicYear.objects.all()
    sections = Section.objects.all()
    sessions = Session.objects.all()
    
    context = {
        'courses': courses,
        'years': years,
        'sections': sections,
        'sessions': sessions,
        'page_title': 'Custom Report Generator'
    }
    return render(request, 'hod_template/custom_report_generator.html', context)


def generate_attendance_report(students, date_from, date_to):
    """Generate detailed attendance report"""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="attendance_report_{datetime.now().strftime("%Y%m%d")}.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Roll No', 'Name', 'Course', 'Year', 'Section', 'Total Classes', 'Present', 'Absent', 'Attendance %'])
    
    from django.db import connection
    for student in students:
        with connection.cursor() as cursor:
            query = """
                SELECT 
                    COUNT(*) as total,
                    COUNT(CASE WHEN status = TRUE THEN 1 END) as present,
                    COUNT(CASE WHEN status = FALSE THEN 1 END) as absent
                FROM main_app_attendance
                WHERE student_id = %s
            """
            params = [student.id]
            
            if date_from and date_to:
                query += " AND date BETWEEN %s AND %s"
                params.extend([date_from, date_to])
            
            cursor.execute(query, params)
            result = cursor.fetchone()
            
            if result and result[0] > 0:
                total, present, absent = result
                attendance_pct = (present / total * 100) if total > 0 else 0
                
                writer.writerow([
                    student.roll_number or 'N/A',
                    f"{student.admin.first_name} {student.admin.last_name}",
                    student.course.name if student.course else 'N/A',
                    str(student.academic_year) if student.academic_year else 'N/A',
                    str(student.section) if student.section else 'N/A',
                    total,
                    present,
                    absent,
                    f"{attendance_pct:.2f}%"
                ])
    
    return response


def generate_performance_report(students):
    """Generate detailed performance report"""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="performance_report_{datetime.now().strftime("%Y%m%d")}.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Roll No', 'Name', 'Course', 'Year', 'Section', 'Subjects', 'Avg Test', 'Avg Exam', 'Total Avg', 'Grade'])
    
    for student in students:
        results = StudentResult.objects.filter(student=student)
        if results.exists():
            avg_test = results.aggregate(Avg('test'))['test__avg'] or 0
            avg_exam = results.aggregate(Avg('exam'))['exam__avg'] or 0
            total_avg = avg_test + avg_exam
            
            # Calculate grade
            if total_avg >= 90:
                grade = 'A+'
            elif total_avg >= 75:
                grade = 'A'
            elif total_avg >= 60:
                grade = 'B'
            elif total_avg >= 50:
                grade = 'C'
            else:
                grade = 'F'
            
            writer.writerow([
                student.roll_number or 'N/A',
                f"{student.admin.first_name} {student.admin.last_name}",
                student.course.name if student.course else 'N/A',
                str(student.academic_year) if student.academic_year else 'N/A',
                str(student.section) if student.section else 'N/A',
                results.count(),
                f"{avg_test:.2f}",
                f"{avg_exam:.2f}",
                f"{total_avg:.2f}",
                grade
            ])
    
    return response


def generate_fee_status_report(students):
    """Generate fee status report"""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="fee_status_report_{datetime.now().strftime("%Y%m%d")}.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Roll No', 'Name', 'Course', 'Year', 'Section', 'Total Fees', 'Paid', 'Pending', 'Status'])
    
    for student in students:
        payments = FeePayment.objects.filter(student=student)
        total_paid = payments.filter(payment_status='paid').aggregate(Sum('amount_paid'))['amount_paid__sum'] or 0
        total_fees = 50000  # You can get this from FeeStructure model
        pending = total_fees - total_paid
        status = 'Paid' if pending <= 0 else 'Pending'
        
        writer.writerow([
            student.roll_number or 'N/A',
            f"{student.admin.first_name} {student.admin.last_name}",
            student.course.name if student.course else 'N/A',
            str(student.academic_year) if student.academic_year else 'N/A',
            str(student.section) if student.section else 'N/A',
            total_fees,
            total_paid,
            pending,
            status
        ])
    
    return response


def generate_complete_report(students):
    """Generate complete student report with all details"""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="complete_student_report_{datetime.now().strftime("%Y%m%d")}.csv"'
    
    writer = csv.writer(response)
    writer.writerow([
        'Roll No', 'Name', 'Email', 'Gender', 'Mobile', 'Course', 'Department',
        'Year', 'Section', 'Session', 'Admission Date', 'Father Name', 'Mother Name',
        'Attendance %', 'Avg Marks', 'Fee Status'
    ])
    
    from django.db import connection
    for student in students:
        # Get attendance
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    COUNT(CASE WHEN status = TRUE THEN 1 END) * 100.0 / NULLIF(COUNT(*), 0)
                FROM main_app_attendance
                WHERE student_id = %s AND date >= CURRENT_DATE - INTERVAL '30 days'
            """, [student.id])
            attendance_pct = cursor.fetchone()[0] or 0
        
        # Get average marks
        results = StudentResult.objects.filter(student=student)
        avg_marks = 0
        if results.exists():
            avg_test = results.aggregate(Avg('test'))['test__avg'] or 0
            avg_exam = results.aggregate(Avg('exam'))['exam__avg'] or 0
            avg_marks = avg_test + avg_exam
        
        # Get fee status
        paid = FeePayment.objects.filter(student=student, payment_status='paid').exists()
        fee_status = 'Paid' if paid else 'Pending'
        
        writer.writerow([
            student.roll_number or 'N/A',
            f"{student.admin.first_name} {student.admin.last_name}",
            student.admin.email,
            student.admin.get_gender_display(),
            student.mobile_number or 'N/A',
            student.course.name if student.course else 'N/A',
            student.department.name if student.department else 'N/A',
            str(student.academic_year) if student.academic_year else 'N/A',
            str(student.section) if student.section else 'N/A',
            student.session.session_name if student.session and student.session.session_name else 'N/A',
            student.admission_date.strftime('%Y-%m-%d') if student.admission_date else 'N/A',
            student.father_name or 'N/A',
            student.mother_name or 'N/A',
            f"{attendance_pct:.2f}%",
            f"{avg_marks:.2f}",
            fee_status
        ])
    
    return response


# ============================================================================
# AT-RISK STUDENT IDENTIFICATION
# ============================================================================

@login_required
def identify_at_risk_students(request):
    """
    Identify students at risk of failure
    Criteria: Low attendance (<75%) OR Low marks (<50%) OR Fee defaulters
    """
    from django.db import connection
    
    # Students with low attendance
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT DISTINCT s.id, 'Low Attendance' as reason,
                   COUNT(CASE WHEN ar.status = FALSE THEN 1 END) * 100.0 / NULLIF(COUNT(*), 0) as metric
            FROM main_app_student s
            LEFT JOIN main_app_attendancereport ar ON ar.student_id = s.id
            LEFT JOIN main_app_attendance a ON ar.attendance_id = a.id
            WHERE a.date >= CURRENT_DATE - INTERVAL '30 days'
            GROUP BY s.id
            HAVING COUNT(CASE WHEN ar.status = FALSE THEN 1 END) * 100.0 / NULLIF(COUNT(*), 0) > 25
        """)
        low_attendance = {row[0]: {'reason': row[1], 'metric': f"{100-row[2]:.1f}%"} for row in cursor.fetchall()}
    
    # Students with low marks
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT s.id, 'Low Performance' as reason, AVG(sr.test + sr.exam) as metric
            FROM main_app_student s
            LEFT JOIN main_app_studentresult sr ON sr.student_id = s.id
            GROUP BY s.id
            HAVING AVG(sr.test + sr.exam) < 50 AND AVG(sr.test + sr.exam) IS NOT NULL
        """)
        low_performance = {row[0]: {'reason': row[1], 'metric': f"{row[2]:.1f}%"} for row in cursor.fetchall()}
    
    # Fee defaulters
    paid_ids = FeePayment.objects.filter(payment_status='paid').values_list('student_id', flat=True)
    fee_defaulters = Student.objects.exclude(id__in=paid_ids).values_list('id', flat=True)
    fee_defaulter_dict = {sid: {'reason': 'Fee Pending', 'metric': 'Unpaid'} for sid in fee_defaulters}
    
    # Combine all at-risk students
    all_at_risk_ids = set(list(low_attendance.keys()) + list(low_performance.keys()) + list(fee_defaulters))
    
    at_risk_students = Student.objects.filter(id__in=all_at_risk_ids).select_related(
        'admin', 'course', 'academic_year', 'section', 'session'
    )
    
    # Add risk reasons to students
    students_with_risks = []
    for student in at_risk_students:
        risks = []
        if student.id in low_attendance:
            risks.append(low_attendance[student.id])
        if student.id in low_performance:
            risks.append(low_performance[student.id])
        if student.id in fee_defaulter_dict:
            risks.append(fee_defaulter_dict[student.id])
        
        students_with_risks.append({
            'student': student,
            'risks': risks,
            'risk_count': len(risks)
        })
    
    # Sort by risk count (highest first)
    students_with_risks.sort(key=lambda x: x['risk_count'], reverse=True)
    
    context = {
        'at_risk_students': students_with_risks,
        'total_at_risk': len(students_with_risks),
        'page_title': 'At-Risk Students'
    }
    return render(request, 'hod_template/at_risk_students.html', context)


# ============================================================================
# CLASS PERFORMANCE COMPARISON
# ============================================================================

@login_required
def class_performance_comparison(request):
    """
    Compare performance across different classes/sections
    """
    from django.db import connection
    
    # Get performance by class group
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT 
                c.name as course,
                ay.year_name,
                sec.name as section,
                sess.session_name,
                COUNT(DISTINCT s.id) as student_count,
                AVG(sr.test + sr.exam) as avg_marks,
                AVG(CASE 
                    WHEN ar.status = TRUE THEN 100
                    ELSE 0
                END) as avg_attendance
            FROM main_app_student s
            LEFT JOIN main_app_course c ON s.course_id = c.id
            LEFT JOIN main_app_academicyear ay ON s.academic_year_id = ay.id
            LEFT JOIN main_app_section sec ON s.section_id = sec.id
            LEFT JOIN main_app_session sess ON s.session_id = sess.id
            LEFT JOIN main_app_studentresult sr ON sr.student_id = s.id
            LEFT JOIN main_app_attendancereport ar ON ar.student_id = s.id
            LEFT JOIN main_app_attendance a ON ar.attendance_id = a.id 
                AND a.date >= CURRENT_DATE - INTERVAL '30 days'
            WHERE c.id IS NOT NULL 
                AND ay.id IS NOT NULL 
                AND sec.id IS NOT NULL
            GROUP BY c.name, ay.year_name, sec.name, sess.session_name
            ORDER BY c.name, ay.year_name, sec.name
        """)
        
        comparisons = []
        for row in cursor.fetchall():
            comparisons.append({
                'course': row[0],
                'year': row[1],
                'section': row[2],
                'session': row[3] or 'N/A',
                'student_count': row[4],
                'avg_marks': round(row[5], 2) if row[5] else 0,
                'avg_attendance': round(row[6], 2) if row[6] else 0
            })
    
    context = {
        'comparisons': comparisons,
        'page_title': 'Class Performance Comparison'
    }
    return render(request, 'hod_template/class_performance_comparison.html', context)

