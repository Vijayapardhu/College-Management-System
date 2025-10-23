from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse


@login_required(login_url='login')
def admission_dashboard(request):
    """Admission dashboard view"""
    if request.user.user_type != '1':
        messages.error(request, 'Access denied')
        return redirect('login')
    
    context = {
        'page_title': 'Admission Dashboard'
    }
    return render(request, 'hod_template/admission_dashboard.html', context)


@login_required(login_url='login')
def manage_applications(request):
    """Manage admission applications"""
    if request.user.user_type != '1':
        messages.error(request, 'Access denied')
        return redirect('login')
    
    context = {
        'page_title': 'Manage Applications'
    }
    return render(request, 'hod_template/manage_applications.html', context)


@login_required(login_url='login')
def view_application(request, application_id):
    """View specific application"""
    if request.user.user_type != '1':
        messages.error(request, 'Access denied')
        return redirect('login')
    
    context = {
        'page_title': 'View Application',
        'application_id': application_id
    }
    return render(request, 'hod_template/view_application.html', context)


@login_required(login_url='login')
def review_applications(request):
    """Review admission applications"""
    if request.user.user_type != '1':
        messages.error(request, 'Access denied')
        return redirect('login')
    
    context = {
        'page_title': 'Review Applications'
    }
    return render(request, 'hod_template/review_applications.html', context)


@login_required(login_url='login')
def admission_statistics(request):
    """Admission statistics"""
    if request.user.user_type != '1':
        messages.error(request, 'Access denied')
        return redirect('login')
    
    context = {
        'page_title': 'Admission Statistics'
    }
    return render(request, 'hod_template/admission_statistics.html', context)


@login_required(login_url='login')
def make_decision(request, application_id):
    """Make admission decision"""
    if request.user.user_type != '1':
        messages.error(request, 'Access denied')
        return redirect('login')
    
    context = {
        'page_title': 'Make Decision',
        'application_id': application_id
    }
    return render(request, 'hod_template/make_decision.html', context)


@login_required(login_url='login')
def admission_reports(request):
    """Admission reports"""
    if request.user.user_type != '1':
        messages.error(request, 'Access denied')
        return redirect('login')
    
    context = {
        'page_title': 'Admission Reports'
    }
    return render(request, 'hod_template/admission_reports.html', context)


@login_required(login_url='login')
def verify_documents(request, document_id):
    """Verify admission documents"""
    if request.user.user_type != '1':
        messages.error(request, 'Access denied')
        return redirect('login')
    
    context = {
        'page_title': 'Verify Documents',
        'document_id': document_id
    }
    return render(request, 'hod_template/verify_documents.html', context)


@login_required(login_url='login')
def admission_settings(request):
    """Admission settings"""
    if request.user.user_type != '1':
        messages.error(request, 'Access denied')
        return redirect('login')
    
    context = {
        'page_title': 'Admission Settings'
    }
    return render(request, 'hod_template/admission_settings.html', context)


@login_required(login_url='login')
def bulk_admit_students(request):
    """Bulk admit students"""
    if request.user.user_type != '1':
        messages.error(request, 'Access denied')
        return redirect('login')
    
    context = {
        'page_title': 'Bulk Admit Students'
    }
    return render(request, 'hod_template/bulk_admit_students.html', context)


@login_required(login_url='login')
def apply_admission(request):
    """Student apply for admission"""
    if request.user.user_type != '3':
        messages.error(request, 'Access denied')
        return redirect('login')
    
    context = {
        'page_title': 'Apply for Admission'
    }
    return render(request, 'student_template/apply_admission.html', context)


@login_required(login_url='login')
def upload_documents(request, application_id):
    """Upload admission documents"""
    if request.user.user_type != '3':
        messages.error(request, 'Access denied')
        return redirect('login')
    
    context = {
        'page_title': 'Upload Documents',
        'application_id': application_id
    }
    return render(request, 'student_template/upload_documents.html', context)


@login_required(login_url='login')
def track_application(request):
    """Track admission application"""
    if request.user.user_type != '3':
        messages.error(request, 'Access denied')
        return redirect('login')
    
    context = {
        'page_title': 'Track Application'
    }
    return render(request, 'student_template/track_application.html', context)


def get_programs_for_session(request):
    """AJAX endpoint to get programs for a session"""
    if request.method == 'GET':
        session_id = request.GET.get('session_id')
        # Add logic to fetch programs for the session
        programs = []  # Replace with actual data
        return JsonResponse({'programs': programs})
    return JsonResponse({'error': 'Invalid request'}, status=400)


def check_application_status(request):
    """AJAX endpoint to check application status"""
    if request.method == 'GET':
        application_id = request.GET.get('application_id')
        # Add logic to check application status
        status = 'pending'  # Replace with actual logic
        return JsonResponse({'status': status})
    return JsonResponse({'error': 'Invalid request'}, status=400)