from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps


def hod_required(view_func):
    """Decorator to require HOD/Admin access"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'Please login first')
            return redirect('login')
        
        if request.user.user_type != '1':
            messages.error(request, 'Access denied. HOD access required.')
            return redirect('login')
        
        return view_func(request, *args, **kwargs)
    return wrapper


def staff_required(view_func):
    """Decorator to require Staff access"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'Please login first')
            return redirect('login')
        
        if request.user.user_type not in ['1', '2']:
            messages.error(request, 'Access denied. Staff access required.')
            return redirect('login')
        
        return view_func(request, *args, **kwargs)
    return wrapper


def student_required(view_func):
    """Decorator to require Student access"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'Please login first')
            return redirect('login')
        
        if request.user.user_type != '3':
            messages.error(request, 'Access denied. Student access required.')
            return redirect('login')
        
        return view_func(request, *args, **kwargs)
    return wrapper


def management_required(view_func):
    """Decorator to require Management access"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'Please login first')
            return redirect('login')
        
        if request.user.user_type not in ['1', '4']:
            messages.error(request, 'Access denied. Management access required.')
            return redirect('login')
        
        return view_func(request, *args, **kwargs)
    return wrapper


def proctor_required(view_func):
    """Decorator to require Proctor access"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'Please login first')
            return redirect('login')
        
        if request.user.user_type not in ['1', '5']:
            messages.error(request, 'Access denied. Proctor access required.')
            return redirect('login')
        
        return view_func(request, *args, **kwargs)
    return wrapper


def login_required_custom(view_func):
    """Custom login required decorator"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'Please login first')
            return redirect('login')
        
        return view_func(request, *args, **kwargs)
    return wrapper
