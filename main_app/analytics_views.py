from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.db.models import Count, Avg, Sum, Q
from django.utils import timezone
from datetime import datetime, timedelta
from .models import (
    Student, Staff, AttendanceReport, StudentResult, FeePayment,
    Course, Subject, Department, Session, Scholarship, ScholarshipApplication,
    Transport, TransportAllocation, Hostel, HostelAllocation, Library, LibraryIssue
)
import json


@login_required(login_url='login')
def analytics_dashboard(request):
    """Analytics dashboard with comprehensive metrics"""
    if request.user.user_type != '1':
        messages.error(request, 'Access denied')
        return redirect('login')
    
    # Student Analytics
    total_students = Student.objects.count()
    active_students = Student.objects.filter(admin__is_active=True).count()
    
    # Attendance Analytics
    total_attendance_records = AttendanceReport.objects.count()
    if total_attendance_records > 0:
        present_records = AttendanceReport.objects.filter(status=True).count()
        overall_attendance = round((present_records / total_attendance_records) * 100, 2)
    else:
        overall_attendance = 0
    
    # Performance Analytics
    results = StudentResult.objects.all()
    if results.exists():
        avg_performance = round(results.aggregate(Avg('marks'))['marks__avg'] or 0, 2)
    else:
        avg_performance = 0
    
    # Financial Analytics
    total_fees_collected = FeePayment.objects.filter(
        payment_status='paid'
    ).aggregate(Sum('amount_paid'))['amount_paid__sum'] or 0
    
    pending_fees = FeePayment.objects.filter(
        payment_status__in=['pending', 'partial']
    ).aggregate(Sum('amount_pending'))['amount_pending__sum'] or 0
    
    # Department-wise stats
    department_stats = Department.objects.annotate(
        student_count=Count('course__student'),
        faculty_count=Count('staff')
    )[:5]
    
    context = {
        'page_title': 'Analytics Dashboard',
        'total_students': total_students,
        'active_students': active_students,
        'overall_attendance': overall_attendance,
        'avg_performance': avg_performance,
        'total_fees_collected': total_fees_collected,
        'pending_fees': pending_fees,
        'department_stats': department_stats
    }
    return render(request, 'hod_template/analytics_dashboard.html', context)


@login_required(login_url='login')
def attendance_analytics(request):
    """Detailed attendance analytics with trends"""
    if request.user.user_type != '1':
        messages.error(request, 'Access denied')
        return redirect('login')
    
    # Overall Statistics
    total_students = Student.objects.count()
    total_attendance_records = AttendanceReport.objects.count()
    
    if total_attendance_records > 0:
        present_count = AttendanceReport.objects.filter(status=True).count()
        overall_attendance = round((present_count / total_attendance_records) * 100, 2)
    else:
        overall_attendance = 0
    
    # Department-wise attendance
    dept_attendance = []
    for dept in Department.objects.all():
        students = Student.objects.filter(course__department=dept)
        student_ids = students.values_list('id', flat=True)
        
        dept_records = AttendanceReport.objects.filter(student_id__in=student_ids)
        if dept_records.exists():
            dept_present = dept_records.filter(status=True).count()
            dept_total = dept_records.count()
            dept_percentage = round((dept_present / dept_total) * 100, 2) if dept_total > 0 else 0
        else:
            dept_percentage = 0
        
        dept_attendance.append({
            'name': dept.name,
            'percentage': dept_percentage,
            'student_count': students.count()
        })
    
    # Course-wise attendance
    course_attendance = []
    for course in Course.objects.all()[:10]:
        students = Student.objects.filter(course=course)
        student_ids = students.values_list('id', flat=True)
        
        course_records = AttendanceReport.objects.filter(student_id__in=student_ids)
        if course_records.exists():
            course_present = course_records.filter(status=True).count()
            course_total = course_records.count()
            course_percentage = round((course_present / course_total) * 100, 2) if course_total > 0 else 0
        else:
            course_percentage = 0
        
        course_attendance.append({
            'name': course.name,
            'percentage': course_percentage,
            'student_count': students.count()
        })
    
    # Monthly trend (last 6 months)
    monthly_trend = []
    today = timezone.now()
    for i in range(5, -1, -1):
        month_start = (today - timedelta(days=30*i)).replace(day=1)
        month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        
        month_records = AttendanceReport.objects.filter(
            attendance_date__range=[month_start, month_end]
        )
        if month_records.exists():
            month_present = month_records.filter(status=True).count()
            month_total = month_records.count()
            month_percentage = round((month_present / month_total) * 100, 2) if month_total > 0 else 0
        else:
            month_percentage = 0
        
        monthly_trend.append({
            'month': month_start.strftime('%b %Y'),
            'percentage': month_percentage
        })
    
    # Low attendance students
    low_attendance_students = []
    for student in Student.objects.all():
        student_records = AttendanceReport.objects.filter(student=student)
        if student_records.exists():
            student_present = student_records.filter(status=True).count()
            student_total = student_records.count()
            student_percentage = round((student_present / student_total) * 100, 2) if student_total > 0 else 0
            
            if student_percentage < 75:
                low_attendance_students.append({
                    'name': f"{student.admin.first_name} {student.admin.last_name}",
                    'roll_number': student.roll_number,
                    'course': student.course.name,
                    'percentage': student_percentage
                })
    
    low_attendance_students = sorted(low_attendance_students, key=lambda x: x['percentage'])[:20]
    
    context = {
        'page_title': 'Attendance Analytics',
        'total_students': total_students,
        'total_records': total_attendance_records,
        'overall_attendance': overall_attendance,
        'dept_attendance': dept_attendance,
        'course_attendance': course_attendance,
        'monthly_trend': monthly_trend,
        'monthly_trend_json': json.dumps(monthly_trend),
        'low_attendance_students': low_attendance_students,
        'low_attendance_count': len(low_attendance_students)
    }
    return render(request, 'hod_template/attendance_analytics.html', context)


@login_required(login_url='login')
def academic_performance_analytics(request):
    """Comprehensive academic performance analytics"""
    if request.user.user_type != '1':
        messages.error(request, 'Access denied')
        return redirect('login')
    
    # Overall Performance Stats
    total_students = Student.objects.count()
    total_results = StudentResult.objects.count()
    
    results = StudentResult.objects.all()
    if results.exists():
        avg_marks = round(results.aggregate(Avg('marks'))['marks__avg'] or 0, 2)
        pass_count = results.filter(marks__gte=40).count()
        pass_rate = round((pass_count / total_results) * 100, 2) if total_results > 0 else 0
    else:
        avg_marks = 0
        pass_rate = 0
    
    # Grade Distribution
    grade_distribution = {
        'A+': results.filter(marks__gte=90).count(),
        'A': results.filter(marks__gte=80, marks__lt=90).count(),
        'B': results.filter(marks__gte=70, marks__lt=80).count(),
        'C': results.filter(marks__gte=60, marks__lt=70).count(),
        'D': results.filter(marks__gte=50, marks__lt=60).count(),
        'E': results.filter(marks__gte=40, marks__lt=50).count(),
        'F': results.filter(marks__lt=40).count()
    }
    
    # Subject-wise Performance
    subject_performance = []
    for subject in Subject.objects.all()[:15]:
        subject_results = StudentResult.objects.filter(subject=subject)
        if subject_results.exists():
            subject_avg = round(subject_results.aggregate(Avg('marks'))['marks__avg'] or 0, 2)
            subject_pass = subject_results.filter(marks__gte=40).count()
            subject_total = subject_results.count()
            subject_pass_rate = round((subject_pass / subject_total) * 100, 2) if subject_total > 0 else 0
        else:
            subject_avg = 0
            subject_pass_rate = 0
        
        subject_performance.append({
            'name': subject.name,
            'avg_marks': subject_avg,
            'pass_rate': subject_pass_rate
        })
    
    # Course-wise Performance
    course_performance = []
    for course in Course.objects.all()[:10]:
        students = Student.objects.filter(course=course)
        student_ids = students.values_list('id', flat=True)
        
        course_results = StudentResult.objects.filter(student_id__in=student_ids)
        if course_results.exists():
            course_avg = round(course_results.aggregate(Avg('marks'))['marks__avg'] or 0, 2)
        else:
            course_avg = 0
        
        course_performance.append({
            'name': course.name,
            'avg_marks': course_avg,
            'student_count': students.count()
        })
    
    # Top Performers
    top_students = []
    for student in Student.objects.all():
        student_results = StudentResult.objects.filter(student=student)
        if student_results.exists():
            student_avg = round(student_results.aggregate(Avg('marks'))['marks__avg'] or 0, 2)
            top_students.append({
                'name': f"{student.admin.first_name} {student.admin.last_name}",
                'roll_number': student.roll_number,
                'course': student.course.name,
                'avg_marks': student_avg
            })
    
    top_students = sorted(top_students, key=lambda x: x['avg_marks'], reverse=True)[:10]
    
    context = {
        'page_title': 'Academic Performance Analytics',
        'total_students': total_students,
        'total_results': total_results,
        'avg_marks': avg_marks,
        'pass_rate': pass_rate,
        'grade_distribution': grade_distribution,
        'grade_distribution_json': json.dumps(grade_distribution),
        'subject_performance': subject_performance,
        'course_performance': course_performance,
        'top_students': top_students
    }
    return render(request, 'hod_template/academic_performance_analytics.html', context)


@login_required(login_url='login')
def financial_analytics(request):
    """Comprehensive financial analytics and reporting"""
    if request.user.user_type != '1':
        messages.error(request, 'Access denied')
        return redirect('login')
    
    # Fee Collection Statistics
    total_fee_collected = FeePayment.objects.filter(
        payment_status='paid'
    ).aggregate(Sum('amount_paid'))['amount_paid__sum'] or 0
    
    partial_payments = FeePayment.objects.filter(
        payment_status='partial'
    ).aggregate(Sum('amount_paid'))['amount_paid__sum'] or 0
    
    pending_fees = FeePayment.objects.filter(
        payment_status__in=['pending', 'partial']
    ).aggregate(Sum('amount_pending'))['amount_pending__sum'] or 0
    
    total_expected = total_fee_collected + pending_fees
    collection_rate = round((total_fee_collected / total_expected) * 100, 2) if total_expected > 0 else 0
    
    # Monthly Revenue Trend (last 6 months)
    monthly_revenue = []
    today = timezone.now()
    for i in range(5, -1, -1):
        month_start = (today - timedelta(days=30*i)).replace(day=1)
        month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        
        month_collection = FeePayment.objects.filter(
            payment_date__range=[month_start, month_end],
            payment_status__in=['paid', 'partial']
        ).aggregate(Sum('amount_paid'))['amount_paid__sum'] or 0
        
        monthly_revenue.append({
            'month': month_start.strftime('%b %Y'),
            'amount': float(month_collection)
        })
    
    # Course-wise Fee Collection
    course_fees = []
    for course in Course.objects.all()[:10]:
        students = Student.objects.filter(course=course)
        student_ids = students.values_list('id', flat=True)
        
        course_collected = FeePayment.objects.filter(
            student_id__in=student_ids,
            payment_status__in=['paid', 'partial']
        ).aggregate(Sum('amount_paid'))['amount_paid__sum'] or 0
        
        course_fees.append({
            'name': course.name,
            'collected': float(course_collected),
            'student_count': students.count()
        })
    
    # Scholarship Disbursements
    total_scholarships_disbursed = ScholarshipApplication.objects.filter(
        status='disbursed'
    ).count()
    
    scholarship_amount = 0
    for app in ScholarshipApplication.objects.filter(status='disbursed'):
        scholarship_amount += app.scholarship.amount
    
    # Payment Mode Distribution
    payment_modes = FeePayment.objects.filter(
        payment_status__in=['paid', 'partial']
    ).values('payment_mode').annotate(
        count=Count('id'),
        total=Sum('amount_paid')
    )
    
    # Fee Defaulters
    defaulters_count = FeePayment.objects.filter(
        payment_status='pending',
        amount_pending__gt=0
    ).values('student').distinct().count()
    
    context = {
        'page_title': 'Financial Analytics',
        'total_fee_collected': total_fee_collected,
        'partial_payments': partial_payments,
        'pending_fees': pending_fees,
        'total_expected': total_expected,
        'collection_rate': collection_rate,
        'monthly_revenue': monthly_revenue,
        'monthly_revenue_json': json.dumps(monthly_revenue),
        'course_fees': course_fees,
        'total_scholarships_disbursed': total_scholarships_disbursed,
        'scholarship_amount': scholarship_amount,
        'payment_modes': payment_modes,
        'defaulters_count': defaulters_count
    }
    return render(request, 'hod_template/financial_analytics.html', context)


@login_required(login_url='login')
def custom_report_builder(request):
    """Dynamic custom report builder with filters"""
    if request.user.user_type != '1':
        messages.error(request, 'Access denied')
        return redirect('login')
    
    # Get filter parameters
    report_type = request.GET.get('report_type', 'attendance')
    course_id = request.GET.get('course')
    department_id = request.GET.get('department')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    # Available options for filters
    courses = Course.objects.all()
    departments = Department.objects.all()
    sessions = Session.objects.all().order_by('-id')[:5]
    
    report_data = None
    
    if request.GET.get('generate'):
        # Generate report based on filters
        if report_type == 'attendance':
            query = AttendanceReport.objects.all()
            
            if course_id:
                students = Student.objects.filter(course_id=course_id)
                query = query.filter(student__in=students)
            
            if department_id:
                students = Student.objects.filter(course__department_id=department_id)
                query = query.filter(student__in=students)
            
            if start_date and end_date:
                query = query.filter(attendance_date__range=[start_date, end_date])
            
            total = query.count()
            present = query.filter(status=True).count()
            percentage = round((present / total) * 100, 2) if total > 0 else 0
            
            report_data = {
                'type': 'Attendance Report',
                'total_records': total,
                'present': present,
                'absent': total - present,
                'percentage': percentage
            }
        
        elif report_type == 'performance':
            query = StudentResult.objects.all()
            
            if course_id:
                students = Student.objects.filter(course_id=course_id)
                query = query.filter(student__in=students)
            
            if department_id:
                students = Student.objects.filter(course__department_id=department_id)
                query = query.filter(student__in=students)
            
            if query.exists():
                avg_marks = round(query.aggregate(Avg('marks'))['marks__avg'] or 0, 2)
                pass_count = query.filter(marks__gte=40).count()
                total = query.count()
                pass_rate = round((pass_count / total) * 100, 2) if total > 0 else 0
            else:
                avg_marks = 0
                pass_rate = 0
                total = 0
            
            report_data = {
                'type': 'Performance Report',
                'total_results': total,
                'avg_marks': avg_marks,
                'pass_rate': pass_rate
            }
        
        elif report_type == 'financial':
            query = FeePayment.objects.all()
            
            if start_date and end_date:
                query = query.filter(payment_date__range=[start_date, end_date])
            
            collected = query.filter(payment_status__in=['paid', 'partial']).aggregate(
                Sum('amount_paid'))['amount_paid__sum'] or 0
            pending = query.filter(payment_status__in=['pending', 'partial']).aggregate(
                Sum('amount_pending'))['amount_pending__sum'] or 0
            
            report_data = {
                'type': 'Financial Report',
                'collected': collected,
                'pending': pending,
                'total': collected + pending
            }
    
    context = {
        'page_title': 'Custom Report Builder',
        'courses': courses,
        'departments': departments,
        'sessions': sessions,
        'report_type': report_type,
        'report_data': report_data,
        'filters': {
            'course': course_id,
            'department': department_id,
            'start_date': start_date,
            'end_date': end_date
        }
    }
    return render(request, 'hod_template/custom_report_builder.html', context)


@login_required(login_url='login')
def report_builder(request):
    """Report builder - simplified interface"""
    return custom_report_builder(request)


@login_required(login_url='login')
def export_report(request):
    """Export reports in various formats (CSV, PDF, Excel)"""
    if request.user.user_type != '1':
        messages.error(request, 'Access denied')
        return redirect('login')
    
    export_format = request.GET.get('format', 'csv')
    report_type = request.GET.get('type', 'attendance')
    
    # Available report types
    available_reports = [
        {'value': 'attendance', 'name': 'Attendance Report'},
        {'value': 'performance', 'name': 'Academic Performance Report'},
        {'value': 'financial', 'name': 'Financial Report'},
        {'value': 'student_list', 'name': 'Student List'},
        {'value': 'staff_list', 'name': 'Staff List'},
        {'value': 'fee_defaulters', 'name': 'Fee Defaulters Report'}
    ]
    
    if request.GET.get('download'):
        # Generate and download report
        import csv
        from io import StringIO
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{report_type}_{datetime.now().strftime("%Y%m%d")}.csv"'
        
        writer = csv.writer(response)
        
        if report_type == 'attendance':
            writer.writerow(['Student Name', 'Roll Number', 'Course', 'Present', 'Total', 'Percentage'])
            for student in Student.objects.all()[:100]:
                records = AttendanceReport.objects.filter(student=student)
                if records.exists():
                    present = records.filter(status=True).count()
                    total = records.count()
                    percentage = round((present / total) * 100, 2) if total > 0 else 0
                    writer.writerow([
                        f"{student.admin.first_name} {student.admin.last_name}",
                        student.roll_number,
                        student.course.name,
                        present,
                        total,
                        percentage
                    ])
        
        elif report_type == 'student_list':
            writer.writerow(['Name', 'Roll Number', 'Course', 'Email', 'Mobile', 'Status'])
            for student in Student.objects.select_related('admin', 'course'):
                writer.writerow([
                    f"{student.admin.first_name} {student.admin.last_name}",
                    student.roll_number,
                    student.course.name,
                    student.admin.email,
                    student.mobile_number or 'N/A',
                    'Active' if student.admin.is_active else 'Inactive'
                ])
        
        return response
    
    context = {
        'page_title': 'Export Report',
        'available_reports': available_reports,
        'selected_type': report_type,
        'selected_format': export_format
    }
    return render(request, 'hod_template/export_report.html', context)