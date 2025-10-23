from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse


@login_required(login_url='login')
def alumni_dashboard(request):
    """Alumni dashboard"""
    if request.user.user_type != '1':
        messages.error(request, 'Access denied')
        return redirect('login')
    
    context = {'page_title': 'Alumni Dashboard'}
    return render(request, 'hod_template/alumni_dashboard.html', context)


@login_required(login_url='login')
def alumni_directory(request):
    """Alumni directory"""
    if request.user.user_type != '1':
        messages.error(request, 'Access denied')
        return redirect('login')
    
    context = {'page_title': 'Alumni Directory'}
    return render(request, 'hod_template/alumni_directory.html', context)


@login_required(login_url='login')
def alumni_profile(request, alumni_id):
    """Alumni profile"""
    if request.user.user_type != '1':
        messages.error(request, 'Access denied')
        return redirect('login')
    
    context = {'page_title': 'Alumni Profile', 'alumni_id': alumni_id}
    return render(request, 'hod_template/alumni_profile.html', context)


@login_required(login_url='login')
def alumni_events(request):
    """Alumni events"""
    if request.user.user_type != '1':
        messages.error(request, 'Access denied')
        return redirect('login')
    
    context = {'page_title': 'Alumni Events'}
    return render(request, 'hod_template/alumni_events.html', context)


@login_required(login_url='login')
def alumni_event_detail(request, event_id):
    """Alumni event detail"""
    if request.user.user_type != '1':
        messages.error(request, 'Access denied')
        return redirect('login')
    
    context = {'page_title': 'Alumni Event Detail', 'event_id': event_id}
    return render(request, 'hod_template/alumni_event_detail.html', context)


@login_required(login_url='login')
def alumni_donations(request):
    """Alumni donations"""
    if request.user.user_type != '1':
        messages.error(request, 'Access denied')
        return redirect('login')
    
    context = {'page_title': 'Alumni Donations'}
    return render(request, 'hod_template/alumni_donations.html', context)


@login_required(login_url='login')
def alumni_donation_detail(request, campaign_id):
    """Alumni donation detail"""
    if request.user.user_type != '1':
        messages.error(request, 'Access denied')
        return redirect('login')
    
    context = {'page_title': 'Alumni Donation Detail', 'campaign_id': campaign_id}
    return render(request, 'hod_template/alumni_donation_detail.html', context)


@login_required(login_url='login')
def alumni_mentorship(request):
    """Alumni mentorship"""
    if request.user.user_type != '1':
        messages.error(request, 'Access denied')
        return redirect('login')
    
    context = {'page_title': 'Alumni Mentorship'}
    return render(request, 'hod_template/alumni_mentorship.html', context)


@login_required(login_url='login')
def alumni_newsletter(request):
    """Alumni newsletter"""
    if request.user.user_type != '1':
        messages.error(request, 'Access denied')
        return redirect('login')
    
    context = {'page_title': 'Alumni Newsletter'}
    return render(request, 'hod_template/alumni_newsletter.html', context)


@login_required(login_url='login')
def alumni_analytics(request):
    """Alumni analytics"""
    if request.user.user_type != '1':
        messages.error(request, 'Access denied')
        return redirect('login')
    
    context = {'page_title': 'Alumni Analytics'}
    return render(request, 'hod_template/alumni_analytics.html', context)


@login_required(login_url='login')
def mentorship_request(request):
    """Mentorship request"""
    if request.user.user_type not in ['3', '1']:
        messages.error(request, 'Access denied')
        return redirect('login')
    
    context = {'page_title': 'Mentorship Request'}
    return render(request, 'student_template/mentorship_request.html', context)


@login_required(login_url='login')
def alumni_jobs(request):
    """Alumni jobs"""
    if request.user.user_type not in ['3', '1']:
        messages.error(request, 'Access denied')
        return redirect('login')
    
    context = {'page_title': 'Alumni Jobs'}
    return render(request, 'student_template/alumni_jobs.html', context)


def get_available_mentors_ajax(request):
    """AJAX endpoint to get available mentors"""
    if request.method == 'GET':
        # Add logic to fetch available mentors
        mentors = []  # Replace with actual data
        return JsonResponse({'mentors': mentors})
    return JsonResponse({'error': 'Invalid request'}, status=400)


def alumni_stats_ajax(request):
    """AJAX endpoint for alumni stats"""
    if request.method == 'GET':
        # Add logic to get alumni stats
        stats = {}  # Replace with actual data
        return JsonResponse({'stats': stats})
    return JsonResponse({'error': 'Invalid request'}, status=400)
