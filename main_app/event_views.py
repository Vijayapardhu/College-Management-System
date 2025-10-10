from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime

from .models import *


# HOD/Admin Event Views
def admin_view_events(request):
    """View all events for approval"""
    events = Event.objects.all().select_related('created_by', 'approved_by', 'course').order_by('-created_at')
    
    context = {
        'page_title': 'Event Management',
        'events': events,
    }
    
    return render(request, 'hod_template/view_events.html', context)


@csrf_exempt
def admin_approve_event(request):
    """Approve or reject an event"""
    if request.method == 'POST':
        event_id = request.POST.get('event_id')
        action = request.POST.get('action')  # 'approve' or 'reject'
        
        try:
            event = Event.objects.get(id=event_id)
            if action == 'approve':
                event.status = 'approved'
                event.approved_by = request.user
            else:
                event.status = 'rejected'
            event.save()
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    
    return JsonResponse({'status': 'error'})


def admin_create_event(request):
    """Create a new event (HOD can create directly approved events)"""
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        event_date = request.POST.get('event_date')
        venue = request.POST.get('venue')
        course_id = request.POST.get('course')
        max_participants = request.POST.get('max_participants', 0)
        
        try:
            course = Course.objects.get(id=course_id) if course_id else None
            event = Event.objects.create(
                title=title,
                description=description,
                event_date=event_date,
                venue=venue,
                course=course,
                max_participants=int(max_participants),
                created_by=request.user,
                approved_by=request.user,
                status='approved'
            )
            messages.success(request, "Event created successfully!")
            return redirect('admin_view_events')
        except Exception as e:
            messages.error(request, f"Failed to create event: {str(e)}")
    
    courses = Course.objects.all()
    context = {
        'page_title': 'Create Event',
        'courses': courses,
    }
    
    return render(request, 'hod_template/create_event.html', context)


# Staff Event Views
def staff_view_events(request):
    """Staff view all events"""
    approved_events = Event.objects.filter(status='approved').order_by('-event_date')
    
    # Get events created by this staff member
    my_events = Event.objects.filter(created_by=request.user).order_by('-created_at')
    
    context = {
        'page_title': 'Events',
        'approved_events': approved_events,
        'my_events': my_events,
    }
    
    return render(request, 'staff_template/view_events.html', context)


def staff_create_event(request):
    """Create event request (pending approval)"""
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        event_date = request.POST.get('event_date')
        venue = request.POST.get('venue')
        course_id = request.POST.get('course')
        max_participants = request.POST.get('max_participants', 0)
        
        try:
            course = Course.objects.get(id=course_id) if course_id else None
            event = Event.objects.create(
                title=title,
                description=description,
                event_date=event_date,
                venue=venue,
                course=course,
                max_participants=int(max_participants),
                created_by=request.user,
                status='pending'
            )
            messages.success(request, "Event proposal submitted for approval!")
            return redirect('staff_view_events')
        except Exception as e:
            messages.error(request, f"Failed to create event: {str(e)}")
    
    courses = Course.objects.all()
    context = {
        'page_title': 'Create Event',
        'courses': courses,
    }
    
    return render(request, 'staff_template/create_event.html', context)


# Student Event Views
def student_view_events(request):
    """Students view and register for approved events"""
    student = get_object_or_404(Student, admin=request.user)
    
    # Get upcoming approved events
    upcoming_events = Event.objects.filter(
        status='approved',
        event_date__gte=datetime.now()
    ).order_by('event_date')
    
    # Get events the student has registered for
    registered_events = EventParticipation.objects.filter(
        student=student
    ).select_related('event')
    
    registered_event_ids = [ep.event.id for ep in registered_events]
    
    # Add registration status to events
    event_data = []
    for event in upcoming_events:
        is_registered = event.id in registered_event_ids
        is_full = (event.max_participants > 0 and event.participant_count >= event.max_participants)
        event_data.append({
            'event': event,
            'is_registered': is_registered,
            'is_full': is_full,
        })
    
    # Past events the student participated in
    past_participations = EventParticipation.objects.filter(
        student=student,
        event__event_date__lt=datetime.now()
    ).select_related('event').order_by('-event__event_date')[:10]
    
    context = {
        'page_title': 'Events',
        'event_data': event_data,
        'registered_events': registered_events,
        'past_participations': past_participations,
    }
    
    return render(request, 'student_template/view_events.html', context)


@csrf_exempt
def student_register_event(request):
    """Register for an event"""
    if request.method == 'POST':
        event_id = request.POST.get('event_id')
        
        try:
            student = Student.objects.get(admin=request.user)
            event = Event.objects.get(id=event_id, status='approved')
            
            # Check if already registered
            existing = EventParticipation.objects.filter(event=event, student=student).exists()
            if existing:
                return JsonResponse({'status': 'error', 'message': 'Already registered'})
            
            # Check if event is full
            if event.max_participants > 0 and event.participant_count >= event.max_participants:
                return JsonResponse({'status': 'error', 'message': 'Event is full'})
            
            # Register
            EventParticipation.objects.create(event=event, student=student)
            return JsonResponse({'status': 'success', 'message': 'Registered successfully!'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    
    return JsonResponse({'status': 'error'})


@csrf_exempt
def student_unregister_event(request):
    """Unregister from an event"""
    if request.method == 'POST':
        event_id = request.POST.get('event_id')
        
        try:
            student = Student.objects.get(admin=request.user)
            event = Event.objects.get(id=event_id)
            
            EventParticipation.objects.filter(event=event, student=student).delete()
            return JsonResponse({'status': 'success', 'message': 'Unregistered successfully!'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    
    return JsonResponse({'status': 'error'})


# Proctor Event Views
def proctor_view_events(request):
    """Proctors view events and their students' participation"""
    staff = get_object_or_404(Staff, admin=request.user)
    
    if not staff.is_proctor:
        messages.error(request, "You don't have proctor privileges")
        return redirect('staff_home')
    
    # Get upcoming approved events
    upcoming_events = Event.objects.filter(
        status='approved',
        event_date__gte=datetime.now()
    ).order_by('event_date')
    
    # Get assigned students
    assigned_students = ProctorAssignment.objects.filter(
        staff=staff, is_active=True
    ).values_list('student', flat=True)
    
    # Get participations of assigned students
    student_participations = EventParticipation.objects.filter(
        student_id__in=assigned_students
    ).select_related('student', 'student__admin', 'event')
    
    context = {
        'page_title': 'Events',
        'upcoming_events': upcoming_events,
        'student_participations': student_participations,
    }
    
    return render(request, 'proctor_template/view_events.html', context)

