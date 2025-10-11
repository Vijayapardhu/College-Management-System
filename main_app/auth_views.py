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
    except:
        data = request.POST
    
    action = data.get('action', 'login')
    
    # Handle different actions
    if action == 'login':
        return handle_login(request, data)
    elif action == 'verify_otp':
        return handle_verify_otp(request, data)
    elif action == 'resend_otp':
        return handle_resend_otp(request)
    else:
        return JsonResponse({'success': False, 'message': 'Invalid action'})


def handle_login(request, data):
    """Handle initial login and OTP generation"""
    email_or_id = data.get('email', '').strip()
    password = data.get('password', '')
    
    print(f"[AUTH] Login attempt: {email_or_id}")
    
    if not email_or_id or not password:
        print(f"[AUTH] Missing credentials")
        return JsonResponse({
            'success': False,
            'message': 'Please enter both email/ID and password'
        })
    
    # Authenticate user
    try:
        user = EmailBackend().authenticate(request, username=email_or_id, password=password)
        print(f"[AUTH] Authentication result: {user}")
    except Exception as e:
        print(f"[AUTH] Authentication exception: {e}")
        return JsonResponse({
            'success': False,
            'message': f'Authentication error: {str(e)}'
        })
    
    if not user:
        print(f"[AUTH] Authentication failed - invalid credentials")
        return JsonResponse({
            'success': False,
            'message': 'Invalid email/ID or password. Default password is: aditya'
        })
    
    # Generate OTP
    try:
        print(f"[AUTH] User authenticated: {user.email}")
        ip_address = request.META.get('REMOTE_ADDR', '127.0.0.1')
        otp_code = create_otp(user, ip_address)  # Returns OTP code directly from cache
        
        print(f"[AUTH] OTP generated: {otp_code}")
        
        # Store in session
        request.session['pending_user_id'] = user.id
        print(f"[AUTH] Stored user ID in session: {user.id}")
        
        # Try to send email
        email_sent = send_otp_email(user, otp_code)
        print(f"[AUTH] Email sent: {email_sent}")
        
        response_data = {
            'success': True,
            'email': user.email,
            'otp_sent': email_sent,
            'otp_code': otp_code if not email_sent else None,  # Show OTP if email fails
            'message': 'OTP sent to your email' if email_sent else 'OTP generated (email failed)'
        }
        print(f"[AUTH] Returning response: {response_data}")
        
        return JsonResponse(response_data)
        
    except Exception as e:
        print(f"[AUTH] Exception generating OTP: {e}")
        import traceback
        traceback.print_exc()
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
        return reverse('admin_home')
    elif user.user_type == '2':
        return reverse('staff_home')
    elif user.user_type == '3':
        return reverse('student_home')
    elif user.user_type == '4':
        return reverse('management_home')
    else:
        return reverse('student_home')


def logout_view(request):
    """Handle user logout"""
    logout(request)
    return redirect('login_with_otp')

