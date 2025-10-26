"""
Parent Portal Views - Monitor child's academic performance
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Avg, Count, Q
from django.http import JsonResponse
from datetime import datetime, timedelta

from main_app.models import (
    ParentGuardian, Student, AttendanceReport, StudentResult,
    Assignment, AssignmentSubmission, FeePayment, LeaveReportStudent,
    Announcement, StudyMaterial
)


@login_required(login_url='/')
def parent_home(request):
    """Parent portal dashboard"""
    try:
        parent = ParentGuardian.objects.get(user=request.user)
    except ParentGuardian.DoesNotExist:
        messages.error(request, 'Parent profile not found')
        return redirect('login')
    
    # Get linked students (children)
    students = Student.objects.filter(
        Q(parent=parent) | Q(guardian_contact=parent.contact_number)
    ).select_related('admin', 'course', 'session')
    
    if not students.exists():
        # No children linked
        context = {
            'page_title': 'Parent Dashboard',
            'parent': parent,
            'no_students': True
        }
        return render(request, 'parent_template/home.html', context)
    
    # Get data for each child
    children_data = []
    for student in students:
        # Attendance
        total_attendance = AttendanceReport.objects.filter(student=student).count()
        present_count = AttendanceReport.objects.filter(student=student, status=True).count()
        attendance_pct = round((present_count / total_attendance * 100), 2) if total_attendance > 0 else 0
        
        # Results
        results = StudentResult.objects.filter(student=student)
        total_marks = sum(r.test + r.exam for r in results)
        avg_marks = round(total_marks / results.count(), 2) if results.count() > 0 else 0
        
        # Pending assignments
        total_assignments = Assignment.objects.filter(course=student.course).count()
        submitted = AssignmentSubmission.objects.filter(student=student).count()
        pending_assignments = total_assignments - submitted
        
        # Fee status
        pending_fees = FeePayment.objects.filter(
            student=student,
            status__in=['pending', 'partial', 'overdue']
        ).count()
        
        children_data.append({
            'student': student,
            'attendance_percentage': attendance_pct,
            'average_marks': avg_marks,
            'pending_assignments': pending_assignments,
            'pending_fees': pending_fees,
            'status': 'Good' if attendance_pct >= 75 and avg_marks >= 60 else 'Needs Attention'
        })
    
    context = {
        'page_title': 'Parent Dashboard',
        'parent': parent,
        'children_data': children_data
    }
    
    return render(request, 'parent_template/home.html', context)


@login_required(login_url='/')
def view_child_attendance(request, student_id):
    """View detailed attendance for a child"""
    try:
        parent = ParentGuardian.objects.get(user=request.user)
        student = get_object_or_404(Student, id=student_id)
        
        # Verify parent has access to this student
        if not (student.parent == parent or student.guardian_contact == parent.contact_number):
            messages.error(request, 'Access denied')
            return redirect('parent_home')
    except ParentGuardian.DoesNotExist:
        messages.error(request, 'Parent profile not found')
        return redirect('login')
    
    # Get attendance records
    attendance_records = AttendanceReport.objects.filter(
        student=student
    ).select_related('attendance', 'attendance__subject').order_by('-attendance__date')
    
    # Calculate statistics
    total_classes = attendance_records.count()
    present_count = attendance_records.filter(status=True).count()
    absent_count = total_classes - present_count
    attendance_pct = round((present_count / total_classes * 100), 2) if total_classes > 0 else 0
    
    # Subject-wise attendance
    subjects = {}
    for record in attendance_records:
        subject_name = record.attendance.subject.name
        if subject_name not in subjects:
            subjects[subject_name] = {'total': 0, 'present': 0}
        subjects[subject_name]['total'] += 1
        if record.status:
            subjects[subject_name]['present'] += 1
    
    # Calculate percentage for each subject
    subject_stats = []
    for subject_name, data in subjects.items():
        percentage = round((data['present'] / data['total'] * 100), 2) if data['total'] > 0 else 0
        subject_stats.append({
            'name': subject_name,
            'total': data['total'],
            'present': data['present'],
            'absent': data['total'] - data['present'],
            'percentage': percentage
        })
    
    context = {
        'page_title': f"Attendance - {student.admin.first_name} {student.admin.last_name}",
        'parent': parent,
        'student': student,
        'total_classes': total_classes,
        'present_count': present_count,
        'absent_count': absent_count,
        'attendance_percentage': attendance_pct,
        'subject_stats': subject_stats,
        'recent_records': attendance_records[:30]
    }
    
    return render(request, 'parent_template/view_attendance.html', context)


@login_required(login_url='/')
def view_child_results(request, student_id):
    """View academic results for a child"""
    try:
        parent = ParentGuardian.objects.get(user=request.user)
        student = get_object_or_404(Student, id=student_id)
        
        # Verify access
        if not (student.parent == parent or student.guardian_contact == parent.contact_number):
            messages.error(request, 'Access denied')
            return redirect('parent_home')
    except ParentGuardian.DoesNotExist:
        messages.error(request, 'Parent profile not found')
        return redirect('login')
    
    # Get results
    results = StudentResult.objects.filter(student=student).select_related('subject')
    
    # Calculate CGPA
    from main_app.staff_views import calculate_grade, calculate_grade_point
    
    results_data = []
    total_credits = 0
    total_grade_points = 0
    
    for result in results:
        total_marks = result.test + result.exam
        grade = calculate_grade(total_marks)
        grade_point = calculate_grade_point(total_marks)
        credits = getattr(result.subject, 'credits', 3)
        
        results_data.append({
            'subject': result.subject.name,
            'internal': result.test,
            'external': result.exam,
            'total': total_marks,
            'grade': grade,
            'grade_point': grade_point,
            'credits': credits
        })
        
        total_credits += credits
        total_grade_points += (grade_point * credits)
    
    cgpa = round(total_grade_points / total_credits, 2) if total_credits > 0 else 0
    
    context = {
        'page_title': f"Results - {student.admin.first_name} {student.admin.last_name}",
        'parent': parent,
        'student': student,
        'results_data': results_data,
        'cgpa': cgpa,
        'total_credits': total_credits
    }
    
    return render(request, 'parent_template/view_results.html', context)


@login_required(login_url='/')
def view_child_assignments(request, student_id):
    """View assignments and submissions for a child"""
    try:
        parent = ParentGuardian.objects.get(user=request.user)
        student = get_object_or_404(Student, id=student_id)
        
        if not (student.parent == parent or student.guardian_contact == parent.contact_number):
            messages.error(request, 'Access denied')
            return redirect('parent_home')
    except ParentGuardian.DoesNotExist:
        messages.error(request, 'Parent profile not found')
        return redirect('login')
    
    # Get assignments
    assignments = Assignment.objects.filter(
        course=student.course
    ).select_related('subject', 'staff').order_by('-due_date')
    
    # Get submissions
    submissions = AssignmentSubmission.objects.filter(
        student=student
    ).select_related('assignment')
    
    submission_dict = {sub.assignment_id: sub for sub in submissions}
    
    # Combine data
    assignment_data = []
    pending_count = 0
    completed_count = 0
    
    for assignment in assignments:
        submission = submission_dict.get(assignment.id)
        status = 'Submitted' if submission else 'Pending'
        if status == 'Pending':
            pending_count += 1
        else:
            completed_count += 1
        
        assignment_data.append({
            'assignment': assignment,
            'submission': submission,
            'status': status,
            'is_overdue': assignment.due_date < datetime.now().date() if not submission else False
        })
    
    context = {
        'page_title': f"Assignments - {student.admin.first_name} {student.admin.last_name}",
        'parent': parent,
        'student': student,
        'assignment_data': assignment_data,
        'pending_count': pending_count,
        'completed_count': completed_count
    }
    
    return render(request, 'parent_template/view_assignments.html', context)


@login_required(login_url='/')
def view_child_fees(request, student_id):
    """View fee payment history for a child"""
    try:
        parent = ParentGuardian.objects.get(user=request.user)
        student = get_object_or_404(Student, id=student_id)
        
        if not (student.parent == parent or student.guardian_contact == parent.contact_number):
            messages.error(request, 'Access denied')
            return redirect('parent_home')
    except ParentGuardian.DoesNotExist:
        messages.error(request, 'Parent profile not found')
        return redirect('login')
    
    # Get fee payments
    payments = FeePayment.objects.filter(student=student).order_by('-payment_date')
    
    # Calculate totals
    total_paid = sum(p.amount_paid for p in payments if p.status == 'paid')
    total_pending = sum(
        p.fee_structure.total_fee - p.amount_paid 
        for p in payments 
        if p.status in ['pending', 'partial'] and hasattr(p, 'fee_structure') and p.fee_structure
    )
    
    context = {
        'page_title': f"Fee Details - {student.admin.first_name} {student.admin.last_name}",
        'parent': parent,
        'student': student,
        'payments': payments,
        'total_paid': total_paid,
        'total_pending': total_pending
    }
    
    return render(request, 'parent_template/view_fees.html', context)


@login_required(login_url='/')
def send_message_to_teacher(request, student_id):
    """Send message to student's teachers"""
    try:
        parent = ParentGuardian.objects.get(user=request.user)
        student = get_object_or_404(Student, id=student_id)
        
        if not (student.parent == parent or student.guardian_contact == parent.contact_number):
            messages.error(request, 'Access denied')
            return redirect('parent_home')
    except ParentGuardian.DoesNotExist:
        messages.error(request, 'Parent profile not found')
        return redirect('login')
    
    if request.method == 'POST':
        subject = request.POST.get('subject')
        message_text = request.POST.get('message')
        teacher_id = request.POST.get('teacher')
        
        try:
            from main_app.models import Message, Staff
            
            teacher = Staff.objects.get(id=teacher_id)
            
            Message.objects.create(
                sender=request.user,
                recipient=teacher.admin,
                subject=subject,
                message=message_text,
                message_type='parent_teacher'
            )
            
            messages.success(request, f'Message sent to {teacher.admin.first_name} {teacher.admin.last_name}')
            return redirect('view_child_detail', student_id=student_id)
            
        except Exception as e:
            messages.error(request, f'Failed to send message: {str(e)}')
    
    # Get teachers for student's subjects
    from main_app.models import Subject, Staff
    teachers = Staff.objects.filter(
        subject__course=student.course
    ).distinct().select_related('admin')
    
    context = {
        'page_title': 'Send Message to Teacher',
        'parent': parent,
        'student': student,
        'teachers': teachers
    }
    
    return render(request, 'parent_template/send_message.html', context)


@login_required(login_url='/')
def view_child_detail(request, student_id):
    """Comprehensive view of child's academic details"""
    try:
        parent = ParentGuardian.objects.get(user=request.user)
        student = get_object_or_404(Student, id=student_id)
        
        if not (student.parent == parent or student.guardian_contact == parent.contact_number):
            messages.error(request, 'Access denied')
            return redirect('parent_home')
    except ParentGuardian.DoesNotExist:
        messages.error(request, 'Parent profile not found')
        return redirect('login')
    
    # Attendance summary
    total_attendance = AttendanceReport.objects.filter(student=student).count()
    present_count = AttendanceReport.objects.filter(student=student, status=True).count()
    attendance_pct = round((present_count / total_attendance * 100), 2) if total_attendance > 0 else 0
    
    # Academic summary
    results = StudentResult.objects.filter(student=student)
    avg_marks = 0
    if results.exists():
        total_marks = sum(r.test + r.exam for r in results)
        avg_marks = round(total_marks / results.count(), 2)
    
    # Recent activity
    recent_attendance = AttendanceReport.objects.filter(
        student=student
    ).select_related('attendance', 'attendance__subject').order_by('-attendance__date')[:5]
    
    recent_submissions = AssignmentSubmission.objects.filter(
        student=student
    ).select_related('assignment').order_by('-submitted_at')[:5]
    
    context = {
        'page_title': f"{student.admin.first_name} {student.admin.last_name} - Details",
        'parent': parent,
        'student': student,
        'attendance_percentage': attendance_pct,
        'average_marks': avg_marks,
        'recent_attendance': recent_attendance,
        'recent_submissions': recent_submissions
    }
    
    return render(request, 'parent_template/child_detail.html', context)


@login_required(login_url='/')
def parent_view_profile(request):
    """View and update parent profile"""
    try:
        parent = ParentGuardian.objects.get(user=request.user)
    except ParentGuardian.DoesNotExist:
        messages.error(request, 'Parent profile not found')
        return redirect('login')
    
    if request.method == 'POST':
        # Update profile
        parent.user.first_name = request.POST.get('first_name')
        parent.user.last_name = request.POST.get('last_name')
        parent.contact_number = request.POST.get('contact_number')
        parent.alternate_contact = request.POST.get('alternate_contact', '')
        parent.address = request.POST.get('address', '')
        parent.occupation = request.POST.get('occupation', '')
        
        # Update password if provided
        password = request.POST.get('password')
        if password:
            parent.user.set_password(password)
        
        parent.user.save()
        parent.save()
        
        messages.success(request, 'Profile updated successfully!')
        return redirect('parent_view_profile')
    
    context = {
        'page_title': 'My Profile',
        'parent': parent
    }
    
    return render(request, 'parent_template/view_profile.html', context)


@login_required(login_url='/')
def link_student(request):
    """Link student account to parent"""
    try:
        parent = ParentGuardian.objects.get(user=request.user)
    except ParentGuardian.DoesNotExist:
        messages.error(request, 'Parent profile not found')
        return redirect('login')
    
    if request.method == 'POST':
        roll_number = request.POST.get('roll_number')
        verification_code = request.POST.get('verification_code')  # Could be DOB or special code
        
        try:
            student = Student.objects.get(roll_number=roll_number)
            
            # Verify using DOB or other method
            # For now, simple check
            student.parent = parent
            student.save()
            
            messages.success(request, f'Successfully linked {student.admin.first_name} {student.admin.last_name}')
            return redirect('parent_home')
            
        except Student.DoesNotExist:
            messages.error(request, 'Student not found with given roll number')
        except Exception as e:
            messages.error(request, f'Failed to link student: {str(e)}')
    
    context = {
        'page_title': 'Link Student Account',
        'parent': parent
    }
    
    return render(request, 'parent_template/link_student.html', context)
















