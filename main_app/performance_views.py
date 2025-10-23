from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse


@login_required(login_url='login')
def performance_dashboard(request):
    """Performance dashboard"""
    if request.user.user_type != '1':
        messages.error(request, 'Access denied')
        return redirect('login')
    
    context = {'page_title': 'Performance Dashboard'}
    return render(request, 'hod_template/performance_dashboard.html', context)


def performance_api(request):
    """Performance API endpoint"""
    if request.method == 'GET':
        # Add logic to get performance data
        data = {}  # Replace with actual data
        return JsonResponse({'data': data})
    return JsonResponse({'error': 'Invalid request'}, status=400)


@login_required(login_url='login')
def clear_cache(request):
    """Clear cache"""
    if request.user.user_type != '1':
        messages.error(request, 'Access denied')
        return redirect('login')
    
    context = {'page_title': 'Clear Cache'}
    return render(request, 'hod_template/clear_cache.html', context)


@login_required(login_url='login')
def optimize_static(request):
    """Optimize static files"""
    if request.user.user_type != '1':
        messages.error(request, 'Access denied')
        return redirect('login')
    
    context = {'page_title': 'Optimize Static Files'}
    return render(request, 'hod_template/optimize_static.html', context)


@login_required(login_url='login')
def slow_queries(request):
    """Slow queries analysis"""
    if request.user.user_type != '1':
        messages.error(request, 'Access denied')
        return redirect('login')
    
    context = {'page_title': 'Slow Queries Analysis'}
    return render(request, 'hod_template/slow_queries.html', context)


@login_required(login_url='login')
def error_logs(request):
    """Error logs"""
    if request.user.user_type != '1':
        messages.error(request, 'Access denied')
        return redirect('login')
    
    context = {'page_title': 'Error Logs'}
    return render(request, 'hod_template/error_logs.html', context)


@login_required(login_url='login')
def system_resources(request):
    """System resources"""
    if request.user.user_type != '1':
        messages.error(request, 'Access denied')
        return redirect('login')
    
    context = {'page_title': 'System Resources'}
    return render(request, 'hod_template/system_resources.html', context)


@login_required(login_url='login')
def export_performance_data(request):
    """Export performance data"""
    if request.user.user_type != '1':
        messages.error(request, 'Access denied')
        return redirect('login')
    
    context = {'page_title': 'Export Performance Data'}
    return render(request, 'hod_template/export_performance_data.html', context)


@login_required(login_url='login')
def database_analysis(request):
    """Database analysis"""
    if request.user.user_type != '1':
        messages.error(request, 'Access denied')
        return redirect('login')
    
    context = {'page_title': 'Database Analysis'}
    return render(request, 'hod_template/database_analysis.html', context)


@login_required(login_url='login')
def cache_analysis(request):
    """Cache analysis"""
    if request.user.user_type != '1':
        messages.error(request, 'Access denied')
        return redirect('login')
    
    context = {'page_title': 'Cache Analysis'}
    return render(request, 'hod_template/cache_analysis.html', context)


@login_required(login_url='login')
def optimization_recommendations(request):
    """Optimization recommendations"""
    if request.user.user_type != '1':
        messages.error(request, 'Access denied')
        return redirect('login')
    
    context = {'page_title': 'Optimization Recommendations'}
    return render(request, 'hod_template/optimization_recommendations.html', context)
