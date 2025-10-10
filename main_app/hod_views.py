import json
import requests
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse, JsonResponse
from django.shortcuts import (HttpResponse, HttpResponseRedirect,
                              get_object_or_404, redirect, render)
from django.templatetags.static import static
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import UpdateView

from .forms import (AdminForm, StaffForm, StudentForm, CourseForm, SubjectForm, SessionForm,
                    EditResultForm, StudentEditForm, StaffEditForm, ManagementForm,
                    DepartmentForm, ProgramForm, ExamForm, ExamScheduleForm, TimetableForm,
                    CompanyForm, PlacementDriveForm, PlacementApplicationForm, FeeStructureForm,
                    FeePaymentForm, ScholarshipForm, ScholarshipApplicationForm, HostelForm,
                    HostelAllocationForm, TransportForm, TransportAllocationForm, LibraryBookForm,
                    LibraryIssueForm, GrievanceForm, SemesterResultForm, SubjectResultForm,
                    OnlineExamForm, OnlineExamQuestionForm, CertificateForm, AlumniForm,
                    InternshipForm, MedicalRecordForm, GatePassForm, DisciplinaryActionForm,
                    SportsActivityForm, ActivityParticipationForm, ResearchForm,
                    AntiRaggingForm, StudentCouncilForm, ParentGuardianForm,
                    ClassroomForm, ClassroomBookingForm, ClassroomMaintenanceForm)
from .models import (CustomUser, Admin, Staff, Student, Course, Subject, Session, 
                      Attendance, AttendanceReport, LeaveReportStaff, LeaveReportStudent,
                      FeedbackStaff, FeedbackStudent, NotificationStaff, NotificationStudent,
                      StudentResult, Event, EventParticipation, Message, StudyMaterial, 
                      ResourceRating, ResourceBookmark, ResourceDownloadLog, Assignment, 
                      AssignmentSubmission, Announcement, Discussion, DiscussionReply,
                      ProctorAssignment, Department, Program, Hostel, HostelAllocation, 
                      HostelVisitorLog, Transport, TransportAllocation, FeeStructure, 
                      FeePayment, Scholarship, ScholarshipApplication, SemesterResult, 
                      SubjectResult, Library, LibraryIssue, Exam, ExamSchedule, Invigilator, 
                      AdmitCard, Timetable, Company, PlacementDrive, PlacementApplication, 
                      Grievance, ActivityLog, Management,
                      OnlineExam, OnlineExamQuestion, OnlineExamAttempt, Certificate, Alumni, 
                      Internship, MedicalRecord, GatePass, DisciplinaryAction, SportsActivity, 
                      ActivityParticipation, Research, AntiRaggingCommittee, StudentCouncil, 
                      ParentGuardian, Classroom, ClassroomBooking, ClassroomMaintenance)


# Helper function to get staff object for current user
def get_staff_for_user(request):
    """Get Staff object for current user, handling both HOD and Staff user types"""
    if hasattr(request.user, 'staff'):
        return request.user.staff
    else:
        # For HOD/Admin users, return the first staff member or None
        # In production, you might want to create a default staff profile for HOD
        return Staff.objects.first()


def admin_home(request):
    total_staff = Staff.objects.all().count()
    total_students = Student.objects.all().count()
    subjects = Subject.objects.all()
    total_subject = subjects.count()
    total_course = Course.objects.all().count()
    attendance_list = Attendance.objects.filter(subject__in=subjects)
    total_attendance = attendance_list.count()
    attendance_list = []
    subject_list = []
    for subject in subjects:
        attendance_count = Attendance.objects.filter(subject=subject).count()
        subject_list.append(subject.name[:7])
        attendance_list.append(attendance_count)
    context = {
        'page_title': "Administrative Dashboard",
        'total_students': total_students,
        'total_staff': total_staff,
        'total_course': total_course,
        'total_subject': total_subject,
        'subject_list': subject_list,
        'attendance_list': attendance_list

    }
    return render(request, 'hod_template/home_content.html', context)


def add_staff(request):
    form = StaffForm(request.POST or None, request.FILES or None)
    context = {'form': form, 'page_title': 'Add Staff'}
    if request.method == 'POST':
        if form.is_valid():
            first_name = form.cleaned_data.get('first_name')
            last_name = form.cleaned_data.get('last_name')
            address = form.cleaned_data.get('address')
            email = form.cleaned_data.get('email')
            gender = form.cleaned_data.get('gender')
            password = form.cleaned_data.get('password')
            course = form.cleaned_data.get('course')
            
            try:
                user = CustomUser.objects.create_user(
                    email=email, password=password, user_type=2, first_name=first_name, last_name=last_name)
                user.gender = gender
                user.address = address
                user.staff.course = course
                user.save()
                messages.success(request, "Successfully Added")
                return redirect(reverse('add_staff'))

            except Exception as e:
                messages.error(request, "Could Not Add " + str(e))
        else:
            messages.error(request, "Please fulfil all requirements")

    return render(request, 'hod_template/add_staff_template.html', context)


def add_student(request):
    student_form = StudentForm(request.POST or None, request.FILES or None)
    context = {'form': student_form, 'page_title': 'Add Student'}
    if request.method == 'POST':
        if student_form.is_valid():
            first_name = student_form.cleaned_data.get('first_name')
            last_name = student_form.cleaned_data.get('last_name')
            address = student_form.cleaned_data.get('address')
            email = student_form.cleaned_data.get('email')
            gender = student_form.cleaned_data.get('gender')
            password = student_form.cleaned_data.get('password')
            course = student_form.cleaned_data.get('course')
            session = student_form.cleaned_data.get('session')
           
            try:
                user = CustomUser.objects.create_user(
                    email=email, password=password, user_type=3, first_name=first_name, last_name=last_name)
                user.gender = gender
                user.address = address
                user.student.session = session
                user.student.course = course
                user.save()
                messages.success(request, "Successfully Added")
                return redirect(reverse('add_student'))
            except Exception as e:
                messages.error(request, "Could Not Add: " + str(e))
        else:
            messages.error(request, "Could Not Add: ")
    return render(request, 'hod_template/add_student_template.html', context)


def add_course(request):
    form = CourseForm(request.POST or None)
    context = {
        'form': form,
        'page_title': 'Add Course'
    }
    if request.method == 'POST':
        if form.is_valid():
            name = form.cleaned_data.get('name')
            try:
                course = Course()
                course.name = name
                course.save()
                messages.success(request, "Successfully Added")
                return redirect(reverse('add_course'))
            except:
                messages.error(request, "Could Not Add")
        else:
            messages.error(request, "Could Not Add")
    return render(request, 'hod_template/add_course_template.html', context)


def add_subject(request):
    form = SubjectForm(request.POST or None)
    context = {
        'form': form,
        'page_title': 'Add Subject'
    }
    if request.method == 'POST':
        if form.is_valid():
            name = form.cleaned_data.get('name')
            course = form.cleaned_data.get('course')
            staff = form.cleaned_data.get('staff')
            try:
                subject = Subject()
                subject.name = name
                subject.staff = staff
                subject.course = course
                subject.save()
                messages.success(request, "Successfully Added")
                return redirect(reverse('add_subject'))

            except Exception as e:
                messages.error(request, "Could Not Add " + str(e))
        else:
            messages.error(request, "Fill Form Properly")

    return render(request, 'hod_template/add_subject_template.html', context)


def manage_staff(request):
    allStaff = CustomUser.objects.filter(user_type=2)
    context = {
        'allStaff': allStaff,
        'page_title': 'Manage Staff'
    }
    return render(request, "hod_template/manage_staff.html", context)


def manage_student(request):
    students = CustomUser.objects.filter(user_type=3)
    context = {
        'students': students,
        'page_title': 'Manage Students'
    }
    return render(request, "hod_template/manage_student.html", context)


def manage_course(request):
    courses = Course.objects.all()
    context = {
        'courses': courses,
        'page_title': 'Manage Courses'
    }
    return render(request, "hod_template/manage_course.html", context)


def manage_subject(request):
    subjects = Subject.objects.all()
    context = {
        'subjects': subjects,
        'page_title': 'Manage Subjects'
    }
    return render(request, "hod_template/manage_subject.html", context)


def edit_staff(request, staff_id):
    staff = get_object_or_404(Staff, id=staff_id)
    form = StaffForm(request.POST or None, instance=staff)
    context = {
        'form': form,
        'staff_id': staff_id,
        'page_title': 'Edit Staff'
    }
    if request.method == 'POST':
        if form.is_valid():
            first_name = form.cleaned_data.get('first_name')
            last_name = form.cleaned_data.get('last_name')
            address = form.cleaned_data.get('address')
            username = form.cleaned_data.get('username')
            email = form.cleaned_data.get('email')
            gender = form.cleaned_data.get('gender')
            password = form.cleaned_data.get('password') or None
            course = form.cleaned_data.get('course')
            passport = request.FILES.get('profile_pic') or None
            try:
                user = CustomUser.objects.get(id=staff.admin.id)
                user.username = username
                user.email = email
                if password != None:
                    user.set_password(password)
                if passport != None:
                    fs = FileSystemStorage()
                    filename = fs.save(passport.name, passport)
                    passport_url = fs.url(filename)
                    user.profile_pic = passport_url
                user.first_name = first_name
                user.last_name = last_name
                user.gender = gender
                user.address = address
                staff.course = course
                user.save()
                staff.save()
                messages.success(request, "Successfully Updated")
                return redirect(reverse('edit_staff', args=[staff_id]))
            except Exception as e:
                messages.error(request, "Could Not Update " + str(e))
        else:
            messages.error(request, "Please fil form properly")
    else:
        user = CustomUser.objects.get(id=staff_id)
        staff = Staff.objects.get(id=user.id)
        return render(request, "hod_template/edit_staff_template.html", context)


def edit_student(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    form = StudentForm(request.POST or None, instance=student)
    context = {
        'form': form,
        'student_id': student_id,
        'page_title': 'Edit Student'
    }
    if request.method == 'POST':
        if form.is_valid():
            first_name = form.cleaned_data.get('first_name')
            last_name = form.cleaned_data.get('last_name')
            address = form.cleaned_data.get('address')
            username = form.cleaned_data.get('username')
            email = form.cleaned_data.get('email')
            gender = form.cleaned_data.get('gender')
            password = form.cleaned_data.get('password') or None
            course = form.cleaned_data.get('course')
            session = form.cleaned_data.get('session')
            passport = request.FILES.get('profile_pic') or None
            try:
                user = CustomUser.objects.get(id=student.admin.id)
                if passport != None:
                    fs = FileSystemStorage()
                    filename = fs.save(passport.name, passport)
                    passport_url = fs.url(filename)
                    user.profile_pic = passport_url
                user.username = username
                user.email = email
                if password != None:
                    user.set_password(password)
                user.first_name = first_name
                user.last_name = last_name
                student.session = session
                user.gender = gender
                user.address = address
                student.course = course
                user.save()
                student.save()
                messages.success(request, "Successfully Updated")
                return redirect(reverse('edit_student', args=[student_id]))
            except Exception as e:
                messages.error(request, "Could Not Update " + str(e))
        else:
            messages.error(request, "Please Fill Form Properly!")
    else:
        return render(request, "hod_template/edit_student_template.html", context)


def edit_course(request, course_id):
    instance = get_object_or_404(Course, id=course_id)
    form = CourseForm(request.POST or None, instance=instance)
    context = {
        'form': form,
        'course_id': course_id,
        'page_title': 'Edit Course'
    }
    if request.method == 'POST':
        if form.is_valid():
            name = form.cleaned_data.get('name')
            try:
                course = Course.objects.get(id=course_id)
                course.name = name
                course.save()
                messages.success(request, "Successfully Updated")
            except:
                messages.error(request, "Could Not Update")
        else:
            messages.error(request, "Could Not Update")

    return render(request, 'hod_template/edit_course_template.html', context)


def edit_subject(request, subject_id):
    instance = get_object_or_404(Subject, id=subject_id)
    form = SubjectForm(request.POST or None, instance=instance)
    context = {
        'form': form,
        'subject_id': subject_id,
        'page_title': 'Edit Subject'
    }
    if request.method == 'POST':
        if form.is_valid():
            name = form.cleaned_data.get('name')
            course = form.cleaned_data.get('course')
            staff = form.cleaned_data.get('staff')
            try:
                subject = Subject.objects.get(id=subject_id)
                subject.name = name
                subject.staff = staff
                subject.course = course
                subject.save()
                messages.success(request, "Successfully Updated")
                return redirect(reverse('edit_subject', args=[subject_id]))
            except Exception as e:
                messages.error(request, "Could Not Add " + str(e))
        else:
            messages.error(request, "Fill Form Properly")
    return render(request, 'hod_template/edit_subject_template.html', context)


def add_session(request):
    form = SessionForm(request.POST or None)
    context = {'form': form, 'page_title': 'Add Session'}
    if request.method == 'POST':
        if form.is_valid():
            try:
                form.save()
                messages.success(request, "Session Created")
                return redirect(reverse('add_session'))
            except Exception as e:
                messages.error(request, 'Could Not Add ' + str(e))
        else:
            messages.error(request, 'Fill Form Properly ')
    return render(request, "hod_template/add_session_template.html", context)


def manage_session(request):
    sessions = Session.objects.all()
    context = {'sessions': sessions, 'page_title': 'Manage Sessions'}
    return render(request, "hod_template/manage_session.html", context)


def edit_session(request, session_id):
    instance = get_object_or_404(Session, id=session_id)
    form = SessionForm(request.POST or None, instance=instance)
    context = {'form': form, 'session_id': session_id,
               'page_title': 'Edit Session'}
    if request.method == 'POST':
        if form.is_valid():
            try:
                form.save()
                messages.success(request, "Session Updated")
                return redirect(reverse('edit_session', args=[session_id]))
            except Exception as e:
                messages.error(
                    request, "Session Could Not Be Updated " + str(e))
                return render(request, "hod_template/edit_session_template.html", context)
        else:
            messages.error(request, "Invalid Form Submitted ")
            return render(request, "hod_template/edit_session_template.html", context)

    else:
        return render(request, "hod_template/edit_session_template.html", context)


@csrf_exempt
def check_email_availability(request):
    email = request.POST.get("email")
    try:
        user = CustomUser.objects.filter(email=email).exists()
        if user:
            return HttpResponse(True)
        return HttpResponse(False)
    except Exception as e:
        return HttpResponse(False)


@csrf_exempt
def student_feedback_message(request):
    if request.method != 'POST':
        feedbacks = FeedbackStudent.objects.all()
        context = {
            'feedbacks': feedbacks,
            'page_title': 'Student Feedback Messages'
        }
        return render(request, 'hod_template/student_feedback_template.html', context)
    else:
        feedback_id = request.POST.get('id')
        try:
            feedback = get_object_or_404(FeedbackStudent, id=feedback_id)
            reply = request.POST.get('reply')
            feedback.reply = reply
            feedback.save()
            return HttpResponse(True)
        except Exception as e:
            return HttpResponse(False)


@csrf_exempt
def staff_feedback_message(request):
    if request.method != 'POST':
        feedbacks = FeedbackStaff.objects.all()
        context = {
            'feedbacks': feedbacks,
            'page_title': 'Staff Feedback Messages'
        }
        return render(request, 'hod_template/staff_feedback_template.html', context)
    else:
        feedback_id = request.POST.get('id')
        try:
            feedback = get_object_or_404(FeedbackStaff, id=feedback_id)
            reply = request.POST.get('reply')
            feedback.reply = reply
            feedback.save()
            return HttpResponse(True)
        except Exception as e:
            return HttpResponse(False)


@csrf_exempt
def view_staff_leave(request):
    if request.method != 'POST':
        allLeave = LeaveReportStaff.objects.all()
        context = {
            'allLeave': allLeave,
            'page_title': 'Leave Applications From Staff'
        }
        return render(request, "hod_template/staff_leave_view.html", context)
    else:
        id = request.POST.get('id')
        status = request.POST.get('status')
        if (status == '1'):
            status = 1
        else:
            status = -1
        try:
            leave = get_object_or_404(LeaveReportStaff, id=id)
            leave.status = status
            leave.save()
            return HttpResponse(True)
        except Exception as e:
            return False


@csrf_exempt
def view_student_leave(request):
    if request.method != 'POST':
        allLeave = LeaveReportStudent.objects.all()
        context = {
            'allLeave': allLeave,
            'page_title': 'Leave Applications From Students'
        }
        return render(request, "hod_template/student_leave_view.html", context)
    else:
        id = request.POST.get('id')
        status = request.POST.get('status')
        if (status == '1'):
            status = 1
        else:
            status = -1
        try:
            leave = get_object_or_404(LeaveReportStudent, id=id)
            leave.status = status
            leave.save()
            return HttpResponse(True)
        except Exception as e:
            return False


def admin_view_attendance(request):
    subjects = Subject.objects.all()
    sessions = Session.objects.all()
    context = {
        'subjects': subjects,
        'sessions': sessions,
        'page_title': 'View Attendance'
    }

    return render(request, "hod_template/admin_view_attendance.html", context)


@csrf_exempt
def get_admin_attendance(request):
    subject_id = request.POST.get('subject')
    session_id = request.POST.get('session')
    attendance_date_id = request.POST.get('attendance_date_id')
    try:
        subject = get_object_or_404(Subject, id=subject_id)
        session = get_object_or_404(Session, id=session_id)
        attendance = get_object_or_404(
            Attendance, id=attendance_date_id, session=session)
        attendance_reports = AttendanceReport.objects.filter(
            attendance=attendance)
        json_data = []
        for report in attendance_reports:
            data = {
                "status":  str(report.status),
                "name": str(report.student)
            }
            json_data.append(data)
        return JsonResponse(json.dumps(json_data), safe=False)
    except Exception as e:
        return None


def admin_view_profile(request):
    admin = get_object_or_404(Admin, admin=request.user)
    form = AdminForm(request.POST or None, request.FILES or None,
                     instance=admin)
    context = {'form': form,
               'page_title': 'View/Edit Profile'
               }
    if request.method == 'POST':
        try:
            if form.is_valid():
                first_name = form.cleaned_data.get('first_name')
                last_name = form.cleaned_data.get('last_name')
                password = form.cleaned_data.get('password') or None
                passport = request.FILES.get('profile_pic') or None
                custom_user = admin.admin
                if password != None:
                    custom_user.set_password(password)
                if passport != None:
                    fs = FileSystemStorage()
                    filename = fs.save(passport.name, passport)
                    passport_url = fs.url(filename)
                    custom_user.profile_pic = passport_url
                custom_user.first_name = first_name
                custom_user.last_name = last_name
                custom_user.save()
                messages.success(request, "Profile Updated!")
                return redirect(reverse('admin_view_profile'))
            else:
                messages.error(request, "Invalid Data Provided")
        except Exception as e:
            messages.error(
                request, "Error Occured While Updating Profile " + str(e))
    return render(request, "hod_template/admin_view_profile.html", context)


def admin_notify_staff(request):
    staff = CustomUser.objects.filter(user_type=2)
    context = {
        'page_title': "Send Notifications To Staff",
        'allStaff': staff
    }
    return render(request, "hod_template/staff_notification.html", context)


def admin_notify_student(request):
    student = CustomUser.objects.filter(user_type=3)
    context = {
        'page_title': "Send Notifications To Students",
        'students': student
    }
    return render(request, "hod_template/student_notification.html", context)


@csrf_exempt
def send_student_notification(request):
    id = request.POST.get('id')
    message = request.POST.get('message')
    student = get_object_or_404(Student, admin_id=id)
    try:
        url = "https://fcm.googleapis.com/fcm/send"
        body = {
            'notification': {
                'title': "EduVision",
                'body': message,
                'click_action': reverse('student_view_notification'),
                'icon': static('dist/img/AdminLTELogo.png')
            },
            'to': student.admin.fcm_token
        }
        headers = {'Authorization':
                   'key=AAAA3Bm8j_M:APA91bElZlOLetwV696SoEtgzpJr2qbxBfxVBfDWFiopBWzfCfzQp2nRyC7_A2mlukZEHV4g1AmyC6P_HonvSkY2YyliKt5tT3fe_1lrKod2Daigzhb2xnYQMxUWjCAIQcUexAMPZePB',
                   'Content-Type': 'application/json'}
        data = requests.post(url, data=json.dumps(body), headers=headers)
        notification = NotificationStudent(student=student, message=message)
        notification.save()
        return HttpResponse("True")
    except Exception as e:
        return HttpResponse("False")


@csrf_exempt
def send_staff_notification(request):
    id = request.POST.get('id')
    message = request.POST.get('message')
    staff = get_object_or_404(Staff, admin_id=id)
    try:
        url = "https://fcm.googleapis.com/fcm/send"
        body = {
            'notification': {
                'title': "EduVision",
                'body': message,
                'click_action': reverse('staff_view_notification'),
                'icon': static('dist/img/AdminLTELogo.png')
            },
            'to': staff.admin.fcm_token
        }
        headers = {'Authorization':
                   'key=AAAA3Bm8j_M:APA91bElZlOLetwV696SoEtgzpJr2qbxBfxVBfDWFiopBWzfCfzQp2nRyC7_A2mlukZEHV4g1AmyC6P_HonvSkY2YyliKt5tT3fe_1lrKod2Daigzhb2xnYQMxUWjCAIQcUexAMPZePB',
                   'Content-Type': 'application/json'}
        data = requests.post(url, data=json.dumps(body), headers=headers)
        notification = NotificationStaff(staff=staff, message=message)
        notification.save()
        return HttpResponse("True")
    except Exception as e:
        return HttpResponse("False")


def delete_staff(request, staff_id):
    staff = get_object_or_404(CustomUser, staff__id=staff_id)
    staff.delete()
    messages.success(request, "Staff deleted successfully!")
    return redirect(reverse('manage_staff'))


def delete_student(request, student_id):
    student = get_object_or_404(CustomUser, student__id=student_id)
    student.delete()
    messages.success(request, "Student deleted successfully!")
    return redirect(reverse('manage_student'))


def delete_course(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    try:
        course.delete()
        messages.success(request, "Course deleted successfully!")
    except Exception:
        messages.error(
            request, "Sorry, some students are assigned to this course already. Kindly change the affected student course and try again")
    return redirect(reverse('manage_course'))


def delete_subject(request, subject_id):
    subject = get_object_or_404(Subject, id=subject_id)
    subject.delete()
    messages.success(request, "Subject deleted successfully!")
    return redirect(reverse('manage_subject'))


def delete_session(request, session_id):
    session = get_object_or_404(Session, id=session_id)
    try:
        session.delete()
        messages.success(request, "Session deleted successfully!")
    except Exception:
        messages.error(
            request, "There are students assigned to this session. Please move them to another session.")
    return redirect(reverse('manage_session'))


def manage_proctors(request):
    """View and manage proctor assignments"""
    # Get all staff who are proctors
    proctors = Staff.objects.filter(is_proctor=True).select_related('admin', 'course')
    
    # Get all assignments
    assignments = ProctorAssignment.objects.filter(
        is_active=True
    ).select_related('staff', 'staff__admin', 'student', 'student__admin').order_by('staff')
    
    context = {
        'page_title': 'Manage Proctors',
        'proctors': proctors,
        'assignments': assignments,
    }
    
    return render(request, 'hod_template/manage_proctors.html', context)


def assign_proctor_to_student(request):
    """Assign a staff (proctor) to students"""
    if request.method == 'POST':
        staff_id = request.POST.get('staff_id')
        student_ids = request.POST.getlist('student_ids')
        
        try:
            staff = Staff.objects.get(id=staff_id)
            
            # Ensure staff is marked as proctor
            if not staff.is_proctor:
                staff.is_proctor = True
                staff.save()
            
            # Create assignments
            count = 0
            for student_id in student_ids:
                student = Student.objects.get(id=student_id)
                obj, created = ProctorAssignment.objects.get_or_create(
                    staff=staff,
                    student=student,
                    defaults={'is_active': True}
                )
                if created:
                    count += 1
                elif not obj.is_active:
                    obj.is_active = True
                    obj.save()
                    count += 1
            
            messages.success(request, f"Successfully assigned {count} students to {staff.admin.first_name}")
            return redirect('manage_proctors')
        except Exception as e:
            messages.error(request, f"Failed to assign students: {str(e)}")
    
    # Get all staff and students
    all_staff = Staff.objects.all().select_related('admin', 'course')
    all_students = Student.objects.all().select_related('admin', 'course')
    courses = Course.objects.all()
    
    context = {
        'page_title': 'Assign Proctor to Students',
        'all_staff': all_staff,
        'all_students': all_students,
        'courses': courses,
    }
    
    return render(request, 'hod_template/assign_proctor.html', context)


@csrf_exempt
def remove_proctor_assignment(request):
    """Remove a proctor assignment"""
    if request.method == 'POST':
        assignment_id = request.POST.get('assignment_id')
        
        try:
            assignment = ProctorAssignment.objects.get(id=assignment_id)
            assignment.is_active = False
            assignment.save()
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    
    return JsonResponse({'status': 'error'})


# ==================== EXAM CELL PANEL ====================

def manage_exams(request):
    """View all exams"""
    exams = Exam.objects.all().order_by('-created_at')
    context = {
        'page_title': 'Manage Exams',
        'exams': exams
    }
    return render(request, 'hod_template/manage_exams.html', context)


def add_exam(request):
    """Create new exam"""
    form = ExamForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            exam = form.save(commit=False)
            exam.created_by = get_staff_for_user(request)
            exam.save()
            messages.success(request, "Exam created successfully!")
            return redirect('manage_exams')
        else:
            messages.error(request, "Failed to create exam. Please check the form.")
    
    context = {
        'page_title': 'Create Exam',
        'form': form
    }
    return render(request, 'hod_template/add_exam.html', context)


def manage_exam_schedule(request, exam_id):
    """Manage exam schedule for a specific exam"""
    exam = get_object_or_404(Exam, id=exam_id)
    schedules = ExamSchedule.objects.filter(exam=exam).order_by('exam_date', 'start_time')
    
    context = {
        'page_title': f'Exam Schedule - {exam.name}',
        'exam': exam,
        'schedules': schedules
    }
    return render(request, 'hod_template/manage_exam_schedule.html', context)


def add_exam_schedule(request, exam_id):
    """Add schedule for an exam"""
    exam = get_object_or_404(Exam, id=exam_id)
    form = ExamScheduleForm(request.POST or None, request.FILES or None)
    
    if request.method == 'POST':
        if form.is_valid():
            schedule = form.save()
            messages.success(request, "Exam schedule added successfully!")
            return redirect('manage_exam_schedule', exam_id=exam.id)
        else:
            messages.error(request, "Failed to add schedule. Please check the form.")
    else:
        form.fields['exam'].initial = exam
        form.fields['exam'].widget = forms.HiddenInput()
    
    context = {
        'page_title': 'Add Exam Schedule',
        'form': form,
        'exam': exam
    }
    return render(request, 'hod_template/add_exam_schedule.html', context)


def assign_invigilators(request, schedule_id):
    """Assign invigilators to exam schedule"""
    schedule = get_object_or_404(ExamSchedule, id=schedule_id)
    staff_list = Staff.objects.filter(status='active')
    assigned = Invigilator.objects.filter(exam_schedule=schedule)
    
    if request.method == 'POST':
        staff_id = request.POST.get('staff_id')
        duty_type = request.POST.get('duty_type')
        
        staff = get_object_or_404(Staff, id=staff_id)
        
        # Check if already assigned
        if Invigilator.objects.filter(exam_schedule=schedule, staff=staff).exists():
            messages.error(request, f"{staff} is already assigned!")
        else:
            Invigilator.objects.create(
                exam_schedule=schedule,
                staff=staff,
                duty_type=duty_type
            )
            messages.success(request, f"{staff} assigned as {duty_type} successfully!")
        
        return redirect('assign_invigilators', schedule_id=schedule.id)
    
    context = {
        'page_title': 'Assign Invigilators',
        'schedule': schedule,
        'staff_list': staff_list,
        'assigned': assigned
    }
    return render(request, 'hod_template/assign_invigilators.html', context)


def generate_admit_cards(request, exam_id):
    """Generate admit cards for all students"""
    exam = get_object_or_404(Exam, id=exam_id)
    
    if request.method == 'POST':
        # Get all active students
        students = Student.objects.filter(student_status='active')
        generated_count = 0
        
        for student in students:
            # Check if admit card already exists
            if not AdmitCard.objects.filter(exam=exam, student=student).exists():
                admit_card_number = f"{exam.id}-{student.id}-{exam.session.start_year.year}"
                AdmitCard.objects.create(
                    exam=exam,
                    student=student,
                    admit_card_number=admit_card_number,
                    is_generated=True
                )
                generated_count += 1
        
        messages.success(request, f"Generated {generated_count} admit cards successfully!")
        return redirect('manage_exams')
    
    # Count how many admit cards would be generated
    students = Student.objects.filter(student_status='active')
    existing = AdmitCard.objects.filter(exam=exam).count()
    to_generate = students.count() - existing
    
    context = {
        'page_title': 'Generate Admit Cards',
        'exam': exam,
        'total_students': students.count(),
        'existing_cards': existing,
        'to_generate': to_generate
    }
    return render(request, 'hod_template/generate_admit_cards.html', context)


def manage_results(request):
    """Manage semester results"""
    results = SemesterResult.objects.all().order_by('-session', '-semester')
    
    context = {
        'page_title': 'Manage Results',
        'results': results
    }
    return render(request, 'hod_template/manage_results.html', context)


def add_semester_result(request):
    """Add semester result"""
    form = SemesterResultForm(request.POST or None)
    
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            messages.success(request, "Semester result added successfully!")
            return redirect('manage_results')
        else:
            messages.error(request, "Failed to add result. Please check the form.")
    
    context = {
        'page_title': 'Add Semester Result',
        'form': form
    }
    return render(request, 'hod_template/add_semester_result.html', context)


def publish_results(request, result_id):
    """Publish semester results"""
    result = get_object_or_404(SemesterResult, id=result_id)
    
    if request.method == 'POST':
        result.is_published = True
        from django.utils import timezone
        result.published_date = timezone.now()
        result.save()
        messages.success(request, "Result published successfully!")
        return redirect('manage_results')
    
    context = {
        'page_title': 'Publish Result',
        'result': result
    }
    return render(request, 'hod_template/publish_result.html', context)


# ==================== PLACEMENT PANEL ====================

def manage_companies(request):
    """View all companies"""
    companies = Company.objects.all().order_by('name')
    
    context = {
        'page_title': 'Manage Companies',
        'companies': companies
    }
    return render(request, 'hod_template/manage_companies.html', context)


def add_company(request):
    """Add new company"""
    form = CompanyForm(request.POST or None, request.FILES or None)
    
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            messages.success(request, "Company added successfully!")
            return redirect('manage_companies')
        else:
            messages.error(request, "Failed to add company. Please check the form.")
    
    context = {
        'page_title': 'Add Company',
        'form': form
    }
    return render(request, 'hod_template/add_company.html', context)


def edit_company(request, company_id):
    """Edit company"""
    company = get_object_or_404(Company, id=company_id)
    form = CompanyForm(request.POST or None, request.FILES or None, instance=company)
    
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            messages.success(request, "Company updated successfully!")
            return redirect('manage_companies')
        else:
            messages.error(request, "Failed to update company.")
    
    context = {
        'page_title': 'Edit Company',
        'form': form,
        'company': company
    }
    return render(request, 'hod_template/edit_company.html', context)


def manage_placement_drives(request):
    """View all placement drives"""
    drives = PlacementDrive.objects.all().order_by('-created_at')
    
    context = {
        'page_title': 'Manage Placement Drives',
        'drives': drives
    }
    return render(request, 'hod_template/manage_placement_drives.html', context)


def add_placement_drive(request):
    """Add new placement drive"""
    form = PlacementDriveForm(request.POST or None, request.FILES or None)
    
    if request.method == 'POST':
        if form.is_valid():
            drive = form.save(commit=False)
            
            # Use helper function to get staff object
            staff = get_staff_for_user(request)
            if staff:
                drive.coordinator = staff
            
            drive.save()
            form.save_m2m()  # Save many-to-many relationships
            messages.success(request, "Placement drive created successfully!")
            return redirect('manage_placement_drives')
        else:
            messages.error(request, "Failed to create drive. Please check the form.")
    
    context = {
        'page_title': 'Create Placement Drive',
        'form': form
    }
    return render(request, 'hod_template/add_placement_drive.html', context)


def view_placement_applications(request, drive_id):
    """View applications for a placement drive"""
    drive = get_object_or_404(PlacementDrive, id=drive_id)
    applications = PlacementApplication.objects.filter(placement_drive=drive).order_by('-applied_at')
    
    # Statistics
    total_apps = applications.count()
    registered = applications.filter(status='registered').count()
    shortlisted = applications.filter(status='shortlisted').count()
    selected = applications.filter(status='selected').count()
    
    context = {
        'page_title': f'Applications - {drive.company.name}',
        'drive': drive,
        'applications': applications,
        'total_apps': total_apps,
        'registered': registered,
        'shortlisted': shortlisted,
        'selected': selected
    }
    return render(request, 'hod_template/view_placement_applications.html', context)


def update_application_status(request, app_id):
    """Update placement application status"""
    application = get_object_or_404(PlacementApplication, id=app_id)
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        aptitude_score = request.POST.get('aptitude_score')
        technical_score = request.POST.get('technical_score')
        hr_score = request.POST.get('hr_score')
        remarks = request.POST.get('remarks')
        
        application.status = new_status
        if aptitude_score:
            application.aptitude_score = aptitude_score
        if technical_score:
            application.technical_score = technical_score
        if hr_score:
            application.hr_score = hr_score
        if remarks:
            application.remarks = remarks
        
        application.save()
        messages.success(request, "Application status updated successfully!")
        return redirect('view_placement_applications', drive_id=application.placement_drive.id)
    
    context = {
        'page_title': 'Update Application Status',
        'application': application
    }
    return render(request, 'hod_template/update_application_status.html', context)


# ==================== FEE MANAGEMENT PANEL ====================

def manage_fee_structure(request):
    """View all fee structures"""
    fee_structures = FeeStructure.objects.all().order_by('-session', 'course', 'semester')
    
    context = {
        'page_title': 'Manage Fee Structure',
        'fee_structures': fee_structures
    }
    return render(request, 'hod_template/manage_fee_structure.html', context)


def add_fee_structure(request):
    """Add fee structure"""
    form = FeeStructureForm(request.POST or None)
    
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            messages.success(request, "Fee structure added successfully!")
            return redirect('manage_fee_structure')
        else:
            messages.error(request, "Failed to add fee structure. Please check the form.")
    
    context = {
        'page_title': 'Add Fee Structure',
        'form': form
    }
    return render(request, 'hod_template/add_fee_structure.html', context)


def edit_fee_structure(request, structure_id):
    """Edit fee structure"""
    structure = get_object_or_404(FeeStructure, id=structure_id)
    form = FeeStructureForm(request.POST or None, instance=structure)
    
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            messages.success(request, "Fee structure updated successfully!")
            return redirect('manage_fee_structure')
        else:
            messages.error(request, "Failed to update fee structure.")
    
    context = {
        'page_title': 'Edit Fee Structure',
        'form': form,
        'structure': structure
    }
    return render(request, 'hod_template/edit_fee_structure.html', context)


def view_fee_payments(request):
    """View all fee payments"""
    payments = FeePayment.objects.all().order_by('-payment_date')
    
    # Statistics
    total_collected = sum([p.amount_paid for p in payments if p.status == 'paid'])
    pending_amount = sum([p.fee_structure.total_fee - p.amount_paid for p in payments if p.status in ['pending', 'partial']])
    
    context = {
        'page_title': 'Fee Payments',
        'payments': payments,
        'total_collected': total_collected,
        'pending_amount': pending_amount
    }
    return render(request, 'hod_template/view_fee_payments.html', context)


def record_fee_payment(request):
    """Record a fee payment"""
    form = FeePaymentForm(request.POST or None)
    
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            messages.success(request, "Fee payment recorded successfully!")
            return redirect('view_fee_payments')
        else:
            messages.error(request, "Failed to record payment. Please check the form.")
    
    context = {
        'page_title': 'Record Fee Payment',
        'form': form
    }
    return render(request, 'hod_template/record_fee_payment.html', context)


def fee_defaulters(request):
    """View fee defaulters"""
    # Get all active students
    students = Student.objects.filter(student_status='active')
    defaulters = []
    
    for student in students:
        # Get all fee payments for this student
        payments = FeePayment.objects.filter(student=student, status__in=['pending', 'partial', 'overdue'])
        if payments.exists():
            total_due = sum([p.fee_structure.total_fee - p.amount_paid for p in payments])
            defaulters.append({
                'student': student,
                'total_due': total_due,
                'pending_payments': payments
            })
    
    context = {
        'page_title': 'Fee Defaulters',
        'defaulters': defaulters
    }
    return render(request, 'hod_template/fee_defaulters.html', context)


# ==================== TRANSPORT MANAGEMENT ====================

def manage_transport(request):
    """Manage all transport routes"""
    routes = Transport.objects.all().order_by('route_name')
    
    context = {
        'page_title': 'Manage Transport',
        'routes': routes
    }
    return render(request, 'hod_template/manage_transport.html', context)


def add_transport(request):
    """Add new transport route"""
    form = TransportForm(request.POST or None)
    
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            messages.success(request, "Transport route added successfully!")
            return redirect('manage_transport')
        else:
            messages.error(request, "Failed to add route. Please check the form.")
    
    context = {
        'page_title': 'Add Transport Route',
        'form': form
    }
    return render(request, 'hod_template/add_transport.html', context)


def edit_transport(request, transport_id):
    """Edit transport route"""
    transport = get_object_or_404(Transport, id=transport_id)
    form = TransportForm(request.POST or None, instance=transport)
    
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            messages.success(request, "Transport route updated successfully!")
            return redirect('manage_transport')
        else:
            messages.error(request, "Failed to update route.")
    
    context = {
        'page_title': 'Edit Transport Route',
        'form': form,
        'transport': transport
    }
    return render(request, 'hod_template/edit_transport.html', context)


def transport_allocations(request):
    """View all transport allocations"""
    allocations = TransportAllocation.objects.filter(is_active=True).order_by('transport__route_name')
    
    context = {
        'page_title': 'Transport Allocations',
        'allocations': allocations
    }
    return render(request, 'hod_template/transport_allocations.html', context)


def allocate_transport(request):
    """Allocate transport to student"""
    form = TransportAllocationForm(request.POST or None)
    
    if request.method == 'POST':
        if form.is_valid():
            allocation = form.save()
            # Update occupied seats
            transport = allocation.transport
            transport.occupied_seats += 1
            transport.save()
            messages.success(request, "Transport allocated successfully!")
            return redirect('transport_allocations')
        else:
            messages.error(request, "Failed to allocate transport.")
    
    context = {
        'page_title': 'Allocate Transport',
        'form': form
    }
    return render(request, 'hod_template/allocate_transport.html', context)


# ==================== LIBRARY MANAGEMENT ====================

def manage_library(request):
    """Manage library books"""
    books = Library.objects.all().order_by('title')
    
    context = {
        'page_title': 'Library Management',
        'books': books
    }
    return render(request, 'hod_template/manage_library.html', context)


def add_library_book(request):
    """Add new book to library"""
    form = LibraryBookForm(request.POST or None, request.FILES or None)
    
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            messages.success(request, "Book added to library successfully!")
            return redirect('manage_library')
        else:
            messages.error(request, "Failed to add book. Please check the form.")
    
    context = {
        'page_title': 'Add Library Book',
        'form': form
    }
    return render(request, 'hod_template/add_library_book.html', context)


def edit_library_book(request, book_id):
    """Edit library book"""
    book = get_object_or_404(Library, id=book_id)
    form = LibraryBookForm(request.POST or None, request.FILES or None, instance=book)
    
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            messages.success(request, "Book updated successfully!")
            return redirect('manage_library')
        else:
            messages.error(request, "Failed to update book.")
    
    context = {
        'page_title': 'Edit Library Book',
        'form': form,
        'book': book
    }
    return render(request, 'hod_template/edit_library_book.html', context)


def library_issues(request):
    """View all library issues"""
    issues = LibraryIssue.objects.filter(status__in=['issued', 'overdue']).order_by('-issue_date')
    
    context = {
        'page_title': 'Library Issues',
        'issues': issues
    }
    return render(request, 'hod_template/library_issues.html', context)


def issue_library_book(request):
    """Issue book to student"""
    form = LibraryIssueForm(request.POST or None)
    
    if request.method == 'POST':
        if form.is_valid():
            issue = form.save(commit=False)
            issue.issued_by = get_staff_for_user(request)
            issue.status = 'issued'
            
            # Update available copies
            book = issue.book
            if book.available_copies > 0:
                book.available_copies -= 1
                book.save()
                issue.save()
                messages.success(request, f"Book issued to {issue.student} successfully!")
                return redirect('library_issues')
            else:
                messages.error(request, "Book not available!")
        else:
            messages.error(request, "Failed to issue book.")
    
    context = {
        'page_title': 'Issue Book',
        'form': form
    }
    return render(request, 'hod_template/issue_library_book.html', context)


def return_library_book(request, issue_id):
    """Return library book"""
    issue = get_object_or_404(LibraryIssue, id=issue_id)
    
    if request.method == 'POST':
        from django.utils import timezone
        from datetime import date
        
        issue.return_date = date.today()
        issue.status = 'returned'
        
        # Calculate fine if overdue
        if issue.return_date > issue.due_date:
            days_overdue = (issue.return_date - issue.due_date).days
            fine_per_day = 5  # ₹5 per day
            issue.fine_amount = days_overdue * fine_per_day
        
        # Update available copies
        book = issue.book
        book.available_copies += 1
        book.save()
        issue.save()
        
        if issue.fine_amount > 0:
            messages.warning(request, f"Book returned with fine of ₹{issue.fine_amount}")
        else:
            messages.success(request, "Book returned successfully!")
        
        return redirect('library_issues')
    
    context = {
        'page_title': 'Return Book',
        'issue': issue
    }
    return render(request, 'hod_template/return_library_book.html', context)


# ==================== HOSTEL MANAGEMENT ====================

def manage_hostels(request):
    """Manage all hostels"""
    hostels = Hostel.objects.all().order_by('name')
    
    context = {
        'page_title': 'Manage Hostels',
        'hostels': hostels
    }
    return render(request, 'hod_template/manage_hostels.html', context)


def add_hostel(request):
    """Add new hostel"""
    form = HostelForm(request.POST or None)
    
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            messages.success(request, "Hostel added successfully!")
            return redirect('manage_hostels')
        else:
            messages.error(request, "Failed to add hostel. Please check the form.")
    
    context = {
        'page_title': 'Add Hostel',
        'form': form
    }
    return render(request, 'hod_template/add_hostel.html', context)


def hostel_allocations(request):
    """View all hostel allocations"""
    allocations = HostelAllocation.objects.filter(is_active=True).order_by('hostel__name', 'room_number')
    
    context = {
        'page_title': 'Hostel Allocations',
        'allocations': allocations
    }
    return render(request, 'hod_template/hostel_allocations.html', context)


def allocate_hostel(request):
    """Allocate hostel room to student"""
    form = HostelAllocationForm(request.POST or None)
    
    if request.method == 'POST':
        if form.is_valid():
            allocation = form.save()
            # Update occupied rooms
            hostel = allocation.hostel
            hostel.occupied_rooms += 1
            hostel.save()
            messages.success(request, "Hostel allocated successfully!")
            return redirect('hostel_allocations')
        else:
            messages.error(request, "Failed to allocate hostel.")
    
    context = {
        'page_title': 'Allocate Hostel',
        'form': form
    }
    return render(request, 'hod_template/allocate_hostel.html', context)


def hostel_visitor_logs(request):
    """View hostel visitor logs"""
    logs = HostelVisitorLog.objects.all().order_by('-entry_time')[:100]
    
    context = {
        'page_title': 'Hostel Visitor Logs',
        'logs': logs
    }
    return render(request, 'hod_template/hostel_visitor_logs.html', context)


# ==================== SCHOLARSHIP MANAGEMENT ====================

def manage_scholarships(request):
    """Manage scholarship programs"""
    scholarships = Scholarship.objects.all().order_by('-application_deadline')
    
    context = {
        'page_title': 'Manage Scholarships',
        'scholarships': scholarships
    }
    return render(request, 'hod_template/manage_scholarships.html', context)


def add_scholarship(request):
    """Add new scholarship"""
    form = ScholarshipForm(request.POST or None)
    
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            messages.success(request, "Scholarship program created successfully!")
            return redirect('manage_scholarships')
        else:
            messages.error(request, "Failed to create scholarship.")
    
    context = {
        'page_title': 'Create Scholarship',
        'form': form
    }
    return render(request, 'hod_template/add_scholarship.html', context)


def scholarship_applications(request):
    """View all scholarship applications"""
    applications = ScholarshipApplication.objects.all().order_by('-application_date')
    
    # Statistics
    total = applications.count()
    pending = applications.filter(status='applied').count()
    approved = applications.filter(status='approved').count()
    disbursed = applications.filter(status='disbursed').count()
    
    context = {
        'page_title': 'Scholarship Applications',
        'applications': applications,
        'total': total,
        'pending': pending,
        'approved': approved,
        'disbursed': disbursed
    }
    return render(request, 'hod_template/scholarship_applications.html', context)


def review_scholarship_application(request, app_id):
    """Review and approve/reject scholarship application"""
    application = get_object_or_404(ScholarshipApplication, id=app_id)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        remarks = request.POST.get('review_remarks')
        
        application.reviewed_by = get_staff_for_user(request)
        application.review_remarks = remarks
        
        from django.utils import timezone
        application.reviewed_at = timezone.now()
        
        if action == 'approve':
            application.status = 'approved'
            messages.success(request, "Scholarship application approved!")
        elif action == 'reject':
            application.status = 'rejected'
            messages.warning(request, "Scholarship application rejected.")
        
        application.save()
        return redirect('scholarship_applications')
    
    context = {
        'page_title': 'Review Scholarship Application',
        'application': application
    }
    return render(request, 'hod_template/review_scholarship_application.html', context)


def disburse_scholarship(request, app_id):
    """Disburse scholarship amount"""
    application = get_object_or_404(ScholarshipApplication, id=app_id, status='approved')
    
    if request.method == 'POST':
        amount = request.POST.get('amount')
        date = request.POST.get('date')
        
        from datetime import datetime
        application.disbursement_amount = amount
        application.disbursement_date = datetime.strptime(date, '%Y-%m-%d').date()
        application.status = 'disbursed'
        application.save()
        
        messages.success(request, f"Scholarship of ₹{amount} disbursed successfully!")
        return redirect('scholarship_applications')
    
    context = {
        'page_title': 'Disburse Scholarship',
        'application': application
    }
    return render(request, 'hod_template/disburse_scholarship.html', context)


# ==================== TIMETABLE MANAGEMENT ====================

def manage_timetable(request):
    """Manage timetables"""
    # Get filter parameters
    session_id = request.GET.get('session')
    course_id = request.GET.get('course')
    semester = request.GET.get('semester')
    
    timetables = Timetable.objects.all()
    
    if session_id:
        timetables = timetables.filter(session_id=session_id)
    if course_id:
        timetables = timetables.filter(course_id=course_id)
    if semester:
        timetables = timetables.filter(semester=semester)
    
    timetables = timetables.order_by('weekday', 'period')
    
    # Get filter options
    sessions = Session.objects.all()
    courses = Course.objects.all()
    
    context = {
        'page_title': 'Manage Timetable',
        'timetables': timetables,
        'sessions': sessions,
        'courses': courses,
        'selected_session': session_id,
        'selected_course': course_id,
        'selected_semester': semester
    }
    return render(request, 'hod_template/manage_timetable.html', context)


def add_timetable(request):
    """Add timetable entry"""
    form = TimetableForm(request.POST or None)
    
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            messages.success(request, "Timetable entry added successfully!")
            return redirect('manage_timetable')
        else:
            messages.error(request, "Failed to add timetable entry. Check for conflicts.")
    
    context = {
        'page_title': 'Add Timetable Entry',
        'form': form
    }
    return render(request, 'hod_template/add_timetable.html', context)


# ==================== DEPARTMENT & PROGRAM MANAGEMENT ====================

def manage_departments(request):
    """Manage all departments"""
    departments = Department.objects.all().order_by('name')
    
    context = {
        'page_title': 'Manage Departments',
        'departments': departments
    }
    return render(request, 'hod_template/manage_departments.html', context)


def add_department(request):
    """Add new department"""
    form = DepartmentForm(request.POST or None)
    
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            messages.success(request, "Department created successfully!")
            return redirect('manage_departments')
        else:
            messages.error(request, "Failed to create department.")
    
    context = {
        'page_title': 'Add Department',
        'form': form
    }
    return render(request, 'hod_template/add_department.html', context)


def edit_department(request, dept_id):
    """Edit department"""
    department = get_object_or_404(Department, id=dept_id)
    form = DepartmentForm(request.POST or None, instance=department)
    
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            messages.success(request, "Department updated successfully!")
            return redirect('manage_departments')
        else:
            messages.error(request, "Failed to update department.")
    
    context = {
        'page_title': 'Edit Department',
        'form': form,
        'department': department
    }
    return render(request, 'hod_template/edit_department.html', context)


def manage_programs(request):
    """Manage all programs"""
    programs = Program.objects.all().order_by('department', 'program_type', 'name')
    
    context = {
        'page_title': 'Manage Programs',
        'programs': programs
    }
    return render(request, 'hod_template/manage_programs.html', context)


def add_program(request):
    """Add new program"""
    form = ProgramForm(request.POST or None, request.FILES or None)
    
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            messages.success(request, "Program created successfully!")
            return redirect('manage_programs')
        else:
            messages.error(request, "Failed to create program.")
    
    context = {
        'page_title': 'Add Program',
        'form': form
    }
    return render(request, 'hod_template/add_program.html', context)


def edit_program(request, program_id):
    """Edit program"""
    program = get_object_or_404(Program, id=program_id)
    form = ProgramForm(request.POST or None, request.FILES or None, instance=program)
    
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            messages.success(request, "Program updated successfully!")
            return redirect('manage_programs')
        else:
            messages.error(request, "Failed to update program.")
    
    context = {
        'page_title': 'Edit Program',
        'form': form,
        'program': program
    }
    return render(request, 'hod_template/edit_program.html', context)


# ==================== GRIEVANCE MANAGEMENT ====================

def view_grievances(request):
    """View all grievances"""
    grievances = Grievance.objects.all().order_by('-submitted_at')
    
    # Statistics
    total = grievances.count()
    pending = grievances.filter(status='submitted').count()
    in_progress = grievances.filter(status='in_progress').count()
    resolved = grievances.filter(status='resolved').count()
    
    context = {
        'page_title': 'Grievance Management',
        'grievances': grievances,
        'total': total,
        'pending': pending,
        'in_progress': in_progress,
        'resolved': resolved,
        'all_staff': Staff.objects.all().select_related('admin')
    }
    return render(request, 'hod_template/view_grievances.html', context)


def assign_grievance(request, grievance_id):
    """Assign grievance to staff"""
    grievance = get_object_or_404(Grievance, id=grievance_id)
    
    if request.method == 'POST':
        staff_id = request.POST.get('staff_id')
        staff = get_object_or_404(Staff, id=staff_id)
        
        grievance.assigned_to = staff
        grievance.status = 'in_progress'
        grievance.save()
        
        messages.success(request, f"Grievance assigned to {staff} successfully!")
        return redirect('view_grievances')
    
    staff_list = Staff.objects.filter(status='active')
    
    context = {
        'page_title': 'Assign Grievance',
        'grievance': grievance,
        'staff_list': staff_list
    }
    return render(request, 'hod_template/assign_grievance.html', context)


def resolve_grievance(request, grievance_id):
    """Resolve grievance"""
    grievance = get_object_or_404(Grievance, id=grievance_id)
    
    if request.method == 'POST':
        resolution = request.POST.get('resolution')
        
        from django.utils import timezone
        grievance.resolution = resolution
        grievance.status = 'resolved'
        grievance.resolved_at = timezone.now()
        grievance.save()
        
        messages.success(request, "Grievance marked as resolved!")
        return redirect('view_grievances')
    
    context = {
        'page_title': 'Resolve Grievance',
        'grievance': grievance
    }
    return render(request, 'hod_template/resolve_grievance.html', context)


# ==================== HOD/ADMIN USER MANAGEMENT ====================

def manage_admins(request):
    """Manage all admin/HOD users"""
    admins = Admin.objects.all().order_by('-admin__date_joined')
    
    context = {
        'page_title': 'Manage HOD/Admin Users',
        'admins': admins
    }
    return render(request, 'hod_template/manage_admins.html', context)


def add_admin(request):
    """Add new HOD/Admin user"""
    form = AdminForm(request.POST or None, request.FILES or None)
    context = {'form': form, 'page_title': 'Add Admin/HOD User'}
    
    if request.method == 'POST':
        if form.is_valid():
            first_name = form.cleaned_data.get('first_name')
            last_name = form.cleaned_data.get('last_name')
            address = form.cleaned_data.get('address')
            email = form.cleaned_data.get('email')
            gender = form.cleaned_data.get('gender')
            password = form.cleaned_data.get('password')
            
            try:
                user = CustomUser.objects.create_user(
                    username=email,
                    password=password,
                    email=email,
                    first_name=first_name,
                    last_name=last_name,
                    user_type=1
                )
                user.gender = gender
                user.address = address
                user.save()
                
                messages.success(request, "Admin user created successfully!")
                return redirect('manage_admins')
            except Exception as e:
                messages.error(request, f"Failed to create admin user: {str(e)}")
        else:
            messages.error(request, "Form has errors!")
    
    return render(request, 'hod_template/add_admin.html', context)


def edit_admin(request, admin_id):
    """Edit admin/HOD user"""
    admin = get_object_or_404(Admin, id=admin_id)
    form = AdminForm(request.POST or None, request.FILES or None, instance=admin)
    
    context = {
        'form': form,
        'admin': admin,
        'page_title': 'Edit Admin User'
    }
    
    if request.method == 'POST':
        if form.is_valid():
            first_name = form.cleaned_data.get('first_name')
            last_name = form.cleaned_data.get('last_name')
            address = form.cleaned_data.get('address')
            gender = form.cleaned_data.get('gender')
            password = form.cleaned_data.get('password')
            
            admin_user = admin.admin
            admin_user.first_name = first_name
            admin_user.last_name = last_name
            admin_user.address = address
            admin_user.gender = gender
            
            if password:
                admin_user.set_password(password)
            
            admin_user.save()
            messages.success(request, "Admin user updated successfully!")
            return redirect('manage_admins')
        else:
            messages.error(request, "Form has errors!")
    
    return render(request, 'hod_template/edit_admin.html', context)


def delete_admin(request, admin_id):
    """Delete admin user"""
    admin = get_object_or_404(Admin, id=admin_id)
    
    # Prevent self-deletion
    if admin.admin == request.user:
        messages.error(request, "You cannot delete your own account!")
        return redirect('manage_admins')
    
    if request.method == 'POST':
        admin_name = f"{admin.admin.first_name} {admin.admin.last_name}"
        admin.admin.delete()
        messages.success(request, f"Admin user {admin_name} deleted successfully!")
        return redirect('manage_admins')
    
    context = {
        'page_title': 'Delete Admin User',
        'admin': admin
    }
    return render(request, 'hod_template/delete_admin.html', context)


# ==================== ANALYTICS & REPORTS ====================

def admin_analytics_dashboard(request):
    """Comprehensive analytics dashboard"""
    
    # Student Analytics
    total_students = Student.objects.count()
    active_students = Student.objects.filter(student_status='active').count()
    graduated_students = Student.objects.filter(student_status='graduated').count()
    
    # Category-wise distribution
    from django.db.models import Count
    category_stats = Student.objects.values('caste_category').annotate(count=Count('id'))
    
    # Course-wise distribution
    course_stats = Student.objects.values('course__name').annotate(count=Count('id'))
    
    # Fee Statistics
    total_fee_collected = sum([p.amount_paid for p in FeePayment.objects.filter(status='paid')])
    pending_fees = FeePayment.objects.filter(status__in=['pending', 'partial', 'overdue']).count()
    
    # Placement Statistics
    total_companies = Company.objects.count()
    active_drives = PlacementDrive.objects.filter(is_active=True).count()
    total_applications = PlacementApplication.objects.count()
    selected_students = PlacementApplication.objects.filter(status='selected').count()
    
    # Hostel & Transport
    total_hostel_rooms = sum([h.total_rooms for h in Hostel.objects.all()])
    occupied_hostel_rooms = sum([h.occupied_rooms for h in Hostel.objects.all()])
    total_transport_seats = sum([t.total_seats for t in Transport.objects.all()])
    occupied_transport_seats = sum([t.occupied_seats for t in Transport.objects.all()])
    
    # Library Statistics
    total_books = Library.objects.count()
    total_copies = sum([b.total_copies for b in Library.objects.all()])
    active_issues = LibraryIssue.objects.filter(status__in=['issued', 'overdue']).count()
    
    # Scholarship Statistics
    active_scholarships = Scholarship.objects.filter(is_active=True).count()
    scholarship_apps = ScholarshipApplication.objects.count()
    approved_scholarships = ScholarshipApplication.objects.filter(status='approved').count()
    
    context = {
        'page_title': 'Analytics Dashboard',
        'total_students': total_students,
        'active_students': active_students,
        'graduated_students': graduated_students,
        'category_stats': category_stats,
        'course_stats': course_stats,
        'total_fee_collected': total_fee_collected,
        'pending_fees': pending_fees,
        'total_companies': total_companies,
        'active_drives': active_drives,
        'total_applications': total_applications,
        'selected_students': selected_students,
        'total_hostel_rooms': total_hostel_rooms,
        'occupied_hostel_rooms': occupied_hostel_rooms,
        'total_transport_seats': total_transport_seats,
        'occupied_transport_seats': occupied_transport_seats,
        'total_books': total_books,
        'total_copies': total_copies,
        'active_issues': active_issues,
        'active_scholarships': active_scholarships,
        'scholarship_apps': scholarship_apps,
        'approved_scholarships': approved_scholarships,
    }
    return render(request, 'hod_template/analytics_dashboard.html', context)


# ============================================================================
# ONLINE EXAMINATION MANAGEMENT
# ============================================================================

@login_required
def manage_online_exams(request):
    """View all online exams"""
    context = {
        'page_title': 'Manage Online Exams',
        'exams': OnlineExam.objects.all().select_related('subject', 'course', 'created_by').order_by('-created_at')
    }
    return render(request, 'hod_template/manage_online_exams.html', context)


@login_required
def create_online_exam(request):
    """Create new online exam"""
    if request.method == 'POST':
        form = OnlineExamForm(request.POST)
        if form.is_valid():
            exam = form.save(commit=False)
            exam.created_by = get_staff_for_user(request)
            exam.save()
            messages.success(request, "Online exam created successfully!")
            return redirect('manage_online_exams')
        else:
            messages.error(request, "Failed to create exam. Check the form.")
    else:
        form = OnlineExamForm()
    
    context = {
        'page_title': 'Create Online Exam',
        'form': form
    }
    return render(request, 'hod_template/create_online_exam.html', context)


@login_required
def add_exam_questions(request, exam_id):
    """Add questions to an online exam"""
    exam = get_object_or_404(OnlineExam, id=exam_id)
    
    if request.method == 'POST':
        form = OnlineExamQuestionForm(request.POST)
        if form.is_valid():
            question = form.save(commit=False)
            question.exam = exam
            question.save()
            messages.success(request, "Question added successfully!")
            return redirect('add_exam_questions', exam_id=exam_id)
    else:
        form = OnlineExamQuestionForm()
    
    context = {
        'page_title': f'Add Questions - {exam.title}',
        'form': form,
        'exam': exam,
        'questions': exam.questions.all()
    }
    return render(request, 'hod_template/add_exam_questions.html', context)


# ============================================================================
# CERTIFICATE MANAGEMENT
# ============================================================================

@login_required
def manage_certificates(request):
    """View all certificates"""
    context = {
        'page_title': 'Manage Certificates',
        'certificates': Certificate.objects.all().select_related('student', 'issued_by').order_by('-issued_date')
    }
    return render(request, 'hod_template/manage_certificates.html', context)


@login_required
def issue_certificate(request):
    """Issue new certificate"""
    if request.method == 'POST':
        form = CertificateForm(request.POST, request.FILES)
        if form.is_valid():
            cert = form.save(commit=False)
            cert.issued_by = get_staff_for_user(request)
            cert.is_verified = True
            cert.save()
            messages.success(request, f"Certificate {cert.certificate_number} issued successfully!")
            return redirect('manage_certificates')
    else:
        # Auto-generate certificate number
        import random
        cert_number = f"CERT{datetime.now().year}{random.randint(1000, 9999)}"
        form = CertificateForm(initial={'certificate_number': cert_number, 'issued_date': datetime.now().date()})
    
    context = {
        'page_title': 'Issue Certificate',
        'form': form
    }
    return render(request, 'hod_template/issue_certificate.html', context)


# ============================================================================
# ALUMNI MANAGEMENT
# ============================================================================

@login_required
def manage_alumni(request):
    """View all alumni"""
    context = {
        'page_title': 'Alumni Database',
        'alumni': Alumni.objects.all().select_related('student').order_by('-passout_year')
    }
    return render(request, 'hod_template/manage_alumni.html', context)


# ============================================================================
# INTERNSHIP MANAGEMENT
# ============================================================================

@login_required
def manage_internships(request):
    """View all student internships"""
    context = {
        'page_title': 'Manage Internships',
        'internships': Internship.objects.all().select_related('student', 'approved_by').order_by('-created_at')
    }
    return render(request, 'hod_template/manage_internships.html', context)


@login_required
def approve_internship(request, internship_id):
    """Approve/reject internship"""
    internship = get_object_or_404(Internship, id=internship_id)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'approve':
            internship.status = 'ongoing'
            internship.approved_by = get_staff_for_user(request)
            messages.success(request, "Internship approved!")
        elif action == 'reject':
            internship.status = 'cancelled'
            messages.success(request, "Internship rejected!")
        internship.save()
        return redirect('manage_internships')
    
    return redirect('manage_internships')


# ============================================================================
# SPORTS & ACTIVITIES
# ============================================================================

@login_required
def manage_sports_activities(request):
    """View all sports and cultural activities"""
    context = {
        'page_title': 'Sports & Cultural Activities',
        'activities': SportsActivity.objects.all().select_related('coordinator').order_by('-start_date')
    }
    return render(request, 'hod_template/manage_sports_activities.html', context)


@login_required
def create_activity(request):
    """Create new activity"""
    if request.method == 'POST':
        form = SportsActivityForm(request.POST)
        if form.is_valid():
            activity = form.save()
            messages.success(request, f"Activity '{activity.name}' created successfully!")
            return redirect('manage_sports_activities')
    else:
        form = SportsActivityForm()
    
    context = {
        'page_title': 'Create Activity',
        'form': form
    }
    return render(request, 'hod_template/create_activity.html', context)


# ============================================================================
# GATE PASS MANAGEMENT
# ============================================================================

@login_required
def manage_gate_passes(request):
    """View all gate pass requests"""
    context = {
        'page_title': 'Manage Gate Passes',
        'gate_passes': GatePass.objects.all().select_related('student', 'approved_by').order_by('-created_at')
    }
    return render(request, 'hod_template/manage_gate_passes.html', context)


@login_required
def approve_gate_pass(request, pass_id):
    """Approve/reject gate pass"""
    gate_pass = get_object_or_404(GatePass, id=pass_id)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'approve':
            gate_pass.status = 'approved'
            gate_pass.approved_by = get_staff_for_user(request)
            gate_pass.approval_date = datetime.now()
            messages.success(request, "Gate pass approved!")
        elif action == 'reject':
            gate_pass.status = 'rejected'
            messages.success(request, "Gate pass rejected!")
        gate_pass.save()
    
    return redirect('manage_gate_passes')


# ============================================================================
# DISCIPLINARY ACTIONS
# ============================================================================

@login_required
def manage_disciplinary_actions(request):
    """View all disciplinary actions"""
    context = {
        'page_title': 'Disciplinary Actions',
        'actions': DisciplinaryAction.objects.all().select_related('student', 'reported_by', 'action_by').order_by('-incident_date')
    }
    return render(request, 'hod_template/manage_disciplinary_actions.html', context)


@login_required
def add_disciplinary_action(request):
    """Add new disciplinary action"""
    if request.method == 'POST':
        form = DisciplinaryActionForm(request.POST)
        if form.is_valid():
            action = form.save(commit=False)
            action.action_by = get_staff_for_user(request)
            action.save()
            messages.success(request, "Disciplinary action recorded!")
            return redirect('manage_disciplinary_actions')
    else:
        form = DisciplinaryActionForm()
    
    context = {
        'page_title': 'Add Disciplinary Action',
        'form': form
    }
    return render(request, 'hod_template/add_disciplinary_action.html', context)


# ============================================================================
# ANTI-RAGGING
# ============================================================================

@login_required
def manage_ragging_incidents(request):
    """View all ragging incidents"""
    context = {
        'page_title': 'Anti-Ragging Incidents',
        'incidents': AntiRaggingCommittee.objects.all().select_related('reporter', 'investigating_officer').order_by('-created_at'),
        'all_staff': Staff.objects.all().select_related('admin')
    }
    return render(request, 'hod_template/manage_ragging_incidents.html', context)


@login_required
def assign_ragging_investigator(request, incident_id):
    """Assign investigating officer"""
    incident = get_object_or_404(AntiRaggingCommittee, id=incident_id)
    
    if request.method == 'POST':
        staff_id = request.POST.get('investigator')
        if staff_id:
            incident.investigating_officer_id = staff_id
            incident.status = 'investigating'
            incident.save()
            messages.success(request, "Investigator assigned!")
    
    return redirect('manage_ragging_incidents')


# ============================================================================
# STUDENT COUNCIL
# ============================================================================

@login_required
def manage_student_council(request):
    """View student council members"""
    context = {
        'page_title': 'Student Council',
        'council_members': StudentCouncil.objects.filter(is_active=True).select_related('student', 'session', 'department')
    }
    return render(request, 'hod_template/manage_student_council.html', context)


@login_required
def add_council_member(request):
    """Add student council member"""
    if request.method == 'POST':
        form = StudentCouncilForm(request.POST)
        if form.is_valid():
            member = form.save()
            messages.success(request, f"{member.student} added to council as {member.get_position_display()}!")
            return redirect('manage_student_council')
    else:
        form = StudentCouncilForm()
    
    context = {
        'page_title': 'Add Council Member',
        'form': form
    }
    return render(request, 'hod_template/add_council_member.html', context)


# ============================================================================
# CLASSROOM MANAGEMENT
# ============================================================================

@login_required
def manage_classrooms(request):
    """View all classrooms"""
    classrooms = Classroom.objects.all().select_related('department').order_by('building', 'floor', 'room_number')
    
    # Statistics
    total_rooms = classrooms.count()
    available_rooms = classrooms.filter(is_available=True, is_under_maintenance=False).count()
    labs = classrooms.filter(room_type='lab').count()
    
    context = {
        'page_title': 'Manage Classrooms',
        'classrooms': classrooms,
        'total_rooms': total_rooms,
        'available_rooms': available_rooms,
        'labs': labs
    }
    return render(request, 'hod_template/manage_classrooms.html', context)


@login_required
def add_classroom(request):
    """Add new classroom"""
    if request.method == 'POST':
        form = ClassroomForm(request.POST)
        if form.is_valid():
            classroom = form.save()
            messages.success(request, f"Classroom {classroom.room_number} added successfully!")
            return redirect('manage_classrooms')
    else:
        form = ClassroomForm()
    
    context = {
        'page_title': 'Add Classroom',
        'form': form
    }
    return render(request, 'hod_template/add_classroom.html', context)


@login_required
def edit_classroom(request, classroom_id):
    """Edit classroom"""
    classroom = get_object_or_404(Classroom, id=classroom_id)
    form = ClassroomForm(request.POST or None, instance=classroom)
    
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            messages.success(request, "Classroom updated successfully!")
            return redirect('manage_classrooms')
    
    context = {
        'page_title': 'Edit Classroom',
        'form': form,
        'classroom': classroom
    }
    return render(request, 'hod_template/edit_classroom.html', context)


@login_required
def manage_classroom_bookings(request):
    """View all classroom bookings"""
    bookings = ClassroomBooking.objects.all().select_related('classroom', 'booked_by', 'subject', 'course').order_by('-booking_date', 'start_time')
    
    context = {
        'page_title': 'Classroom Bookings',
        'bookings': bookings
    }
    return render(request, 'hod_template/classroom_bookings.html', context)


@login_required
def book_classroom(request):
    """Book a classroom"""
    if request.method == 'POST':
        form = ClassroomBookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.booked_by = get_staff_for_user(request)
            booking.save()
            messages.success(request, f"Classroom {booking.classroom.room_number} booked successfully!")
            return redirect('manage_classroom_bookings')
    else:
        form = ClassroomBookingForm()
    
    context = {
        'page_title': 'Book Classroom',
        'form': form,
        'available_classrooms': Classroom.objects.filter(is_available=True, is_under_maintenance=False)
    }
    return render(request, 'hod_template/book_classroom.html', context)


@login_required
def classroom_schedule(request):
    """View classroom schedule/availability"""
    from datetime import datetime, timedelta
    
    today = datetime.now().date()
    week_days = [today + timedelta(days=i) for i in range(7)]
    
    classrooms = Classroom.objects.filter(is_available=True)
    
    context = {
        'page_title': 'Classroom Schedule',
        'classrooms': classrooms,
        'week_days': week_days,
        'today': today
    }
    return render(request, 'hod_template/classroom_schedule.html', context)


@login_required
def classroom_maintenance(request):
    """View maintenance records"""
    maintenance_records = ClassroomMaintenance.objects.all().select_related('classroom', 'reported_by').order_by('-reported_date')
    
    context = {
        'page_title': 'Classroom Maintenance',
        'maintenance_records': maintenance_records
    }
    return render(request, 'hod_template/classroom_maintenance.html', context)


@login_required
def report_maintenance(request):
    """Report classroom maintenance issue"""
    if request.method == 'POST':
        form = ClassroomMaintenanceForm(request.POST)
        if form.is_valid():
            maintenance = form.save(commit=False)
            maintenance.reported_by = get_staff_for_user(request)
            maintenance.save()
            
            # Mark classroom as under maintenance
            classroom = maintenance.classroom
            classroom.is_under_maintenance = True
            classroom.save()
            
            messages.success(request, "Maintenance issue reported successfully!")
            return redirect('classroom_maintenance')
    else:
        form = ClassroomMaintenanceForm()
    
    context = {
        'page_title': 'Report Maintenance Issue',
        'form': form
    }
    return render(request, 'hod_template/report_maintenance.html', context)


@login_required
def approve_classroom_booking(request, booking_id):
    """Approve classroom booking"""
    booking = get_object_or_404(ClassroomBooking, id=booking_id)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'approve':
            booking.status = 'approved'
            booking.approved_by = get_staff_for_user(request)
            from datetime import datetime
            booking.approval_date = datetime.now()
            messages.success(request, "Booking approved!")
        elif action == 'reject':
            booking.status = 'rejected'
            messages.success(request, "Booking rejected!")
        booking.save()
    
    return redirect('manage_classroom_bookings')

