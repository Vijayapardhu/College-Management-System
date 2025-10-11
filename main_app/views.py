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
    return render(request, 'main_app/login.html')


def doLogin(request, **kwargs):
    if request.method != 'POST':
        return HttpResponse("<h4>Denied</h4>")
    else:
        from .otp_utils import create_otp, send_otp_email
        
        username_or_id = request.POST.get('email')  # Can be email, roll number, or employee ID
        password = request.POST.get('password')
        
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
                pass
        
        if user is not None:
            # Generate and send OTP
            try:
                ip_address = request.META.get('REMOTE_ADDR')
                otp = create_otp(user, ip_address)
                
                if send_otp_email(user, otp.otp_code):
                    # Store user ID in session temporarily
                    request.session['pending_login_user_id'] = user.id
                    request.session['otp_sent_time'] = str(otp.created_at)
                    
                    messages.success(request, f"OTP has been sent to {user.email}. Please check your email.")
                    return redirect(reverse("verify_otp"))
                else:
                    messages.error(request, "Failed to send OTP. Please try again later.")
                    return redirect("/")
                    
            except Exception as e:
                messages.error(request, f"Error sending OTP: {str(e)}")
                return redirect("/")
        else:
            messages.error(request, "Invalid Email/ID or Password")
            return redirect("/")



def verify_otp(request):
    """OTP Verification Page"""
    if request.user.is_authenticated:
        # Already logged in, redirect to appropriate dashboard
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
        messages.error(request, "No pending login found. Please login again.")
        return redirect("/")
    
    if request.method == 'POST':
        from .otp_utils import verify_otp as verify_otp_code
        from .models import CustomUser
        
        otp_code = request.POST.get('otp_code', '').strip()
        user_id = request.session.get('pending_login_user_id')
        
        try:
            user = CustomUser.objects.get(id=user_id)
            
            # Verify OTP
            is_valid, result = verify_otp_code(user, otp_code)
            
            if is_valid:
                # Clear session data
                del request.session['pending_login_user_id']
                if 'otp_sent_time' in request.session:
                    del request.session['otp_sent_time']
                
                # Login user
                login(request, user)
                messages.success(request, "Login successful!")
                
                # Redirect based on user type
                if user.user_type == '1':
                    return redirect(reverse("admin_home"))
                elif user.user_type == '2':
                    return redirect(reverse("staff_home"))
                elif user.user_type == '3':
                    return redirect(reverse("student_home"))
                elif user.user_type == '4':
                    return redirect(reverse("management_home"))
                else:
                    return redirect(reverse("student_home"))
            else:
                messages.error(request, result)  # result contains error message
                return redirect(reverse("verify_otp"))
                
        except CustomUser.DoesNotExist:
            messages.error(request, "User not found. Please login again.")
            del request.session['pending_login_user_id']
            return redirect("/")
        except Exception as e:
            messages.error(request, f"Error verifying OTP: {str(e)}")
            return redirect(reverse("verify_otp"))
    
    return render(request, 'main_app/verify_otp.html')


def resend_otp(request):
    """Resend OTP to user"""
    if 'pending_login_user_id' not in request.session:
        messages.error(request, "No pending login found. Please login again.")
        return redirect("/")
    
    from .otp_utils import resend_otp as resend_otp_code
    from .models import CustomUser
    
    user_id = request.session.get('pending_login_user_id')
    
    try:
        user = CustomUser.objects.get(id=user_id)
        ip_address = request.META.get('REMOTE_ADDR')
        
        success, result = resend_otp_code(user, ip_address)
        
        if success:
            request.session['otp_sent_time'] = str(result.created_at)
            messages.success(request, f"New OTP has been sent to {user.email}")
        else:
            messages.error(request, result)  # result contains error message
            
    except CustomUser.DoesNotExist:
        messages.error(request, "User not found. Please login again.")
        del request.session['pending_login_user_id']
        return redirect("/")
    except Exception as e:
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
