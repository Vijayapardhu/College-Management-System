from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse


@login_required(login_url='login')
def placement_dashboard(request):
    """Placement dashboard"""
    if request.user.user_type != '1':
        messages.error(request, 'Access denied')
        return redirect('login')
    
    context = {'page_title': 'Placement Dashboard'}
    return render(request, 'hod_template/placement_dashboard.html', context)


# Company Management
@login_required(login_url='login')
def manage_companies(request):
    """Manage companies"""
    if request.user.user_type != '1':
        messages.error(request, 'Access denied')
        return redirect('login')
    
    context = {'page_title': 'Manage Companies'}
    return render(request, 'hod_template/manage_companies.html', context)


@login_required(login_url='login')
def add_company(request):
    """Add company"""
    if request.user.user_type != '1':
        messages.error(request, 'Access denied')
        return redirect('login')
    
    context = {'page_title': 'Add Company'}
    return render(request, 'hod_template/add_company.html', context)


@login_required(login_url='login')
def edit_company(request, company_id):
    """Edit company"""
    if request.user.user_type != '1':
        messages.error(request, 'Access denied')
        return redirect('login')
    
    context = {'page_title': 'Edit Company', 'company_id': company_id}
    return render(request, 'hod_template/edit_company.html', context)


# Placement Drives
@login_required(login_url='login')
def manage_placement_drives(request):
    """Manage placement drives"""
    if request.user.user_type != '1':
        messages.error(request, 'Access denied')
        return redirect('login')
    
    context = {'page_title': 'Manage Placement Drives'}
    return render(request, 'hod_template/manage_placement_drives.html', context)


@login_required(login_url='login')
def add_placement_drive(request):
    """Add placement drive"""
    if request.user.user_type != '1':
        messages.error(request, 'Access denied')
        return redirect('login')
    
    context = {'page_title': 'Add Placement Drive'}
    return render(request, 'hod_template/add_placement_drive.html', context)


@login_required(login_url='login')
def edit_placement_drive(request, drive_id):
    """Edit placement drive"""
    if request.user.user_type != '1':
        messages.error(request, 'Access denied')
        return redirect('login')
    
    context = {'page_title': 'Edit Placement Drive', 'drive_id': drive_id}
    return render(request, 'hod_template/edit_placement_drive.html', context)


@login_required(login_url='login')
def view_placement_drive(request, drive_id):
    """View placement drive"""
    if request.user.user_type != '1':
        messages.error(request, 'Access denied')
        return redirect('login')
    
    context = {'page_title': 'View Placement Drive', 'drive_id': drive_id}
    return render(request, 'hod_template/view_placement_drive.html', context)


# Interview Management
@login_required(login_url='login')
def manage_interview_rounds(request, drive_id):
    """Manage interview rounds"""
    if request.user.user_type != '1':
        messages.error(request, 'Access denied')
        return redirect('login')
    
    context = {'page_title': 'Manage Interview Rounds', 'drive_id': drive_id}
    return render(request, 'hod_template/manage_interview_rounds.html', context)


@login_required(login_url='login')
def add_interview_round(request, drive_id):
    """Add interview round"""
    if request.user.user_type != '1':
        messages.error(request, 'Access denied')
        return redirect('login')
    
    context = {'page_title': 'Add Interview Round', 'drive_id': drive_id}
    return render(request, 'hod_template/add_interview_round.html', context)


@login_required(login_url='login')
def manage_interview_slots(request, round_id):
    """Manage interview slots"""
    if request.user.user_type != '1':
        messages.error(request, 'Access denied')
        return redirect('login')
    
    context = {'page_title': 'Manage Interview Slots', 'round_id': round_id}
    return render(request, 'hod_template/manage_interview_slots.html', context)


@login_required(login_url='login')
def create_bulk_slots(request, round_id):
    """Create bulk slots"""
    if request.user.user_type != '1':
        messages.error(request, 'Access denied')
        return redirect('login')
    
    context = {'page_title': 'Create Bulk Slots', 'round_id': round_id}
    return render(request, 'hod_template/create_bulk_slots.html', context)


@login_required(login_url='login')
def placement_analytics(request):
    """Placement analytics"""
    if request.user.user_type != '1':
        messages.error(request, 'Access denied')
        return redirect('login')
    
    context = {'page_title': 'Placement Analytics'}
    return render(request, 'hod_template/placement_analytics.html', context)


# Student Placement
@login_required(login_url='login')
def student_placement_dashboard(request):
    """Student placement dashboard"""
    if request.user.user_type != '3':
        messages.error(request, 'Access denied')
        return redirect('login')
    
    context = {'page_title': 'Placement Dashboard'}
    return render(request, 'student_template/placement_dashboard.html', context)


@login_required(login_url='login')
def student_placement_profile(request):
    """Student placement profile"""
    if request.user.user_type != '3':
        messages.error(request, 'Access denied')
        return redirect('login')
    
    context = {'page_title': 'Placement Profile'}
    return render(request, 'student_template/placement_profile.html', context)


@login_required(login_url='login')
def apply_placement(request, drive_id):
    """Apply for placement"""
    if request.user.user_type != '3':
        messages.error(request, 'Access denied')
        return redirect('login')
    
    context = {'page_title': 'Apply for Placement', 'drive_id': drive_id}
    return render(request, 'student_template/apply_placement.html', context)


@login_required(login_url='login')
def view_application_status(request, application_id):
    """View application status"""
    if request.user.user_type != '3':
        messages.error(request, 'Access denied')
        return redirect('login')
    
    context = {'page_title': 'Application Status', 'application_id': application_id}
    return render(request, 'student_template/view_application_status.html', context)


@login_required(login_url='login')
def book_interview_slot(request, round_id):
    """Book interview slot"""
    if request.user.user_type != '3':
        messages.error(request, 'Access denied')
        return redirect('login')
    
    context = {'page_title': 'Book Interview Slot', 'round_id': round_id}
    return render(request, 'student_template/book_interview_slot.html', context)


# AJAX Endpoints
def update_application_status(request):
    """AJAX endpoint to update application status"""
    if request.method == 'POST':
        # Add logic to update application status
        success = True  # Replace with actual logic
        return JsonResponse({'success': success})
    return JsonResponse({'error': 'Invalid request'}, status=400)


def respond_to_offer(request):
    """AJAX endpoint to respond to offer"""
    if request.method == 'POST':
        # Add logic to respond to offer
        success = True  # Replace with actual logic
        return JsonResponse({'success': success})
    return JsonResponse({'error': 'Invalid request'}, status=400)
