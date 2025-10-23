from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse


@login_required(login_url='login')
def analytics_dashboard(request):
    """Analytics dashboard"""
    if request.user.user_type != '1':
        messages.error(request, 'Access denied')
        return redirect('login')
    
    context = {'page_title': 'Analytics Dashboard'}
    return render(request, 'hod_template/analytics_dashboard.html', context)


@login_required(login_url='login')
def attendance_analytics(request):
    """Attendance analytics"""
    if request.user.user_type != '1':
        messages.error(request, 'Access denied')
        return redirect('login')
    
    context = {'page_title': 'Attendance Analytics'}
    return render(request, 'hod_template/attendance_analytics.html', context)


@login_required(login_url='login')
def academic_performance_analytics(request):
    """Academic performance analytics"""
    if request.user.user_type != '1':
        messages.error(request, 'Access denied')
        return redirect('login')
    
    context = {'page_title': 'Academic Performance Analytics'}
    return render(request, 'hod_template/academic_performance_analytics.html', context)


@login_required(login_url='login')
def financial_analytics(request):
    """Financial analytics"""
    if request.user.user_type != '1':
        messages.error(request, 'Access denied')
        return redirect('login')
    
    context = {'page_title': 'Financial Analytics'}
    return render(request, 'hod_template/financial_analytics.html', context)


@login_required(login_url='login')
def custom_report_builder(request):
    """Custom report builder"""
    if request.user.user_type != '1':
        messages.error(request, 'Access denied')
        return redirect('login')
    
    context = {'page_title': 'Custom Report Builder'}
    return render(request, 'hod_template/custom_report_builder.html', context)


@login_required(login_url='login')
def report_builder(request):
    """Report builder (alias for custom_report_builder)"""
    if request.user.user_type != '1':
        messages.error(request, 'Access denied')
        return redirect('login')
    
    context = {'page_title': 'Report Builder'}
    return render(request, 'hod_template/report_builder.html', context)


@login_required(login_url='login')
def export_report(request):
    """Export report"""
    if request.user.user_type != '1':
        messages.error(request, 'Access denied')
        return redirect('login')
    
    context = {'page_title': 'Export Report'}
    return render(request, 'hod_template/export_report.html', context)