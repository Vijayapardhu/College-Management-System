"""
REST API Views for EduVision College Management System
Comprehensive API with JWT authentication and documentation
"""
import json
from datetime import datetime, timedelta
from django.shortcuts import get_object_or_404
from django.contrib.auth import authenticate
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.db.models import Q, Count, Avg, Sum
from django.core.paginator import Paginator
from django.core.serializers import serialize
from django.utils import timezone
from django.conf import settings
import jwt
from functools import wraps

from .models import (
    CustomUser, Student, Staff, Course, Subject, Session, Department,
    Attendance, AttendanceReport, StudentResult, FeePayment,
    LeaveReportStudent, LeaveReportStaff, FeedbackStudent, FeedbackStaff,
    Event, EventParticipation, StudyMaterial, Message, Assignment,
    AssignmentSubmission, PlacementDrive, PlacementApplication,
    Alumni, Management, AdmissionApplication
)

from .serializers import (
    SubjectSerializer,
    TimetableSerializer,
    CurriculumSubjectSerializer,
)
from .utils.query_helpers import (
    get_enrolled_subjects_for_student,
    get_class_timetable,
    get_curriculum_subjects,
)


def get_token_for_user(user):
    """Generate JWT token for user"""
    payload = {
        'user_id': user.id,
        'username': user.username,
        'user_type': user.user_type,
        'exp': datetime.utcnow() + timedelta(days=7),
        'iat': datetime.utcnow()
    }
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
    return token


def jwt_required(view_func):
    """JWT authentication decorator"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        auth_header = request.META.get('HTTP_AUTHORIZATION')
        if not auth_header or not auth_header.startswith('Bearer '):
            return JsonResponse({'error': 'No valid token provided'}, status=401)
        
        token = auth_header.split(' ')[1]
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            user_id = payload.get('user_id')
            user = CustomUser.objects.get(id=user_id)
            request.user = user
            return view_func(request, *args, **kwargs)
        except jwt.ExpiredSignatureError:
            return JsonResponse({'error': 'Token has expired'}, status=401)
        except jwt.InvalidTokenError:
            return JsonResponse({'error': 'Invalid token'}, status=401)
        except CustomUser.DoesNotExist:
            return JsonResponse({'error': 'User not found'}, status=401)
    
    return wrapper


def role_required(allowed_roles):
    """Role-based access control decorator"""
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not hasattr(request, 'user') or not request.user.is_authenticated:
                return JsonResponse({'error': 'Authentication required'}, status=401)
            
            if request.user.user_type not in allowed_roles:
                return JsonResponse({'error': 'Insufficient permissions'}, status=403)
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


@csrf_exempt
@require_http_methods(["POST"])
def api_login(request):
    """API Login endpoint"""
    try:
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return JsonResponse({'error': 'Username and password required'}, status=400)
        
        user = authenticate(username=username, password=password)
        if user and user.is_active:
            token = get_token_for_user(user)
            return JsonResponse({
                'success': True,
                'token': token,
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'user_type': user.user_type,
                    'profile_pic': user.profile_pic.url if user.profile_pic else None
                }
            })
        else:
            return JsonResponse({'error': 'Invalid credentials'}, status=401)
    
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@jwt_required
@require_http_methods(["GET"])
def api_profile(request):
    """Get user profile"""
    try:
        user = request.user
        profile_data = {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'user_type': user.user_type,
            'profile_pic': user.profile_pic.url if user.profile_pic else None,
            'address': user.address,
            'gender': user.gender,
            'created_at': user.created_at.isoformat() if hasattr(user, 'created_at') else None
        }
        
        # Add role-specific profile data
        if user.user_type == '3':  # Student
            try:
                student = Student.objects.get(admin=user)
                profile_data.update({
                    'roll_number': student.roll_number,
                    'course': student.course.name if student.course else None,
                    'session': student.session.session_start_year if student.session else None
                })
            except Student.DoesNotExist:
                pass
        
        elif user.user_type == '2':  # Staff
            try:
                staff = Staff.objects.get(admin=user)
                profile_data.update({
                    'employee_id': staff.employee_id,
                    'designation': staff.designation,
                    'department': staff.department.name if staff.department else None,
                    'qualification': staff.qualification
                })
            except Staff.DoesNotExist:
                pass
        
        return JsonResponse({'success': True, 'profile': profile_data})
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@jwt_required
@role_required(['1', '2'])  # HOD and Staff
@require_http_methods(["GET"])
def api_students(request):
    """Get students list with pagination and filtering"""
    try:
        page = int(request.GET.get('page', 1))
        per_page = int(request.GET.get('per_page', 20))
        search = request.GET.get('search', '')
        course_id = request.GET.get('course_id')
        session_id = request.GET.get('session_id')
        
        students = Student.objects.select_related('admin', 'course', 'session').all()
        
        # Apply filters
        if search:
            students = students.filter(
                Q(admin__first_name__icontains=search) |
                Q(admin__last_name__icontains=search) |
                Q(roll_number__icontains=search) |
                Q(admin__email__icontains=search)
            )
        
        if course_id:
            students = students.filter(course_id=course_id)
        
        if session_id:
            students = students.filter(session_id=session_id)
        
        # Pagination
        paginator = Paginator(students, per_page)
        page_obj = paginator.get_page(page)
        
        students_data = []
        for student in page_obj:
            students_data.append({
                'id': student.id,
                'roll_number': student.roll_number,
                'first_name': student.admin.first_name,
                'last_name': student.admin.last_name,
                'email': student.admin.email,
                'course': student.course.name if student.course else None,
                'session': f"{student.session.session_start_year}-{student.session.session_end_year}" if student.session else None,
                'profile_pic': student.admin.profile_pic.url if student.admin.profile_pic else None,
                'created_at': student.admin.created_at.isoformat() if hasattr(student.admin, 'created_at') else None
            })
        
        return JsonResponse({
            'success': True,
            'students': students_data,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total_pages': paginator.num_pages,
                'total_count': paginator.count,
                'has_next': page_obj.has_next(),
                'has_previous': page_obj.has_previous()
            }
        })
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@jwt_required
@role_required(['1', '2'])  # HOD and Staff
@require_http_methods(["GET"])
def api_student_detail(request, student_id):
    """Get student detail"""
    try:
        student = get_object_or_404(Student, id=student_id)
        
        # Get attendance data
        attendance_reports = AttendanceReport.objects.filter(student=student)
        total_attendance = attendance_reports.count()
        present_count = attendance_reports.filter(status=True).count()
        attendance_percentage = (present_count / total_attendance * 100) if total_attendance > 0 else 0
        
        # Get academic results
        results = StudentResult.objects.filter(student=student)
        avg_marks = results.aggregate(avg=Avg('exam'))['avg'] or 0
        
        student_data = {
            'id': student.id,
            'roll_number': student.roll_number,
            'admission_number': student.admission_number,
            'first_name': student.admin.first_name,
            'last_name': student.admin.last_name,
            'email': student.admin.email,
            'phone': student.mobile_number,
            'address': student.admin.address,
            'gender': student.admin.gender,
            'date_of_birth': student.date_of_birth.isoformat() if student.date_of_birth else None,
            'course': {
                'id': student.course.id,
                'name': student.course.name
            } if student.course else None,
            'session': {
                'id': student.session.id,
                'start_year': student.session.session_start_year,
                'end_year': student.session.session_end_year
            } if student.session else None,
            'profile_pic': student.admin.profile_pic.url if student.admin.profile_pic else None,
            'attendance': {
                'total_classes': total_attendance,
                'present_classes': present_count,
                'percentage': round(attendance_percentage, 2)
            },
            'academic': {
                'average_marks': round(avg_marks, 2),
                'total_subjects': results.count()
            },
            'created_at': student.admin.created_at.isoformat() if hasattr(student.admin, 'created_at') else None
        }
        
        return JsonResponse({'success': True, 'student': student_data})
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@jwt_required
@role_required(['1', '2'])  # HOD and Staff
@require_http_methods(["GET"])
def api_staff(request):
    """Get staff list with pagination and filtering"""
    try:
        page = int(request.GET.get('page', 1))
        per_page = int(request.GET.get('per_page', 20))
        search = request.GET.get('search', '')
        department_id = request.GET.get('department_id')
        designation = request.GET.get('designation')
        
        staff = Staff.objects.select_related('admin', 'department').all()
        
        # Apply filters
        if search:
            staff = staff.filter(
                Q(admin__first_name__icontains=search) |
                Q(admin__last_name__icontains=search) |
                Q(employee_id__icontains=search) |
                Q(admin__email__icontains=search)
            )
        
        if department_id:
            staff = staff.filter(department_id=department_id)
        
        if designation:
            staff = staff.filter(designation=designation)
        
        # Pagination
        paginator = Paginator(staff, per_page)
        page_obj = paginator.get_page(page)
        
        staff_data = []
        for member in page_obj:
            staff_data.append({
                'id': member.id,
                'employee_id': member.employee_id,
                'first_name': member.admin.first_name,
                'last_name': member.admin.last_name,
                'email': member.admin.email,
                'designation': member.designation,
                'department': member.department.name if member.department else None,
                'qualification': member.qualification,
                'experience_years': member.experience_years,
                'profile_pic': member.admin.profile_pic.url if member.admin.profile_pic else None,
                'created_at': member.admin.created_at.isoformat() if hasattr(member.admin, 'created_at') else None
            })
        
        return JsonResponse({
            'success': True,
            'staff': staff_data,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total_pages': paginator.num_pages,
                'total_count': paginator.count,
                'has_next': page_obj.has_next(),
                'has_previous': page_obj.has_previous()
            }
        })
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@jwt_required
@role_required(['1', '2'])  # HOD and Staff
@require_http_methods(["GET"])
def api_courses(request):
    """Get courses list"""
    try:
        courses = Course.objects.select_related('department').all()
        
        courses_data = []
        for course in courses:
            courses_data.append({
                'id': course.id,
                'name': course.name,
                'code': course.code,
                'duration_years': course.duration_years,
                'department': course.department.name if course.department else None,
                'created_at': course.created_at.isoformat() if hasattr(course, 'created_at') else None
            })
        
        return JsonResponse({'success': True, 'courses': courses_data})
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@jwt_required
@role_required(['1', '2'])  # HOD and Staff
@require_http_methods(["GET"])
def api_attendance(request):
    """Get attendance data with filtering"""
    try:
        student_id = request.GET.get('student_id')
        subject_id = request.GET.get('subject_id')
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        page = int(request.GET.get('page', 1))
        per_page = int(request.GET.get('per_page', 20))
        
        attendance = AttendanceReport.objects.select_related(
            'student', 'attendance__subject'
        ).all()
        
        # Apply filters
        if student_id:
            attendance = attendance.filter(student_id=student_id)
        
        if subject_id:
            attendance = attendance.filter(attendance__subject_id=subject_id)
        
        if start_date:
            attendance = attendance.filter(attendance__date__gte=start_date)
        
        if end_date:
            attendance = attendance.filter(attendance__date__lte=end_date)
        
        # Pagination
        paginator = Paginator(attendance, per_page)
        page_obj = paginator.get_page(page)
        
        attendance_data = []
        for record in page_obj:
            attendance_data.append({
                'id': record.id,
                'student': {
                    'id': record.student.id,
                    'name': f"{record.student.admin.first_name} {record.student.admin.last_name}",
                    'roll_number': record.student.roll_number
                },
                'subject': {
                    'id': record.attendance.subject.id,
                    'name': record.attendance.subject.name
                },
                'date': record.attendance.date.isoformat(),
                'status': record.status,
                'created_at': record.created_at.isoformat() if hasattr(record, 'created_at') else None
            })
        
        return JsonResponse({
            'success': True,
            'attendance': attendance_data,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total_pages': paginator.num_pages,
                'total_count': paginator.count,
                'has_next': page_obj.has_next(),
                'has_previous': page_obj.has_previous()
            }
        })
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@jwt_required
@role_required(['1', '2'])  # HOD and Staff
@require_http_methods(["GET"])
def api_analytics(request):
    """Get analytics data"""
    try:
        # Basic statistics
        total_students = Student.objects.count()
        total_staff = Staff.objects.count()
        total_courses = Course.objects.count()
        total_subjects = Subject.objects.count()
        
        # Attendance statistics
        total_attendance = AttendanceReport.objects.count()
        present_count = AttendanceReport.objects.filter(status=True).count()
        attendance_percentage = (present_count / total_attendance * 100) if total_attendance > 0 else 0
        
        # Academic performance
        results = StudentResult.objects.all()
        avg_marks = results.aggregate(avg=Avg('exam'))['avg'] or 0
        pass_count = results.filter(exam__gte=40).count()
        pass_percentage = (pass_count / results.count() * 100) if results.count() > 0 else 0
        
        # Recent activity
        recent_students = Student.objects.select_related('admin').order_by('-admin__created_at')[:5]
        recent_staff = Staff.objects.select_related('admin').order_by('-admin__created_at')[:5]
        
        analytics_data = {
            'overview': {
                'total_students': total_students,
                'total_staff': total_staff,
                'total_courses': total_courses,
                'total_subjects': total_subjects
            },
            'attendance': {
                'total_classes': total_attendance,
                'present_classes': present_count,
                'percentage': round(attendance_percentage, 2)
            },
            'academic': {
                'average_marks': round(avg_marks, 2),
                'pass_percentage': round(pass_percentage, 2),
                'total_results': results.count()
            },
            'recent_activity': {
                'students': [
                    {
                        'id': student.id,
                        'name': f"{student.admin.first_name} {student.admin.last_name}",
                        'roll_number': student.roll_number,
                        'created_at': student.admin.created_at.isoformat() if hasattr(student.admin, 'created_at') else None
                    } for student in recent_students
                ],
                'staff': [
                    {
                        'id': staff.id,
                        'name': f"{staff.admin.first_name} {staff.admin.last_name}",
                        'employee_id': staff.employee_id,
                        'designation': staff.designation,
                        'created_at': staff.admin.created_at.isoformat() if hasattr(staff.admin, 'created_at') else None
                    } for staff in recent_staff
                ]
            }
        }
        
        return JsonResponse({'success': True, 'analytics': analytics_data})
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@jwt_required
@role_required(['1', '2'])  # HOD and Staff
@require_http_methods(["POST"])
def api_mark_attendance(request):
    """Mark attendance for students"""
    try:
        data = json.loads(request.body)
        student_ids = data.get('student_ids', [])
        subject_id = data.get('subject_id')
        date = data.get('date')
        status = data.get('status', True)
        
        if not student_ids or not subject_id or not date:
            return JsonResponse({'error': 'Missing required fields'}, status=400)
        
        subject = get_object_or_404(Subject, id=subject_id)
        attendance_date = datetime.strptime(date, '%Y-%m-%d').date()
        
        # Create or get attendance record
        attendance, created = Attendance.objects.get_or_create(
            subject=subject,
            date=attendance_date,
            defaults={'created_at': timezone.now()}
        )
        
        # Mark attendance for each student
        marked_count = 0
        for student_id in student_ids:
            student = get_object_or_404(Student, id=student_id)
            attendance_report, created = AttendanceReport.objects.get_or_create(
                student=student,
                attendance=attendance,
                defaults={'status': status}
            )
            if not created:
                attendance_report.status = status
                attendance_report.save()
            marked_count += 1
        
        return JsonResponse({
            'success': True,
            'message': f'Attendance marked for {marked_count} students',
            'marked_count': marked_count
        })
    
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@jwt_required
@role_required(['1', '2'])  # HOD and Staff
@require_http_methods(["POST"])
def api_add_result(request):
    """Add student result"""
    try:
        data = json.loads(request.body)
        student_id = data.get('student_id')
        subject_id = data.get('subject_id')
        test_marks = data.get('test_marks', 0)
        exam_marks = data.get('exam_marks', 0)
        
        if not student_id or not subject_id:
            return JsonResponse({'error': 'Student ID and Subject ID required'}, status=400)
        
        student = get_object_or_404(Student, id=student_id)
        subject = get_object_or_404(Subject, id=subject_id)
        
        result, created = StudentResult.objects.get_or_create(
            student=student,
            subject=subject,
            defaults={
                'test': test_marks,
                'exam': exam_marks
            }
        )
        
        if not created:
            result.test = test_marks
            result.exam = exam_marks
            result.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Result added successfully',
            'result': {
                'id': result.id,
                'student': f"{student.admin.first_name} {student.admin.last_name}",
                'subject': subject.name,
                'test_marks': result.test,
                'exam_marks': result.exam,
                'total': result.test + result.exam
            }
        })
    
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@jwt_required
@require_http_methods(["GET"])
def api_dashboard_data(request):
    """Get dashboard data based on user role"""
    try:
        user = request.user
        dashboard_data = {}
        
        if user.user_type == '1':  # HOD
            dashboard_data = {
                'role': 'HOD',
                'total_students': Student.objects.count(),
                'total_staff': Staff.objects.count(),
                'total_courses': Course.objects.count(),
                'total_subjects': Subject.objects.count(),
                'recent_activities': get_recent_activities()
            }
        
        elif user.user_type == '2':  # Staff
            try:
                staff = Staff.objects.get(admin=user)
                dashboard_data = {
                    'role': 'Staff',
                    'employee_id': staff.employee_id,
                    'designation': staff.designation,
                    'department': staff.department.name if staff.department else None,
                    'assigned_subjects': list(Subject.objects.filter(staff=staff).values('id', 'name')),
                    'recent_activities': get_recent_activities()
                }
            except Staff.DoesNotExist:
                dashboard_data = {'role': 'Staff', 'error': 'Staff profile not found'}
        
        elif user.user_type == '3':  # Student
            try:
                student = Student.objects.get(admin=user)
                # Get attendance data
                attendance_reports = AttendanceReport.objects.filter(student=student)
                total_attendance = attendance_reports.count()
                present_count = attendance_reports.filter(status=True).count()
                attendance_percentage = (present_count / total_attendance * 100) if total_attendance > 0 else 0
                
                # Get academic results
                results = StudentResult.objects.filter(student=student)
                avg_marks = results.aggregate(avg=Avg('exam'))['avg'] or 0
                
                dashboard_data = {
                    'role': 'Student',
                    'roll_number': student.roll_number,
                    'course': student.course.name if student.course else None,
                    'session': f"{student.session.session_start_year}-{student.session.session_end_year}" if student.session else None,
                    'attendance_percentage': round(attendance_percentage, 2),
                    'average_marks': round(avg_marks, 2),
                    'recent_activities': get_recent_activities()
                }
            except Student.DoesNotExist:
                dashboard_data = {'role': 'Student', 'error': 'Student profile not found'}
        
        return JsonResponse({'success': True, 'dashboard': dashboard_data})
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def get_recent_activities():
    """Get recent activities for dashboard"""
    activities = []
    
    # Recent students
    recent_students = Student.objects.select_related('admin').order_by('-admin__created_at')[:3]
    for student in recent_students:
        activities.append({
            'type': 'student',
            'message': f"New student {student.admin.first_name} {student.admin.last_name} enrolled",
            'time': student.admin.created_at.isoformat() if hasattr(student.admin, 'created_at') else None
        })
    
    # Recent staff
    recent_staff = Staff.objects.select_related('admin').order_by('-admin__created_at')[:3]
    for staff in recent_staff:
        activities.append({
            'type': 'staff',
            'message': f"New staff {staff.admin.first_name} {staff.admin.last_name} joined",
            'time': staff.admin.created_at.isoformat() if hasattr(staff.admin, 'created_at') else None
        })
    
    return sorted(activities, key=lambda x: x['time'], reverse=True)[:5]


@jwt_required
@require_http_methods(["GET"])
def api_search(request):
    """Global search across the system"""
    try:
        query = request.GET.get('q', '')
        if not query:
            return JsonResponse({'error': 'Search query required'}, status=400)
        
        results = {
            'students': [],
            'staff': [],
            'courses': [],
            'subjects': []
        }
        
        # Search students
        students = Student.objects.filter(
            Q(admin__first_name__icontains=query) |
            Q(admin__last_name__icontains=query) |
            Q(roll_number__icontains=query) |
            Q(admin__email__icontains=query)
        )[:5]
        
        for student in students:
            results['students'].append({
                'id': student.id,
                'name': f"{student.admin.first_name} {student.admin.last_name}",
                'roll_number': student.roll_number,
                'email': student.admin.email
            })
        
        # Search staff
        staff = Staff.objects.filter(
            Q(admin__first_name__icontains=query) |
            Q(admin__last_name__icontains=query) |
            Q(employee_id__icontains=query) |
            Q(admin__email__icontains=query)
        )[:5]
        
        for member in staff:
            results['staff'].append({
                'id': member.id,
                'name': f"{member.admin.first_name} {member.admin.last_name}",
                'employee_id': member.employee_id,
                'designation': member.designation,
                'email': member.admin.email
            })
        
        # Search courses
        courses = Course.objects.filter(
            Q(name__icontains=query) |
            Q(code__icontains=query)
        )[:5]
        
        for course in courses:
            results['courses'].append({
                'id': course.id,
                'name': course.name,
                'code': course.code,
                'department': course.department.name if course.department else None
            })
        
        # Search subjects
        subjects = Subject.objects.filter(
            Q(name__icontains=query) |
            Q(code__icontains=query)
        )[:5]
        
        for subject in subjects:
            results['subjects'].append({
                'id': subject.id,
                'name': subject.name,
                'code': subject.code,
                'course': subject.course.name if subject.course else None
            })
        
        return JsonResponse({'success': True, 'results': results})
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@require_http_methods(["GET"])
def test_api(request):
    """Test API endpoint"""
    return JsonResponse({
        'success': True,
        'message': 'API is working',
        'timestamp': timezone.now().isoformat()
    })


