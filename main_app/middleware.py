from django.utils.deprecation import MiddlewareMixin
from django.urls import reverse
from django.shortcuts import redirect


class LoginCheckMiddleWare(MiddlewareMixin):
    def process_view(self, request, view_func, view_args, view_kwargs):
        modulename = view_func.__module__
        user = request.user # Who is the current user ?
        if user.is_authenticated:
            if user.user_type == '1': # Is it the HOD/Admin
                if modulename == 'main_app.student_views':
                    return redirect(reverse('hod_home'))
            elif user.user_type == '2': #  Staff :-/ ?
                if modulename == 'main_app.student_views' or modulename == 'main_app.hod_views':
                    return redirect(reverse('staff_home'))
            elif user.user_type == '3': # ... or Student ?
                if modulename == 'main_app.hod_views' or modulename == 'main_app.staff_views':
                    return redirect(reverse('student_home'))
            else: # None of the aforementioned ? Please take the user to login page
                return redirect(reverse('login_page'))
        else:
            # Allow access to login pages and auth views
            if (request.path == reverse('login_page') or 
                modulename == 'django.contrib.auth.views' or 
                request.path == reverse('user_login') or
                request.path == '/' or  # Allow root path
                modulename == 'main_app.auth_views'):  # Allow auth_views
                pass
            else:
                # For AJAX requests, return JSON error instead of redirect
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    from django.http import JsonResponse
                    return JsonResponse({'success': False, 'message': 'Authentication required'}, status=401)
                else:
                    return redirect(reverse('login_page'))
