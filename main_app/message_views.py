from django.contrib import messages as django_messages
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q

from .models import *


def send_message(request):
    """Send a new message"""
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
            django_messages.success(request, "Message sent successfully!")
            
            # Redirect based on user type
            if request.user.user_type == '1':
                return redirect('admin_messages')
            elif request.user.user_type == '2':
                return redirect('staff_messages')
            elif request.user.user_type == '3':
                return redirect('student_messages')
            elif request.user.user_type == '4':
                return redirect('proctor_messages')
        except Exception as e:
            django_messages.error(request, f"Failed to send message: {str(e)}")
    
    # Get recipients based on user type
    recipients = []
    if request.user.user_type == '1':  # HOD
        recipients = CustomUser.objects.exclude(id=request.user.id).select_related()
        template = 'hod_template/send_message.html'
    elif request.user.user_type == '2':  # Staff
        # Staff can message HOD, students, and other staff
        recipients = CustomUser.objects.filter(
            Q(user_type='1') | Q(user_type='2') | Q(user_type='3')
        ).exclude(id=request.user.id)
        template = 'staff_template/send_message.html'
    elif request.user.user_type == '3':  # Student
        # Students can message HOD, staff, and their proctors
        student = Student.objects.get(admin=request.user)
        proctor_ids = ProctorAssignment.objects.filter(
            student=student, is_active=True
        ).values_list('staff__admin_id', flat=True)
        
        recipients = CustomUser.objects.filter(
            Q(user_type='1') | Q(user_type='2') | Q(id__in=proctor_ids)
        ).exclude(id=request.user.id)
        template = 'student_template/send_message.html'
    elif request.user.user_type == '2' and hasattr(request.user, 'staff') and request.user.staff.is_proctor:  # Staff acting as proctor
        # Proctors can message HOD, staff, and their assigned students
        staff = Staff.objects.get(admin=request.user)
        student_ids = ProctorAssignment.objects.filter(
            staff=staff, is_active=True
        ).values_list('student__admin_id', flat=True)
        
        recipients = CustomUser.objects.filter(
            Q(user_type='1') | Q(user_type='2') | Q(id__in=student_ids)
        ).exclude(id=request.user.id)
        template = 'proctor_template/send_message.html'
    
    context = {
        'page_title': 'Send Message',
        'recipients': recipients,
    }
    
    return render(request, template, context)


def view_messages(request):
    """View inbox and sent messages"""
    # Inbox - received messages
    inbox = Message.objects.filter(
        receiver=request.user
    ).select_related('sender').order_by('-created_at')
    
    # Sent messages
    sent = Message.objects.filter(
        sender=request.user
    ).select_related('receiver').order_by('-created_at')
    
    # Count unread messages
    unread_count = inbox.filter(is_read=False).count()
    
    # Determine template based on user type
    if request.user.user_type == '1':
        template = 'hod_template/messages.html'
    elif request.user.user_type == '2':
        template = 'staff_template/messages.html'
    elif request.user.user_type == '3':
        template = 'student_template/messages.html'
    elif request.user.user_type == '4':
        template = 'proctor_template/messages.html'
    
    context = {
        'page_title': 'Messages',
        'inbox': inbox,
        'sent': sent,
        'unread_count': unread_count,
    }
    
    return render(request, template, context)


def view_message(request, message_id):
    """View a specific message"""
    message = get_object_or_404(Message, id=message_id)
    
    # Check if user is authorized to view this message
    if message.sender != request.user and message.receiver != request.user:
        django_messages.error(request, "You don't have permission to view this message")
        return redirect('view_messages')
    
    # Mark as read if user is receiver
    if message.receiver == request.user and not message.is_read:
        message.is_read = True
        message.save()
    
    # Get replies
    replies = Message.objects.filter(parent_message=message).select_related('sender').order_by('created_at')
    
    # Get sender's student profile if sender is a student
    sender_student = None
    if message.sender.user_type == '3':
        try:
            from main_app.models import Student
            sender_student = Student.objects.select_related('course', 'session').get(admin=message.sender)
        except Student.DoesNotExist:
            sender_student = None
    
    # Determine template based on user type
    if request.user.user_type == '1':
        template = 'hod_template/view_message.html'
    elif request.user.user_type == '2':
        template = 'staff_template/view_message.html'
    elif request.user.user_type == '3':
        template = 'student_template/view_message.html'
    elif request.user.user_type == '4':
        template = 'proctor_template/view_message.html'
    
    context = {
        'page_title': 'Message Details',
        'message': message,
        'replies': replies,
        'sender_student': sender_student,
    }
    
    return render(request, template, context)


def reply_message(request, message_id):
    """Reply to a message"""
    if request.method == 'POST':
        original_message = get_object_or_404(Message, id=message_id)
        reply_text = request.POST.get('message')
        
        # Check authorization
        if original_message.sender != request.user and original_message.receiver != request.user:
            django_messages.error(request, "You don't have permission to reply to this message")
            return redirect('view_messages')
        
        try:
            # Determine receiver (send to the other party)
            if original_message.sender == request.user:
                receiver = original_message.receiver
            else:
                receiver = original_message.sender
            
            # Create reply
            reply = Message.objects.create(
                sender=request.user,
                receiver=receiver,
                subject=f"Re: {original_message.subject}",
                message=reply_text,
                parent_message=original_message
            )
            
            django_messages.success(request, "Reply sent successfully!")
            return redirect('view_message', message_id=message_id)
        except Exception as e:
            django_messages.error(request, f"Failed to send reply: {str(e)}")
    
    return redirect('view_message', message_id=message_id)


@csrf_exempt
def delete_message(request, message_id):
    """Delete a message"""
    if request.method == 'POST':
        try:
            message = Message.objects.get(id=message_id)
            
            # Only sender or receiver can delete
            if message.sender == request.user or message.receiver == request.user:
                message.delete()
                return JsonResponse({'status': 'success'})
            else:
                return JsonResponse({'status': 'error', 'message': 'Unauthorized'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    
    return JsonResponse({'status': 'error'})


@csrf_exempt
def mark_message_read(request, message_id):
    """Mark a message as read"""
    if request.method == 'POST':
        try:
            message = Message.objects.get(id=message_id, receiver=request.user)
            message.is_read = True
            message.save()
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    
    return JsonResponse({'status': 'error'})


@csrf_exempt
def mark_all_read(request):
    """Mark all messages as read"""
    if request.method == 'POST':
        try:
            Message.objects.filter(receiver=request.user, is_read=False).update(is_read=True)
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    
    return JsonResponse({'status': 'error'})

