from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse


@login_required(login_url='login')
def lms_dashboard(request):
    """LMS dashboard"""
    context = {'page_title': 'LMS Dashboard'}
    return render(request, 'hod_template/lms_dashboard.html', context)


# Course Module Management
@login_required(login_url='login')
def manage_course_modules(request):
    """Manage course modules"""
    if request.user.user_type != '1':
        messages.error(request, 'Access denied')
        return redirect('login')
    
    context = {'page_title': 'Manage Course Modules'}
    return render(request, 'hod_template/manage_course_modules.html', context)


@login_required(login_url='login')
def add_course_module(request):
    """Add course module"""
    if request.user.user_type != '1':
        messages.error(request, 'Access denied')
        return redirect('login')
    
    context = {'page_title': 'Add Course Module'}
    return render(request, 'hod_template/add_course_module.html', context)


@login_required(login_url='login')
def edit_course_module(request, module_id):
    """Edit course module"""
    if request.user.user_type != '1':
        messages.error(request, 'Access denied')
        return redirect('login')
    
    context = {'page_title': 'Edit Course Module', 'module_id': module_id}
    return render(request, 'hod_template/edit_course_module.html', context)


# Quiz Management
@login_required(login_url='login')
def manage_quizzes(request):
    """Manage quizzes"""
    if request.user.user_type != '1':
        messages.error(request, 'Access denied')
        return redirect('login')
    
    context = {'page_title': 'Manage Quizzes'}
    return render(request, 'hod_template/manage_quizzes.html', context)


@login_required(login_url='login')
def add_quiz(request, module_id):
    """Add quiz"""
    if request.user.user_type != '1':
        messages.error(request, 'Access denied')
        return redirect('login')
    
    context = {'page_title': 'Add Quiz', 'module_id': module_id}
    return render(request, 'hod_template/add_quiz.html', context)


@login_required(login_url='login')
def manage_quiz_questions(request, quiz_id):
    """Manage quiz questions"""
    if request.user.user_type != '1':
        messages.error(request, 'Access denied')
        return redirect('login')
    
    context = {'page_title': 'Manage Quiz Questions', 'quiz_id': quiz_id}
    return render(request, 'hod_template/manage_quiz_questions.html', context)


@login_required(login_url='login')
def add_quiz_question(request, quiz_id):
    """Add quiz question"""
    if request.user.user_type != '1':
        messages.error(request, 'Access denied')
        return redirect('login')
    
    context = {'page_title': 'Add Quiz Question', 'quiz_id': quiz_id}
    return render(request, 'hod_template/add_quiz_question.html', context)


@login_required(login_url='login')
def manage_question_options(request, question_id):
    """Manage question options"""
    if request.user.user_type != '1':
        messages.error(request, 'Access denied')
        return redirect('login')
    
    context = {'page_title': 'Manage Question Options', 'question_id': question_id}
    return render(request, 'hod_template/manage_question_options.html', context)


# Assignment Management
@login_required(login_url='login')
def manage_assignments(request):
    """Manage assignments"""
    if request.user.user_type != '1':
        messages.error(request, 'Access denied')
        return redirect('login')
    
    context = {'page_title': 'Manage Assignments'}
    return render(request, 'hod_template/manage_assignments.html', context)


@login_required(login_url='login')
def add_assignment(request):
    """Add assignment"""
    if request.user.user_type != '1':
        messages.error(request, 'Access denied')
        return redirect('login')
    
    context = {'page_title': 'Add Assignment'}
    return render(request, 'hod_template/add_assignment.html', context)


@login_required(login_url='login')
def view_assignment_submissions(request, assignment_id):
    """View assignment submissions"""
    if request.user.user_type != '1':
        messages.error(request, 'Access denied')
        return redirect('login')
    
    context = {'page_title': 'Assignment Submissions', 'assignment_id': assignment_id}
    return render(request, 'hod_template/view_assignment_submissions.html', context)


@login_required(login_url='login')
def grade_assignment(request, submission_id):
    """Grade assignment"""
    if request.user.user_type != '1':
        messages.error(request, 'Access denied')
        return redirect('login')
    
    context = {'page_title': 'Grade Assignment', 'submission_id': submission_id}
    return render(request, 'hod_template/grade_assignment.html', context)


# Enrollment Management
@login_required(login_url='login')
def manage_course_enrollments(request):
    """Manage course enrollments"""
    if request.user.user_type != '1':
        messages.error(request, 'Access denied')
        return redirect('login')
    
    context = {'page_title': 'Manage Course Enrollments'}
    return render(request, 'hod_template/manage_course_enrollments.html', context)


@login_required(login_url='login')
def bulk_enroll_students(request):
    """Bulk enroll students"""
    if request.user.user_type != '1':
        messages.error(request, 'Access denied')
        return redirect('login')
    
    context = {'page_title': 'Bulk Enroll Students'}
    return render(request, 'hod_template/bulk_enroll_students.html', context)


# Staff LMS Views
@login_required(login_url='login')
def staff_lms_dashboard(request):
    """Staff LMS dashboard"""
    if request.user.user_type != '2':
        messages.error(request, 'Access denied')
        return redirect('login')
    
    context = {'page_title': 'LMS Dashboard'}
    return render(request, 'staff_template/lms_dashboard.html', context)


@login_required(login_url='login')
def staff_view_modules(request):
    """Staff view modules"""
    if request.user.user_type != '2':
        messages.error(request, 'Access denied')
        return redirect('login')
    
    context = {'page_title': 'View Modules'}
    return render(request, 'staff_template/view_modules.html', context)


@login_required(login_url='login')
def staff_view_assignments(request):
    """Staff view assignments"""
    if request.user.user_type != '2':
        messages.error(request, 'Access denied')
        return redirect('login')
    
    context = {'page_title': 'View Assignments'}
    return render(request, 'staff_template/view_assignments.html', context)


# Student LMS Views
@login_required(login_url='login')
def student_lms_dashboard(request):
    """Student LMS dashboard"""
    if request.user.user_type != '3':
        messages.error(request, 'Access denied')
        return redirect('login')
    
    context = {'page_title': 'LMS Dashboard'}
    return render(request, 'student_template/lms_dashboard.html', context)


@login_required(login_url='login')
def student_view_course_modules(request, course_id):
    """Student view course modules"""
    if request.user.user_type != '3':
        messages.error(request, 'Access denied')
        return redirect('login')
    
    context = {'page_title': 'Course Modules', 'course_id': course_id}
    return render(request, 'student_template/view_course_modules.html', context)


@login_required(login_url='login')
def student_view_module(request, module_id):
    """Student view module"""
    if request.user.user_type != '3':
        messages.error(request, 'Access denied')
        return redirect('login')
    
    context = {'page_title': 'View Module', 'module_id': module_id}
    return render(request, 'student_template/view_module.html', context)


@login_required(login_url='login')
def student_take_quiz(request, quiz_id):
    """Student take quiz"""
    if request.user.user_type != '3':
        messages.error(request, 'Access denied')
        return redirect('login')
    
    context = {'page_title': 'Take Quiz', 'quiz_id': quiz_id}
    return render(request, 'student_template/take_quiz.html', context)


@login_required(login_url='login')
def student_quiz_result(request, attempt_id):
    """Student quiz result"""
    if request.user.user_type != '3':
        messages.error(request, 'Access denied')
        return redirect('login')
    
    context = {'page_title': 'Quiz Result', 'attempt_id': attempt_id}
    return render(request, 'student_template/quiz_result.html', context)


@login_required(login_url='login')
def student_view_assignments(request):
    """Student view assignments"""
    if request.user.user_type != '3':
        messages.error(request, 'Access denied')
        return redirect('login')
    
    context = {'page_title': 'View Assignments'}
    return render(request, 'student_template/view_assignments.html', context)


@login_required(login_url='login')
def student_submit_assignment(request, assignment_id):
    """Student submit assignment"""
    if request.user.user_type != '3':
        messages.error(request, 'Access denied')
        return redirect('login')
    
    context = {'page_title': 'Submit Assignment', 'assignment_id': assignment_id}
    return render(request, 'student_template/submit_assignment.html', context)


# AJAX Endpoints
def mark_module_complete(request):
    """AJAX endpoint to mark module complete"""
    if request.method == 'POST':
        # Add logic to mark module complete
        success = True  # Replace with actual logic
        return JsonResponse({'success': success})
    return JsonResponse({'error': 'Invalid request'}, status=400)


def toggle_bookmark(request):
    """AJAX endpoint to toggle bookmark"""
    if request.method == 'POST':
        # Add logic to toggle bookmark
        success = True  # Replace with actual logic
        return JsonResponse({'success': success})
    return JsonResponse({'error': 'Invalid request'}, status=400)