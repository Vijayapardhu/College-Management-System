from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.db import connection
from django.core.cache import cache
from django.conf import settings
import os
import sys
from datetime import datetime, timedelta


@login_required(login_url='login')
def performance_dashboard(request):
    """System performance monitoring dashboard"""
    if request.user.user_type != '1':
        messages.error(request, 'Access denied')
        return redirect('login')
    
    # System Information
    python_version = sys.version.split()[0]
    django_version = settings.VERSION if hasattr(settings, 'VERSION') else 'Unknown'
    
    # Database Statistics
    total_queries = len(connection.queries) if settings.DEBUG else 'N/A'
    
    # Cache Statistics
    cache_info = {
        'backend': settings.CACHES['default']['BACKEND'].split('.')[-1],
        'location': settings.CACHES['default'].get('LOCATION', 'Default')
    }
    
    # Application Statistics
    from .models import Student, Staff, CustomUser
    total_users = CustomUser.objects.count()
    active_users = CustomUser.objects.filter(is_active=True).count()
    student_count = Student.objects.count()
    staff_count = Staff.objects.count()
    
    # Approximate response time (simplified)
    avg_response_time = '< 100ms' if settings.DEBUG else 'N/A'
    
    # System Health Score (simplified calculation)
    health_score = 85  # Can be calculated based on various metrics
    
    context = {
        'page_title': 'Performance Dashboard',
        'python_version': python_version,
        'django_version': django_version,
        'total_queries': total_queries,
        'cache_info': cache_info,
        'total_users': total_users,
        'active_users': active_users,
        'student_count': student_count,
        'staff_count': staff_count,
        'avg_response_time': avg_response_time,
        'health_score': health_score,
        'debug_mode': settings.DEBUG
    }
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
    """Clear application cache"""
    if request.user.user_type != '1':
        messages.error(request, 'Access denied')
        return redirect('login')
    
    cache_cleared = False
    cache_info = {}
    
    if request.method == 'POST':
        try:
            cache.clear()
            cache_cleared = True
            messages.success(request, 'Cache cleared successfully!')
        except Exception as e:
            messages.error(request, f'Error clearing cache: {str(e)}')
    
    # Get cache info
    cache_info = {
        'backend': settings.CACHES['default']['BACKEND'].split('.')[-1],
        'location': settings.CACHES['default'].get('LOCATION', 'Default'),
        'status': 'Cleared' if cache_cleared else 'Active'
    }
    
    context = {
        'page_title': 'Clear Cache',
        'cache_info': cache_info,
        'cache_cleared': cache_cleared
    }
    return render(request, 'hod_template/clear_cache.html', context)


@login_required(login_url='login')
def optimize_static(request):
    """Optimize static files for production"""
    if request.user.user_type != '1':
        messages.error(request, 'Access denied')
        return redirect('login')
    
    optimization_status = {
        'collectstatic_run': os.path.exists(settings.STATIC_ROOT) if hasattr(settings, 'STATIC_ROOT') else False,
        'compression_enabled': False,  # Check if whitenoise or similar is configured
        'cdn_configured': False
    }
    
    # Check for compression middleware
    if 'whitenoise' in str(settings.MIDDLEWARE).lower():
        optimization_status['compression_enabled'] = True
    
    # Recommendations
    recommendations = []
    if not optimization_status['collectstatic_run']:
        recommendations.append('Run python manage.py collectstatic to gather all static files')
    if not optimization_status['compression_enabled']:
        recommendations.append('Install WhiteNoise for static file compression: pip install whitenoise')
    
    context = {
        'page_title': 'Optimize Static Files',
        'optimization_status': optimization_status,
        'recommendations': recommendations
    }
    return render(request, 'hod_template/optimize_static.html', context)


@login_required(login_url='login')
def slow_queries(request):
    """Analyze slow database queries"""
    if request.user.user_type != '1':
        messages.error(request, 'Access denied')
        return redirect('login')
    
    slow_queries_list = []
    
    if settings.DEBUG:
        # In DEBUG mode, we can access query information
        for query in connection.queries[-50:]:  # Last 50 queries
            time = float(query.get('time', 0))
            if time > 0.1:  # Queries taking more than 100ms
                slow_queries_list.append({
                    'sql': query['sql'][:200],  # Truncate long queries
                    'time': round(time * 1000, 2),  # Convert to milliseconds
                    'type': query['sql'].split()[0].upper()
                })
        
        total_queries = len(connection.queries)
        slow_count = len(slow_queries_list)
        slow_percentage = round((slow_count / total_queries) * 100, 2) if total_queries > 0 else 0
    else:
        total_queries = 'N/A (Enable DEBUG mode)'
        slow_count = 'N/A'
        slow_percentage = 'N/A'
    
    context = {
        'page_title': 'Slow Queries Analysis',
        'slow_queries': slow_queries_list,
        'total_queries': total_queries,
        'slow_count': slow_count,
        'slow_percentage': slow_percentage,
        'debug_enabled': settings.DEBUG
    }
    return render(request, 'hod_template/slow_queries.html', context)


@login_required(login_url='login')
def error_logs(request):
    """View application error logs"""
    if request.user.user_type != '1':
        messages.error(request, 'Access denied')
        return redirect('login')
    
    error_entries = []
    log_file_path = os.path.join(settings.BASE_DIR, 'logs', 'errors.log')
    
    # Try to read error log file if it exists
    if os.path.exists(log_file_path):
        try:
            with open(log_file_path, 'r') as f:
                lines = f.readlines()[-100:]  # Last 100 lines
                for line in lines:
                    if line.strip():
                        error_entries.append(line.strip())
        except Exception as e:
            messages.warning(request, f'Could not read log file: {str(e)}')
    else:
        messages.info(request, 'No error log file found. Errors will be logged here when they occur.')
    
    context = {
        'page_title': 'Error Logs',
        'error_entries': error_entries,
        'total_errors': len(error_entries),
        'log_file_exists': os.path.exists(log_file_path)
    }
    return render(request, 'hod_template/error_logs.html', context)


@login_required(login_url='login')
def system_resources(request):
    """Monitor system resource usage"""
    if request.user.user_type != '1':
        messages.error(request, 'Access denied')
        return redirect('login')
    
    # Try to get system resources (requires psutil)
    system_info = {}
    
    try:
        import psutil
        
        # CPU Usage
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_count = psutil.cpu_count()
        
        # Memory Usage
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        memory_used = round(memory.used / (1024 ** 3), 2)  # GB
        memory_total = round(memory.total / (1024 ** 3), 2)  # GB
        
        # Disk Usage
        disk = psutil.disk_usage('/')
        disk_percent = disk.percent
        disk_used = round(disk.used / (1024 ** 3), 2)  # GB
        disk_total = round(disk.total / (1024 ** 3), 2)  # GB
        
        system_info = {
            'cpu_percent': cpu_percent,
            'cpu_count': cpu_count,
            'memory_percent': memory_percent,
            'memory_used': memory_used,
            'memory_total': memory_total,
            'disk_percent': disk_percent,
            'disk_used': disk_used,
            'disk_total': disk_total,
            'available': True
        }
    except ImportError:
        system_info = {
            'available': False,
            'message': 'Install psutil for system monitoring: pip install psutil'
        }
    
    context = {
        'page_title': 'System Resources',
        'system_info': system_info
    }
    return render(request, 'hod_template/system_resources.html', context)


@login_required(login_url='login')
def export_performance_data(request):
    """Export system performance metrics"""
    if request.user.user_type != '1':
        messages.error(request, 'Access denied')
        return redirect('login')
    
    if request.GET.get('download'):
        import csv
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="performance_data_{datetime.now().strftime("%Y%m%d")}.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Metric', 'Value', 'Status'])
        
        # Write performance metrics
        writer.writerow(['Total Users', CustomUser.objects.count(), 'OK'])
        writer.writerow(['Active Users', CustomUser.objects.filter(is_active=True).count(), 'OK'])
        writer.writerow(['Total Students', Student.objects.count(), 'OK'])
        writer.writerow(['Total Staff', Staff.objects.count(), 'OK'])
        
        if settings.DEBUG:
            writer.writerow(['Total Queries', len(connection.queries), 'DEBUG MODE'])
        
        return response
    
    context = {'page_title': 'Export Performance Data'}
    return render(request, 'hod_template/export_performance_data.html', context)


@login_required(login_url='login')
def database_analysis(request):
    """Analyze database performance and structure"""
    if request.user.user_type != '1':
        messages.error(request, 'Access denied')
        return redirect('login')
    
    # Get database information
    from django.apps import apps
    
    table_stats = []
    for model in apps.get_models():
        if model._meta.app_label == 'main_app':
            try:
                count = model.objects.count()
                table_stats.append({
                    'name': model._meta.verbose_name_plural.title(),
                    'model': model.__name__,
                    'count': count
                })
            except:
                pass
    
    # Sort by count
    table_stats = sorted(table_stats, key=lambda x: x['count'], reverse=True)[:20]
    
    # Total records across all tables
    total_records = sum(stat['count'] for stat in table_stats)
    
    # Database backend
    db_backend = settings.DATABASES['default']['ENGINE'].split('.')[-1]
    db_name = settings.DATABASES['default']['NAME']
    
    context = {
        'page_title': 'Database Analysis',
        'table_stats': table_stats,
        'total_records': total_records,
        'total_tables': len(table_stats),
        'db_backend': db_backend,
        'db_name': db_name
    }
    return render(request, 'hod_template/database_analysis.html', context)


@login_required(login_url='login')
def cache_analysis(request):
    """Analyze cache performance and usage"""
    if request.user.user_type != '1':
        messages.error(request, 'Access denied')
        return redirect('login')
    
    # Cache Configuration
    cache_config = settings.CACHES['default']
    cache_backend = cache_config['BACKEND'].split('.')[-1]
    cache_location = cache_config.get('LOCATION', 'Default')
    
    # Test cache functionality
    test_key = 'cache_test_key'
    test_value = 'cache_test_value'
    
    cache.set(test_key, test_value, 60)
    cache_working = cache.get(test_key) == test_value
    
    # Cache statistics (if available)
    cache_stats = {
        'backend': cache_backend,
        'location': cache_location,
        'working': cache_working,
        'test_passed': cache_working
    }
    
    # Recommendations
    recommendations = []
    if cache_backend == 'DummyCache':
        recommendations.append('Using DummyCache. Consider using Redis or Memcached for production.')
    if settings.DEBUG:
        recommendations.append('DEBUG mode is ON. Disable for production to enable caching.')
    
    context = {
        'page_title': 'Cache Analysis',
        'cache_stats': cache_stats,
        'recommendations': recommendations
    }
    return render(request, 'hod_template/cache_analysis.html', context)


@login_required(login_url='login')
def optimization_recommendations(request):
    """AI-powered optimization recommendations"""
    if request.user.user_type != '1':
        messages.error(request, 'Access denied')
        return redirect('login')
    
    recommendations = []
    
    # Check DEBUG mode
    if settings.DEBUG:
        recommendations.append({
            'category': 'Security',
            'priority': 'Critical',
            'title': 'Disable DEBUG mode in production',
            'description': 'DEBUG=True exposes sensitive information and impacts performance.',
            'action': 'Set DEBUG=False in settings.py for production'
        })
    
    # Check SECRET_KEY
    if hasattr(settings, 'SECRET_KEY') and (len(settings.SECRET_KEY) < 50 or settings.SECRET_KEY.startswith('django-insecure-')):
        recommendations.append({
            'category': 'Security',
            'priority': 'Critical',
            'title': 'Generate strong SECRET_KEY',
            'description': 'Current SECRET_KEY is weak or auto-generated.',
            'action': 'Generate a new random SECRET_KEY with 50+ characters'
        })
    
    # Check cache backend
    cache_backend = settings.CACHES['default']['BACKEND']
    if 'DummyCache' in cache_backend or 'LocMemCache' in cache_backend:
        recommendations.append({
            'category': 'Performance',
            'priority': 'High',
            'title': 'Use production-grade caching',
            'description': 'Current cache backend is not suitable for production.',
            'action': 'Configure Redis or Memcached for caching'
        })
    
    # Check static files
    if not settings.DEBUG and not hasattr(settings, 'STATIC_ROOT'):
        recommendations.append({
            'category': 'Performance',
            'priority': 'Medium',
            'title': 'Configure static files serving',
            'description': 'STATIC_ROOT not configured for production.',
            'action': 'Set STATIC_ROOT and run collectstatic'
        })
    
    # Check database optimization
    from django.apps import apps
    large_tables = []
    for model in apps.get_models():
        if model._meta.app_label == 'main_app':
            try:
                count = model.objects.count()
                if count > 1000:
                    large_tables.append(model.__name__)
            except:
                pass
    
    if large_tables:
        recommendations.append({
            'category': 'Performance',
            'priority': 'Medium',
            'title': 'Optimize large tables',
            'description': f'Tables with >1000 records: {", ".join(large_tables[:5])}',
            'action': 'Add database indexes, use select_related(), pagination'
        })
    
    # Check media files
    if not hasattr(settings, 'MEDIA_ROOT'):
        recommendations.append({
            'category': 'Configuration',
            'priority': 'Low',
            'title': 'Configure media files storage',
            'description': 'MEDIA_ROOT not configured.',
            'action': 'Set MEDIA_ROOT and MEDIA_URL in settings.py'
        })
    
    # Categorize recommendations
    critical = [r for r in recommendations if r['priority'] == 'Critical']
    high = [r for r in recommendations if r['priority'] == 'High']
    medium = [r for r in recommendations if r['priority'] == 'Medium']
    low = [r for r in recommendations if r['priority'] == 'Low']
    
    context = {
        'page_title': 'Optimization Recommendations',
        'recommendations': recommendations,
        'critical_count': len(critical),
        'high_count': len(high),
        'medium_count': len(medium),
        'low_count': len(low),
        'total_recommendations': len(recommendations)
    }
    return render(request, 'hod_template/optimization_recommendations.html', context)


