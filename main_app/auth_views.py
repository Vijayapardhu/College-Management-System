"""
Complete Authentication System with OTP
Clean implementation from scratch
"""
import json
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth import login, logout
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .models import CustomUser, OTP
from .otp_utils import create_otp, send_otp_email, verify_otp as verify_otp_code, resend_otp
from .EmailBackend import EmailBackend


@require_http_methods(["GET", "POST"])
def login_with_otp(request):
    """
    Single-page login with OTP verification
    Handles both AJAX and regular requests
    """
    # If already logged in, redirect to dashboard
    if request.user.is_authenticated:
        return redirect(get_dashboard_url(request.user))
    
    # GET request - show login page
    if request.method == 'GET':
        return render(request, 'main_app/login_with_otp.html')
    
    # POST request - handle login
    try:
        data = json.loads(request.body) if request.content_type == 'application/json' else request.POST
    except Exception as e:
        data = request.POST
    
    action = data.get('action', 'login')
    
    # Handle different actions
    try:
        if action == 'login':
            return handle_login(request, data)
        elif action == 'verify_otp':
            return handle_verify_otp(request, data)
        elif action == 'resend_otp':
            return handle_resend_otp(request)
        else:
            return JsonResponse({'success': False, 'message': 'Invalid action'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Server error: {str(e)}'})


def handle_login(request, data):
    """Handle initial login and OTP generation"""
    email_or_id = data.get('email', '').strip()
    password = data.get('password', '')
    
    if not email_or_id or not password:
        return JsonResponse({
            'success': False,
            'message': 'Please enter both email/ID and password'
        })
    
    # Authenticate user
    try:
        user = EmailBackend().authenticate(username=email_or_id, password=password)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Authentication error: {str(e)}'
        })
    
    if not user:
        return JsonResponse({
            'success': False,
            'message': 'Invalid email/ID or password. Default password is: aditya'
        })
    
    # Generate OTP
    try:
        ip_address = request.META.get('REMOTE_ADDR', '127.0.0.1')
        otp_code = create_otp(user, ip_address)
        
        # Store in session
        request.session['pending_user_id'] = user.id
        
        # Try to send email
        email_sent = send_otp_email(user, otp_code)
        
        response_data = {
            'success': True,
            'email': user.email,
            'otp_sent': email_sent,
            'otp_code': otp_code if not email_sent else None,  # Show OTP if email fails
            'message': 'OTP sent to your email' if email_sent else 'OTP generated (email failed)'
        }
        
        return JsonResponse(response_data)
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error generating OTP: {str(e)}'
        })


def handle_verify_otp(request, data):
    """Handle OTP verification"""
    otp_code = data.get('otp_code', '').strip()
    
    if not otp_code or len(otp_code) != 6:
        return JsonResponse({
            'success': False,
            'message': 'Please enter valid 6-digit OTP'
        })
    
    # Get pending user from session
    user_id = request.session.get('pending_user_id')
    if not user_id:
        return JsonResponse({
            'success': False,
            'message': 'Session expired. Please login again'
        })
    
    try:
        user = CustomUser.objects.get(id=user_id)
        
        # Verify OTP
        is_valid, result = verify_otp_code(user, otp_code)
        
        if is_valid:
            # Clear session data
            request.session.pop('pending_user_id', None)
            request.session.pop('otp_id', None)
            
            # Login user
            login(request, user, backend='main_app.EmailBackend.EmailBackend')
            
            # Get dashboard URL
            dashboard_url = get_dashboard_url(user)
            
            return JsonResponse({
                'success': True,
                'message': 'Login successful',
                'redirect_url': dashboard_url
            })
        else:
            return JsonResponse({
                'success': False,
                'message': result  # Error message from verify_otp_code
            })
            
    except CustomUser.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'User not found'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Verification error: {str(e)}'
        })


def handle_resend_otp(request):
    """Handle OTP resend"""
    user_id = request.session.get('pending_user_id')
    
    if not user_id:
        return JsonResponse({
            'success': False,
            'message': 'Session expired. Please login again'
        })
    
    try:
        user = CustomUser.objects.get(id=user_id)
        ip_address = request.META.get('REMOTE_ADDR', '127.0.0.1')
        
        # Generate new OTP (returns OTP code from cache)
        success, otp_code = resend_otp(user, ip_address)
        
        if not success:
            return JsonResponse({
                'success': False,
                'message': otp_code  # Error message
            })
        
        # Try to send email
        email_sent = send_otp_email(user, otp_code)
        
        return JsonResponse({
            'success': True,
            'email': user.email,
            'otp_sent': email_sent,
            'otp_code': otp_code if not email_sent else None,
            'message': 'New OTP sent' if email_sent else 'New OTP generated'
        })
        
    except CustomUser.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'User not found'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error: {str(e)}'
        })


def get_dashboard_url(user):
    """Get dashboard URL based on user type"""
    from django.urls import reverse
    
    if user.user_type == '1':
        return reverse('hod_home')
    elif user.user_type == '2':
        return reverse('staff_home')
    elif user.user_type == '3':
        return reverse('student_home')
    elif user.user_type == '4':
        return reverse('management_home')
    elif user.user_type == '5':
        return reverse('parent_home')
    else:
        return reverse('student_home')


def logout_view(request):
    """Handle user logout"""
    logout(request)
    return redirect('login_with_otp')

# ==================== PARENT LOGIN WITH OTP ====================

def parent_login(request):
    """Parent login with phone number and password, then OTP to email"""
    if request.user.is_authenticated:
        try:
            ParentGuardian.objects.get(user=request.user)
            return redirect('parent_home')
        except:
            pass
    
    if request.method == 'POST':
        action = request.POST.get('action', 'login')
        
        if action == 'login':
            # Step 1: Verify phone number and password
            phone_number = request.POST.get('phone_number', '').strip()
            password = request.POST.get('password', '').strip()
            
            if not phone_number or not password:
                messages.error(request, 'Please enter phone number and password')
                return render(request, 'registration/parent_login.html')
            
            # Remove any spaces or dashes
            phone_number = phone_number.replace(' ', '').replace('-', '')
            
            # Validate phone number (should be 10 digits without country code)
            if not phone_number.isdigit() or len(phone_number) != 10:
                messages.error(request, 'Please enter a valid 10-digit phone number (without country code)')
                return render(request, 'registration/parent_login.html')
            
            try:
                from .models import ParentGuardian
                # Find parent by phone number
                parent = ParentGuardian.objects.get(mobile_number=phone_number, is_active=True)
                
                # Verify password
                from django.contrib.auth.hashers import check_password
                if not check_password(password, parent.password_hash):
                    messages.error(request, 'Invalid phone number or password')
                    return render(request, 'registration/parent_login.html')
                
                # Create or get CustomUser for parent
                if not parent.user:
                    temp_user = CustomUser.objects.create(
                        email=parent.email,
                        first_name=parent.parent_name,
                        user_type='5',
                        is_active=True
                    )
                    temp_user.set_password(password)
                    temp_user.save()
                    parent.user = temp_user
                    parent.save()
                
                # Generate OTP and send to parent's email
                ip_address = request.META.get('REMOTE_ADDR', '127.0.0.1')
                otp_code = create_otp(parent.user, ip_address)
                email_sent = send_otp_email(parent.user, otp_code)
                
                # Store parent ID in session
                request.session['pending_parent_id'] = parent.id
                request.session['otp_sent'] = True
                
                if email_sent:
                    messages.success(request, f'OTP sent to your email: {parent.email}')
                else:
                    messages.warning(request, f'Could not send email. Your OTP is: {otp_code}')
                
                return render(request, 'registration/parent_login.html', {
                    'show_otp_form': True,
                    'parent_email': parent.email
                })
                
            except ParentGuardian.DoesNotExist:
                messages.error(request, 'No parent account found with this phone number')
                return render(request, 'registration/parent_login.html')
            except Exception as e:
                messages.error(request, f'Error: {str(e)}')
                return render(request, 'registration/parent_login.html')
        
        elif action == 'verify_otp':
            # Step 2: Verify OTP
            otp_code = request.POST.get('otp_code', '').strip()
            parent_id = request.session.get('pending_parent_id')
            
            if not parent_id:
                messages.error(request, 'Session expired. Please login again.')
                return redirect('parent_login')
            
            try:
                from .models import ParentGuardian
                parent = ParentGuardian.objects.get(id=parent_id)
                
                # Verify OTP
                from .otp_utils import verify_otp
                is_valid, message = verify_otp(parent.user, otp_code)
                
                if is_valid:
                    # OTP verified - login the user
                    login(request, parent.user, backend='django.contrib.auth.backends.ModelBackend')
                    
                    # Update last login
                    from django.utils import timezone
                    parent.last_login = timezone.now()
                    parent.save()
                    
                    # Clear session
                    request.session.pop('pending_parent_id', None)
                    request.session.pop('otp_sent', None)
                    
                    messages.success(request, 'Login successful!')
                    return redirect('parent_home')
                else:
                    messages.error(request, message)
                    return render(request, 'registration/parent_login.html', {
                        'show_otp_form': True,
                        'parent_email': parent.email
                    })
                    
            except ParentGuardian.DoesNotExist:
                messages.error(request, 'Invalid session. Please login again.')
                return redirect('parent_login')
            except Exception as e:
                messages.error(request, f'Error verifying OTP: {str(e)}')
                return render(request, 'registration/parent_login.html', {'show_otp_form': True})
        
        elif action == 'resend_otp':
            # Resend OTP
            parent_id = request.session.get('pending_parent_id')
            if not parent_id:
                messages.error(request, 'Session expired. Please login again.')
                return redirect('parent_login')
            
            try:
                from .models import ParentGuardian
                parent = ParentGuardian.objects.get(id=parent_id)
                from .otp_utils import resend_otp
                success, result = resend_otp(parent.user, request.META.get('REMOTE_ADDR'))
                
                if success:
                    messages.success(request, f'New OTP sent to {parent.email}')
                else:
                    messages.error(request, result)
                
                return render(request, 'registration/parent_login.html', {
                    'show_otp_form': True,
                    'parent_email': parent.email
                })
            except Exception as e:
                messages.error(request, f'Error: {str(e)}')
                return redirect('parent_login')
    
    return render(request, 'registration/parent_login.html')


