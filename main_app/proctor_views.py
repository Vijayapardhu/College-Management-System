from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q, Count, Avg
from datetime import datetime, timedelta

from .models import *


def proctor_home(request):
    """Proctor Dashboard - Shown to staff with is_proctor=True"""
    staff = get_object_or_404(Staff, admin=request.user)
    
    # Check if staff is a proctor
    if not staff.is_proctor:
        messages.error(request, "You don't have proctor privileges")
        return redirect('staff_home')
    
    # Get assigned students
    assigned_students = ProctorAssignment.objects.filter(staff=staff, is_active=True)
    total_students = assigned_students.count()
    
    # Get attendance statistics for assigned students
    students_list = [ps.student for ps in assigned_students]
    
    # Recent attendance data
    recent_attendance = AttendanceReport.objects.filter(
        student__in=students_list
    ).select_related('attendance', 'student').order_by('-created_at')[:10]
    
    # Students with low attendance (< 75%)
    low_attendance_students = []
    for student in students_list:
        total_attendance = AttendanceReport.objects.filter(student=student).count()
        if total_attendance > 0:
            present_count = AttendanceReport.objects.filter(student=student, status=True).count()
            attendance_percentage = (present_count / total_attendance) * 100
            if attendance_percentage < 75:
                low_attendance_students.append({
                    'student': student,
                    'percentage': round(attendance_percentage, 2)
                })
    
    # Upcoming events
    upcoming_events = Event.objects.filter(
        status='approved',
        event_date__gte=datetime.now()
    ).order_by('event_date')[:5]
    
    # Unread messages
    unread_messages = Message.objects.filter(receiver=request.user, is_read=False).count()
    
    context = {
        'page_title': 'Proctor Dashboard',
        'total_students': total_students,
        'recent_attendance': recent_attendance,
        'low_attendance_count': len(low_attendance_students),
        'low_attendance_students': low_attendance_students[:5],
        'upcoming_events': upcoming_events,
        'unread_messages': unread_messages,
    }
    
    return render(request, 'proctor_template/home_content.html', context)


def proctor_view_students(request):
    """View all assigned students"""
    staff = get_object_or_404(Staff, admin=request.user)
    
    if not staff.is_proctor:
        messages.error(request, "You don't have proctor privileges")
        return redirect('staff_home')
    
    assigned_students = ProctorAssignment.objects.filter(
        staff=staff, is_active=True
    ).select_related('student', 'student__admin', 'student__course')
    
    # Calculate attendance for each student
    student_data = []
    for ps in assigned_students:
        student = ps.student
        total_attendance = AttendanceReport.objects.filter(student=student).count()
        if total_attendance > 0:
            present_count = AttendanceReport.objects.filter(student=student, status=True).count()
            attendance_percentage = round((present_count / total_attendance) * 100, 2)
        else:
            attendance_percentage = 0
        
        # Get average marks
        results = StudentResult.objects.filter(student=student)
        if results.exists():
            avg_marks = results.aggregate(
                avg_test=Avg('test'),
                avg_exam=Avg('exam')
            )
            total_avg = round((avg_marks['avg_test'] + avg_marks['avg_exam']) / 2, 2) if avg_marks['avg_test'] and avg_marks['avg_exam'] else 0
        else:
            total_avg = 0
        
        student_data.append({
            'assignment': ps,
            'attendance_percentage': attendance_percentage,
            'average_marks': total_avg,
        })
    
    context = {
        'page_title': 'My Students',
        'student_data': student_data,
    }
    
    return render(request, 'proctor_template/view_students.html', context)


def proctor_student_details(request, student_id):
    """View detailed information about a specific student"""
    staff = get_object_or_404(Staff, admin=request.user)
    
    if not staff.is_proctor:
        messages.error(request, "You don't have proctor privileges")
        return redirect('staff_home')
    
    student = get_object_or_404(Student, id=student_id)
    
    # Verify this student is assigned to this staff member (proctor)
    assignment = ProctorAssignment.objects.filter(
        staff=staff,
        student=student,
        is_active=True
    ).first()
    
    if not assignment:
        messages.error(request, "You don't have access to this student's records")
        return redirect('proctor_view_students')
    
    # Attendance history
    attendance_records = AttendanceReport.objects.filter(
        student=student
    ).select_related('attendance', 'attendance__subject').order_by('-attendance__date')[:20]
    
    total_attendance = AttendanceReport.objects.filter(student=student).count()
    if total_attendance > 0:
        present_count = AttendanceReport.objects.filter(student=student, status=True).count()
        attendance_percentage = round((present_count / total_attendance) * 100, 2)
    else:
        attendance_percentage = 0
    
    # Academic results
    results = StudentResult.objects.filter(student=student).select_related('subject')
    
    # Leave history
    leaves = LeaveReportStudent.objects.filter(student=student).order_by('-created_at')[:10]
    
    # Event participation
    events = EventParticipation.objects.filter(student=student).select_related('event')[:10]
    
    context = {
        'page_title': f'Student Details: {student.admin.first_name} {student.admin.last_name}',
        'student': student,
        'assignment': assignment,
        'attendance_percentage': attendance_percentage,
        'attendance_records': attendance_records,
        'results': results,
        'leaves': leaves,
        'events': events,
    }
    
    return render(request, 'proctor_template/student_details.html', context)


def proctor_absentee_list(request):
    """Generate absentee list for assigned students"""
    staff = get_object_or_404(Staff, admin=request.user)
    
    if not staff.is_proctor:
        messages.error(request, "You don't have proctor privileges")
        return redirect('staff_home')
    
    if request.method == 'POST':
        date_from = request.POST.get('date_from')
        date_to = request.POST.get('date_to')
        
        if date_from and date_to:
            assigned_students = ProctorAssignment.objects.filter(
                staff=staff, is_active=True
            ).values_list('student', flat=True)
            
            # Get all attendance records in date range
            attendances = Attendance.objects.filter(
                date__range=[date_from, date_to]
            )
            
            absentee_data = []
            for attendance in attendances:
                absent_students = AttendanceReport.objects.filter(
                    attendance=attendance,
                    status=False,
                    student_id__in=assigned_students
                ).select_related('student', 'student__admin')
                
                for report in absent_students:
                    absentee_data.append({
                        'date': attendance.date,
                        'subject': attendance.subject.name,
                        'student': report.student,
                    })
            
            context = {
                'page_title': 'Absentee List',
                'absentee_data': absentee_data,
                'date_from': date_from,
                'date_to': date_to,
            }
            
            return render(request, 'proctor_template/absentee_results.html', context)
    
    context = {
        'page_title': 'Generate Absentee List',
    }
    
    return render(request, 'proctor_template/absentee_list.html', context)


def proctor_view_profile(request):
    """View and edit proctor profile"""
    staff = get_object_or_404(Staff, admin=request.user)
    
    if not staff.is_proctor:
        messages.error(request, "You don't have proctor privileges")
        return redirect('staff_home')
    
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        address = request.POST.get('address')
        gender = request.POST.get('gender')
        password = request.POST.get('password')
        
        try:
            user = request.user
            user.first_name = first_name
            user.last_name = last_name
            user.address = address
            user.gender = gender
            
            if password:
                user.set_password(password)
            
            user.save()
            messages.success(request, "Profile updated successfully!")
            return redirect('proctor_view_profile')
        except Exception as e:
            messages.error(request, f"Failed to update profile: {str(e)}")
    
    context = {
        'page_title': 'My Profile',
        'staff': staff,
    }
    
    return render(request, 'proctor_template/view_profile.html', context)


def proctor_send_message(request):
    """Send message to students or staff"""
    staff = get_object_or_404(Staff, admin=request.user)
    
    if not staff.is_proctor:
        messages.error(request, "You don't have proctor privileges")
        return redirect('staff_home')
    
    if request.method == 'POST':
        receiver_id = request.POST.get('receiver_id')
        subject = request.POST.get('subject')
        message_text = request.POST.get('message')
        
        try:
            receiver = CustomUser.objects.get(id=receiver_id)
            message = Message.objects.create(
                sender=request.user,
                receiver=receiver,
                subject=subject,
                message=message_text
            )
            messages.success(request, "Message sent successfully!")
            return redirect('proctor_messages')
        except Exception as e:
            messages.error(request, f"Failed to send message: {str(e)}")
    
    # Get assigned students and staff for the dropdown
    assigned_students = ProctorAssignment.objects.filter(
        staff=staff, is_active=True
    ).select_related('student', 'student__admin')
    
    staff_members = Staff.objects.all().select_related('admin')
    hod = Admin.objects.first()
    
    context = {
        'page_title': 'Send Message',
        'assigned_students': assigned_students,
        'staff_members': staff_members,
        'hod': hod,
    }
    
    return render(request, 'proctor_template/send_message.html', context)


def proctor_messages(request):
    """View all messages"""
    # Inbox
    inbox = Message.objects.filter(
        receiver=request.user
    ).select_related('sender').order_by('-created_at')
    
    # Sent messages
    sent = Message.objects.filter(
        sender=request.user
    ).select_related('receiver').order_by('-created_at')
    
    context = {
        'page_title': 'Messages',
        'inbox': inbox,
        'sent': sent,
    }
    
    return render(request, 'proctor_template/messages.html', context)


@csrf_exempt
def proctor_mark_message_read(request, message_id):
    """Mark a message as read"""
    if request.method == 'POST':
        try:
            message = Message.objects.get(id=message_id, receiver=request.user)
            message.is_read = True
            message.save()
            return JsonResponse({'status': 'success'})
        except:
            return JsonResponse({'status': 'error'})
    return JsonResponse({'status': 'error'})

