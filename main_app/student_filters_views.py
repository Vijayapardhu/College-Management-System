"""
Advanced Student Filtering and Export Views
"""
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.db.models import Q, Avg, Sum, Count, F
from django.utils import timezone
from datetime import datetime, timedelta
import csv
import json

from .models import Student, Attendance, FeePayment, StudentResult, LeaveReportStudent


@login_required
def filter_students(request):
    """
    Filter students based on various criteria
    """
    filter_type = request.GET.get('filter', 'all')
    students = Student.objects.select_related('admin', 'course', 'session', 'department', 'academic_year', 'section').all()
    
    # Apply filters
    if filter_type == 'absent':
        # Students with low attendance (< 75%)
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT s.id, 
                       COUNT(CASE WHEN ar.status = FALSE THEN 1 END) * 100.0 / NULLIF(COUNT(*), 0) as absent_pct
                FROM main_app_student s
                LEFT JOIN main_app_attendancereport ar ON ar.student_id = s.id
                LEFT JOIN main_app_attendance a ON ar.attendance_id = a.id
                WHERE a.date >= CURRENT_DATE - INTERVAL '30 days'
                GROUP BY s.id
                HAVING COUNT(CASE WHEN ar.status = FALSE THEN 1 END) * 100.0 / NULLIF(COUNT(*), 0) > 25
            """)
            absent_student_ids = [row[0] for row in cursor.fetchall()]
        students = students.filter(id__in=absent_student_ids)
        
    elif filter_type == 'fee_defaulters':
        # Students who haven't paid fees
        paid_student_ids = FeePayment.objects.filter(
            payment_status='paid'
        ).values_list('student_id', flat=True).distinct()
        students = students.exclude(id__in=paid_student_ids)
        
    elif filter_type == 'toppers':
        # Top 20 students by average marks (test + exam)
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT s.id, AVG(sr.test + sr.exam) as avg_marks
                FROM main_app_student s
                LEFT JOIN main_app_studentresult sr ON sr.student_id = s.id
                GROUP BY s.id
                HAVING AVG(sr.test + sr.exam) IS NOT NULL
                ORDER BY avg_marks DESC
                LIMIT 20
            """)
            topper_ids = [row[0] for row in cursor.fetchall()]
        students = students.filter(id__in=topper_ids)
        
    elif filter_type == 'high_attendance':
        # Students with > 90% attendance
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT s.id, 
                       COUNT(CASE WHEN ar.status = TRUE THEN 1 END) * 100.0 / NULLIF(COUNT(*), 0) as attendance_pct
                FROM main_app_student s
                LEFT JOIN main_app_attendancereport ar ON ar.student_id = s.id
                LEFT JOIN main_app_attendance a ON ar.attendance_id = a.id
                WHERE a.date >= CURRENT_DATE - INTERVAL '30 days'
                GROUP BY s.id
                HAVING COUNT(CASE WHEN ar.status = TRUE THEN 1 END) * 100.0 / NULLIF(COUNT(*), 0) > 90
            """)
            high_attendance_ids = [row[0] for row in cursor.fetchall()]
        students = students.filter(id__in=high_attendance_ids)
        
    elif filter_type == 'active_leave':
        # Students currently on leave
        try:
            active_leaves = LeaveReportStudent.objects.filter(
                status=1,  # Approved
                date__lte=timezone.now().date(),
                date__gte=timezone.now().date() - timedelta(days=30)
            ).values_list('student_id', flat=True)
            students = students.filter(id__in=active_leaves)
        except:
            # If leave model structure is different, skip this filter
            pass
        
    elif filter_type == 'by_year':
        year_id = request.GET.get('year_id')
        if year_id:
            students = students.filter(academic_year_id=year_id)
            
    elif filter_type == 'by_section':
        section_id = request.GET.get('section_id')
        if section_id:
            students = students.filter(section_id=section_id)
            
    elif filter_type == 'by_session':
        session_id = request.GET.get('session_id')
        if session_id:
            students = students.filter(session_id=session_id)
    
    # Return as JSON for AJAX requests
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        student_data = []
        for student in students:
            student_data.append({
                'id': student.id,
                'name': f"{student.admin.first_name} {student.admin.last_name}",
                'email': student.admin.email,
                'roll_number': student.roll_number or 'N/A',
                'course': student.course.name if student.course else 'N/A',
                'year': str(student.academic_year) if student.academic_year else 'N/A',
                'section': str(student.section) if student.section else 'N/A',
                'session': student.session.session_name if student.session and student.session.session_name else 'N/A',
            })
        return JsonResponse({'students': student_data, 'count': len(student_data)})
    
    context = {
        'students': students,
        'filter_type': filter_type,
        'page_title': 'Filtered Students'
    }
    return render(request, 'hod_template/manage_student.html', context)


@login_required
def export_students_csv(request):
    """
    Export filtered students to CSV
    """
    filter_type = request.GET.get('filter', 'all')
    
    # Get filtered students (reuse filter logic)
    from django.test import RequestFactory
    factory = RequestFactory()
    req = factory.get('/', data=request.GET)
    req.user = request.user
    req.headers = request.headers
    
    # Call filter_students to get the filtered queryset
    students = Student.objects.select_related('admin', 'course', 'session', 'department', 'academic_year', 'section').all()
    
    # Apply same filters as filter_students
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
        paid_student_ids = FeePayment.objects.filter(payment_status='paid').values_list('student_id', flat=True).distinct()
        students = students.exclude(id__in=paid_student_ids)
    elif filter_type == 'toppers':
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT s.id
                FROM main_app_student s
                LEFT JOIN main_app_studentresult sr ON sr.student_id = s.id
                GROUP BY s.id
                HAVING AVG(sr.test + sr.exam) IS NOT NULL
                ORDER BY AVG(sr.test + sr.exam) DESC
                LIMIT 20
            """)
            student_ids = [row[0] for row in cursor.fetchall()]
        students = students.filter(id__in=student_ids)
    elif filter_type == 'by_year':
        year_id = request.GET.get('year_id')
        if year_id:
            students = students.filter(academic_year_id=year_id)
    elif filter_type == 'by_section':
        section_id = request.GET.get('section_id')
        if section_id:
            students = students.filter(section_id=section_id)
    elif filter_type == 'by_session':
        session_id = request.GET.get('session_id')
        if session_id:
            students = students.filter(session_id=session_id)
    
    # Create CSV response
    response = HttpResponse(content_type='text/csv')
    filename = f'students_{filter_type}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    writer = csv.writer(response)
    
    # Header row
    writer.writerow([
        'S.No', 'Full Name', 'Email', 'Gender', 'Course', 
        'Department', 'Year', 'Section', 'Session', 'Roll Number',
        'Mobile', 'Admission Date'
    ])
    
    # Data rows
    for idx, student in enumerate(students, 1):
        writer.writerow([
            idx,
            f"{student.admin.first_name} {student.admin.last_name}",
            student.admin.email,
            student.admin.get_gender_display(),
            student.course.name if student.course else 'N/A',
            student.department.name if student.department else 'N/A',
            str(student.academic_year) if student.academic_year else 'N/A',
            str(student.section) if student.section else 'N/A',
            student.session.session_name if student.session and student.session.session_name else 'N/A',
            student.roll_number or 'N/A',
            student.mobile_number or 'N/A',
            student.admission_date.strftime('%Y-%m-%d') if student.admission_date else 'N/A',
        ])
    
    return response


@login_required
def get_filter_stats(request):
    """
    Get statistics for different filter types
    """
    stats = {}
    
    # Total students
    stats['total'] = Student.objects.count()
    
    # Absent students (< 75% attendance in last 30 days)
    from django.db import connection
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT COUNT(DISTINCT s.id)
            FROM main_app_student s
            LEFT JOIN main_app_attendance a ON a.student_id = s.id
            WHERE a.date >= CURRENT_DATE - INTERVAL '30 days'
            GROUP BY s.id
            HAVING COUNT(CASE WHEN a.status = FALSE THEN 1 END) * 100.0 / NULLIF(COUNT(*), 0) > 25
        """)
        result = cursor.fetchone()
        stats['absent'] = result[0] if result else 0
    
    # Fee defaulters
    paid_student_ids = FeePayment.objects.filter(payment_status='paid').values_list('student_id', flat=True).distinct()
    stats['fee_defaulters'] = Student.objects.exclude(id__in=paid_student_ids).count()
    
    # Toppers
    stats['toppers'] = 20
    
    # High attendance
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT COUNT(DISTINCT s.id)
            FROM main_app_student s
            LEFT JOIN main_app_attendance a ON a.student_id = s.id
            WHERE a.date >= CURRENT_DATE - INTERVAL '30 days'
            GROUP BY s.id
            HAVING COUNT(CASE WHEN a.status = TRUE THEN 1 END) * 100.0 / NULLIF(COUNT(*), 0) > 90
        """)
        result = cursor.fetchone()
        stats['high_attendance'] = result[0] if result else 0
    
    # Active leaves
    stats['active_leave'] = LeaveApplication.objects.filter(
        status='approved',
        leave_start_date__lte=timezone.now().date(),
        leave_end_date__gte=timezone.now().date()
    ).count()
    
    return JsonResponse(stats)

