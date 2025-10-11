import json
import requests
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render, reverse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q

from .EmailBackend import EmailBackend
from .models import Attendance, Session, Subject, Student, Staff

# Create your views here.


def login_page(request):
    if request.user.is_authenticated:
        if request.user.user_type == '1':
            return redirect(reverse("admin_home"))
        elif request.user.user_type == '2':
            return redirect(reverse("staff_home"))
        elif request.user.user_type == '3':
            return redirect(reverse("student_home"))
    # Use single-page login
    return render(request, 'main_app/login_single_page.html')


def doLogin(request, **kwargs):
    if request.method != 'POST':
        return HttpResponse("<h4>Denied</h4>")
    
    from .otp_utils import create_otp, send_otp_email
    
    # Check if this is an AJAX request FIRST
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.content_type == 'application/json'
    
    print(f"[DEBUG] doLogin called - Is AJAX: {is_ajax}")
    print(f"[DEBUG] Request headers: X-Requested-With = {request.headers.get('X-Requested-With')}")
    print(f"[DEBUG] Content-Type: {request.content_type}")
    
    username_or_id = request.POST.get('email')  # Can be email, roll number, or employee ID
    password = request.POST.get('password')
    
    print(f"[DEBUG] Login attempt with: {username_or_id}")
    
    # Try to find user by email, username, or unique ID
    user = EmailBackend.authenticate(request, username=username_or_id, password=password)
    
    # If not found, try by student roll number or staff employee ID
    if user is None:
        try:
            # Try student roll number or admission number
            student = Student.objects.filter(
                Q(roll_number=username_or_id) | Q(admission_number=username_or_id)
            ).first()
            
            if student:
                user = EmailBackend.authenticate(request, username=student.admin.email, password=password)
            
            # Try staff employee ID
            if user is None:
                staff = Staff.objects.filter(employee_id=username_or_id).first()
                if staff:
                    user = EmailBackend.authenticate(request, username=staff.admin.email, password=password)
                    
        except Exception as e:
            print(f"[DEBUG] Error trying alternate auth: {e}")
            pass
    
    if user is not None:
        # Generate and send OTP
        try:
            ip_address = request.META.get('REMOTE_ADDR')
            otp = create_otp(user, ip_address)
            
            # Store user ID in session first (before email attempt)
            request.session['pending_login_user_id'] = user.id
            from django.utils import timezone
            request.session['otp_sent_time'] = str(timezone.now())
            request.session['otp_code_temp'] = otp  # OTP is now just the code string
            
            # Try to send email
            email_sent = send_otp_email(user, otp)  # otp is now just the code string
            
            print(f"[DEBUG] Email sent: {email_sent}")
            print(f"[DEBUG] Returning response - AJAX: {is_ajax}")
            
            # ALWAYS return JSON for AJAX requests
            if is_ajax:
                return JsonResponse({
                    'success': True,
                    'message': 'OTP sent successfully' if email_sent else f'Email failed. OTP: {otp}',
                    'email': user.email,
                    'user_id': user.id,
                    'otp_for_testing': otp if not email_sent else None
                })
            
            # Regular Response (redirect) - only for non-AJAX
            if email_sent:
                messages.success(request, f"✅ OTP has been sent to {user.email}. Please check your email inbox.")
            else:
                messages.warning(request, f"⚠️ Email sending failed. For testing, use OTP: {otp}")
            
            return redirect(reverse("verify_otp"))
                
        except Exception as e:
            print(f"[DEBUG] Exception in doLogin: {e}")
            import traceback
            traceback.print_exc()
            if is_ajax:
                return JsonResponse({
                    'success': False,
                    'message': f'Error: {str(e)}'
                })
            messages.error(request, f"Error: {str(e)}. Please try again.")
            return redirect("/")
    else:
        print(f"[DEBUG] Authentication failed")
        if is_ajax:
            return JsonResponse({
                'success': False,
                'message': 'Invalid Email/ID or Password'
            })
        messages.error(request, "❌ Invalid Email/ID or Password. Please try again.")
        return redirect("/")



def verify_otp(request):
    """OTP Verification Page"""
    # Check if this is an AJAX request
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.content_type == 'application/json'
    
    print(f"[DEBUG] verify_otp called - Is AJAX: {is_ajax}")
    
    if request.user.is_authenticated:
        # Already logged in
        if is_ajax:
            # Return redirect URL for AJAX
            if request.user.user_type == '1':
                return JsonResponse({'success': True, 'redirect_url': reverse("admin_home")})
            elif request.user.user_type == '2':
                return JsonResponse({'success': True, 'redirect_url': reverse("staff_home")})
            elif request.user.user_type == '3':
                return JsonResponse({'success': True, 'redirect_url': reverse("student_home")})
            elif request.user.user_type == '4':
                return JsonResponse({'success': True, 'redirect_url': reverse("management_home")})
        
        # Regular redirect for non-AJAX
        if request.user.user_type == '1':
            return redirect(reverse("admin_home"))
        elif request.user.user_type == '2':
            return redirect(reverse("staff_home"))
        elif request.user.user_type == '3':
            return redirect(reverse("student_home"))
        elif request.user.user_type == '4':
            return redirect(reverse("management_home"))
    
    # Check if there's a pending login
    if 'pending_login_user_id' not in request.session:
        print(f"[DEBUG] No pending login in session")
        if is_ajax:
            return JsonResponse({'success': False, 'message': 'No pending login found'})
        messages.error(request, "No pending login found. Please login again.")
        return redirect("/")
    
    if request.method == 'POST':
        from .otp_utils import verify_otp as verify_otp_code
        from .models import CustomUser
        
        otp_code = request.POST.get('otp_code', '').strip()
        user_id = request.session.get('pending_login_user_id')
        
        print(f"[DEBUG VIEW] POST request received")
        print(f"[DEBUG VIEW] Received OTP code: '{otp_code}'")
        print(f"[DEBUG VIEW] User ID from session: {user_id}")
        print(f"[DEBUG VIEW] Is AJAX: {is_ajax}")
        print(f"[DEBUG VIEW] All POST data: {request.POST}")
        
        # For AJAX requests, ALWAYS return JSON - never fall through to template
        try:
            user = CustomUser.objects.get(id=user_id)
            print(f"[DEBUG VIEW] Found user: {user.email}")
            
            # Verify OTP
            is_valid, result = verify_otp_code(user, otp_code)
            print(f"[DEBUG VIEW] Verification result: Valid={is_valid}, Message={result}")
            
            if is_valid:
                # Clear session data
                if 'pending_login_user_id' in request.session:
                    del request.session['pending_login_user_id']
                if 'otp_sent_time' in request.session:
                    del request.session['otp_sent_time']
                if 'otp_code_temp' in request.session:
                    del request.session['otp_code_temp']
                
                # Login user
                login(request, user)
                
                # Determine redirect URL
                if user.user_type == '1':
                    redirect_url = reverse("admin_home")
                elif user.user_type == '2':
                    redirect_url = reverse("staff_home")
                elif user.user_type == '3':
                    redirect_url = reverse("student_home")
                elif user.user_type == '4':
                    redirect_url = reverse("management_home")
                else:
                    redirect_url = reverse("student_home")
                
                # AJAX Response
                if is_ajax:
                    return JsonResponse({
                        'success': True,
                        'message': 'Login successful',
                        'redirect_url': redirect_url
                    })
                
                # Regular Response
                messages.success(request, "Login successful!")
                return redirect(redirect_url)
            else:
                # AJAX Response
                if is_ajax:
                    return JsonResponse({
                        'success': False,
                        'message': result
                    })
                
                messages.error(request, result)
                return redirect(reverse("verify_otp"))
                
        except CustomUser.DoesNotExist:
            if is_ajax:
                return JsonResponse({
                    'success': False,
                    'message': 'User not found'
                })
            messages.error(request, "User not found. Please login again.")
            if 'pending_login_user_id' in request.session:
                del request.session['pending_login_user_id']
            return redirect("/")
        except Exception as e:
            if is_ajax:
                return JsonResponse({
                    'success': False,
                    'message': f'Error: {str(e)}'
                })
            messages.error(request, f"Error verifying OTP: {str(e)}")
            return redirect(reverse("verify_otp"))
    
    # GET request - render template
    print(f"[DEBUG VIEW] GET request - rendering template")
    return render(request, 'main_app/verify_otp.html')


def resend_otp(request):
    """Resend OTP to user"""
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    
    if 'pending_login_user_id' not in request.session:
        if is_ajax:
            return JsonResponse({'success': False, 'message': 'No pending login found'})
        messages.error(request, "No pending login found. Please login again.")
        return redirect("/")
    
    from .otp_utils import resend_otp as resend_otp_code
    from .models import CustomUser
    
    user_id = request.session.get('pending_login_user_id')
    
    try:
        user = CustomUser.objects.get(id=user_id)
        ip_address = request.META.get('REMOTE_ADDR')
        
        success, otp_code = resend_otp_code(user, ip_address)
        
        if success:
            from django.utils import timezone
            request.session['otp_sent_time'] = str(timezone.now())
            
            # AJAX Response
            if is_ajax:
                return JsonResponse({
                    'success': True,
                    'message': f'New OTP sent to {user.email}',
                    'otp_for_testing': otp_code  # For testing when email fails
                })
            
            messages.success(request, f"New OTP has been sent to {user.email}")
        else:
            if is_ajax:
                return JsonResponse({'success': False, 'message': otp_code})  # otp_code contains error message
            messages.error(request, otp_code)  # otp_code contains error message
            
    except CustomUser.DoesNotExist:
        if is_ajax:
            return JsonResponse({'success': False, 'message': 'User not found'})
        messages.error(request, "User not found. Please login again.")
        if 'pending_login_user_id' in request.session:
            del request.session['pending_login_user_id']
        return redirect("/")
    except Exception as e:
        if is_ajax:
            return JsonResponse({'success': False, 'message': f'Error: {str(e)}'})
        messages.error(request, f"Error resending OTP: {str(e)}")
    
    return redirect(reverse("verify_otp"))


def public_data(request):
    """
    Public data access page - No authentication required
    Shows publicly available information about the institution
    """
    from .models import Department, Course, Program, PlacementDrive, Event
    
    # Get public data
    departments = Department.objects.all()
    programs = Program.objects.select_related('department').all()
    recent_placements = PlacementDrive.objects.filter(is_active=True).order_by('-created_at')[:5]
    upcoming_events = Event.objects.filter(is_public=True).order_by('date')[:5]
    
    context = {
        'departments': departments,
        'programs': programs,
        'recent_placements': recent_placements,
        'upcoming_events': upcoming_events,
    }
    
    return render(request, 'main_app/public_data.html', context)


def logout_user(request):
    if request.user != None:
        logout(request)
    return redirect("/")


@csrf_exempt
def get_attendance(request):
    subject_id = request.POST.get('subject')
    session_id = request.POST.get('session')
    try:
        subject = get_object_or_404(Subject, id=subject_id)
        session = get_object_or_404(Session, id=session_id)
        attendance = Attendance.objects.filter(subject=subject, session=session)
        attendance_list = []
        for attd in attendance:
            data = {
                    "id": attd.id,
                    "attendance_date": str(attd.date),
                    "session": attd.session.id
                    }
            attendance_list.append(data)
        return JsonResponse(json.dumps(attendance_list), safe=False)
    except Exception as e:
        return None


def showFirebaseJS(request):
    data = """
    // Give the service worker access to Firebase Messaging.
// Note that you can only use Firebase Messaging here, other Firebase libraries
// are not available in the service worker.
importScripts('https://www.gstatic.com/firebasejs/7.22.1/firebase-app.js');
importScripts('https://www.gstatic.com/firebasejs/7.22.1/firebase-messaging.js');

// Initialize the Firebase app in the service worker by passing in
// your app's Firebase config object.
// https://firebase.google.com/docs/web/setup#config-object
firebase.initializeApp({
    apiKey: "AIzaSyBarDWWHTfTMSrtc5Lj3Cdw5dEvjAkFwtM",
    authDomain: "sms-with-django.firebaseapp.com",
    databaseURL: "https://sms-with-django.firebaseio.com",
    projectId: "sms-with-django",
    storageBucket: "sms-with-django.appspot.com",
    messagingSenderId: "945324593139",
    appId: "1:945324593139:web:03fa99a8854bbd38420c86",
    measurementId: "G-2F2RXTL9GT"
});

// Retrieve an instance of Firebase Messaging so that it can handle background
// messages.
const messaging = firebase.messaging();
messaging.setBackgroundMessageHandler(function (payload) {
    const notification = JSON.parse(payload);
    const notificationOption = {
        body: notification.body,
        icon: notification.icon
    }
    return self.registration.showNotification(payload.notification.title, notificationOption);
});
    """
    return HttpResponse(data, content_type='application/javascript')
