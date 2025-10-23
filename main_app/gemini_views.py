"""
Views for Gemini AI-powered features
"""

from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
import json

from .gemini_service import GeminiAIService
from .models import Student, Staff, StudentResult, Attendance, Subject, StudyMaterial
from .decorators import hod_required, staff_required, student_required


@login_required
@hod_required
def ai_student_insights_enhanced(request):
    """
    Enhanced AI-powered student insights dashboard using Gemini
    """
    try:
        students = Student.objects.select_related('user', 'course').all()
        insights_list = []
        
        for student in students[:10]:  # Limit to 10 for performance
            # Gather student data
            attendance_records = Attendance.objects.filter(student=student)
            total_classes = attendance_records.count()
            attended = attendance_records.filter(status=True).count()
            attendance_pct = (attended / total_classes * 100) if total_classes > 0 else 0
            
            results = StudentResult.objects.filter(student=student)
            avg_marks = sum([r.marks for r in results]) / len(results) if results else 0
            
            student_data = {
                'name': f"{student.user.first_name} {student.user.last_name}",
                'roll_number': student.roll_number,
                'course': student.course.name if student.course else 'N/A',
                'cgpa': avg_marks / 10 if avg_marks > 0 else 0,
                'attendance': round(attendance_pct, 2),
                'subjects': [r.subject.name for r in results],
                'marks': [r.marks for r in results],
                'assignments_completed': 0,  # Placeholder
                'total_assignments': 0  # Placeholder
            }
            
            # Get AI analysis
            ai_analysis = GeminiAIService.analyze_student_performance(student_data)
            
            if ai_analysis['success']:
                insights_list.append({
                    'student': student,
                    'data': student_data,
                    'ai_insights': ai_analysis['data']
                })
        
        context = {
            'page_title': 'AI Student Insights',
            'insights': insights_list
        }
        
        return render(request, 'hod_template/ai_insights_enhanced.html', context)
        
    except Exception as e:
        messages.error(request, f'Error generating AI insights: {str(e)}')
        return redirect('admin_home')


@login_required
@require_http_methods(["POST"])
def ai_chatbot_api(request):
    """
    API endpoint for AI chatbot responses
    """
    try:
        data = json.loads(request.body)
        user_message = data.get('message', '')
        
        if not user_message:
            return JsonResponse({
                'success': False,
                'error': 'Message is required'
            }, status=400)
        
        # Build context based on user role
        context = {
            'user_type': request.user.user_type,
            'user_name': f"{request.user.first_name} {request.user.last_name}"
        }
        
        if request.user.user_type == '3':  # Student
            try:
                student = Student.objects.get(user=request.user)
                context['roll_number'] = student.roll_number
                context['course'] = student.course.name if student.course else 'N/A'
            except Student.DoesNotExist:
                pass
        
        # Get AI response
        ai_response = GeminiAIService.chatbot_response(user_message, context)
        
        return JsonResponse({
            'success': True,
            'response': ai_response,
            'timestamp': str(timezone.now())
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@staff_required
def ai_generate_study_material(request):
    """
    AI-powered study material generator for faculty
    """
    if request.method == 'POST':
        subject = request.POST.get('subject')
        topic = request.POST.get('topic')
        difficulty = request.POST.get('difficulty', 'intermediate')
        
        # Generate content using AI
        result = GeminiAIService.generate_study_content(subject, topic, difficulty)
        
        if result['success']:
            messages.success(request, 'Study material generated successfully!')
            context = {
                'page_title': 'AI Generated Study Material',
                'content': result['content'],
                'subject': subject,
                'topic': topic,
                'difficulty': difficulty
            }
            return render(request, 'staff_template/ai_generated_content.html', context)
        else:
            messages.error(request, f'Error generating content: {result.get("error", "Unknown error")}')
    
    # GET request - show form
    subjects = Subject.objects.all()
    context = {
        'page_title': 'Generate Study Material with AI',
        'subjects': subjects
    }
    return render(request, 'staff_template/ai_content_generator.html', context)


@login_required
def ai_compose_email(request):
    """
    AI-powered email composer
    """
    if request.method == 'POST':
        purpose = request.POST.get('purpose')
        recipient_type = request.POST.get('recipient_type')
        
        context_data = {
            'sender_name': f"{request.user.first_name} {request.user.last_name}",
            'sender_role': 'HOD' if request.user.user_type == '1' else 'Faculty',
            'purpose_details': request.POST.get('purpose_details', '')
        }
        
        result = GeminiAIService.compose_email(purpose, recipient_type, context_data)
        
        if result['success']:
            context = {
                'page_title': 'AI Composed Email',
                'email_data': result['email'],
                'purpose': purpose,
                'recipient_type': recipient_type
            }
            return render(request, 'hod_template/ai_email_preview.html', context)
        else:
            messages.error(request, f'Error composing email: {result.get("error", "Unknown error")}')
    
    context = {
        'page_title': 'AI Email Composer'
    }
    return render(request, 'hod_template/ai_email_composer.html', context)


@login_required
@staff_required
def ai_generate_questions(request):
    """
    AI-powered exam question generator
    """
    if request.method == 'POST':
        subject = request.POST.get('subject')
        topic = request.POST.get('topic')
        num_questions = int(request.POST.get('num_questions', 10))
        difficulty = request.POST.get('difficulty', 'mixed')
        
        result = GeminiAIService.generate_exam_questions(subject, topic, num_questions, difficulty)
        
        if result['success']:
            context = {
                'page_title': 'AI Generated Questions',
                'questions': result['questions'],
                'subject': subject,
                'topic': topic
            }
            return render(request, 'staff_template/ai_questions_preview.html', context)
        else:
            messages.error(request, f'Error generating questions: {result.get("error", "Unknown error")}')
    
    subjects = Subject.objects.all()
    context = {
        'page_title': 'AI Question Generator',
        'subjects': subjects
    }
    return render(request, 'staff_template/ai_question_generator.html', context)


@login_required
@student_required
def ai_career_counseling(request):
    """
    AI-powered career counseling for students
    """
    try:
        student = Student.objects.get(user=request.user)
        
        # Gather student profile data
        results = StudentResult.objects.filter(student=student)
        subjects_marks = {r.subject.name: r.marks for r in results}
        avg_marks = sum(subjects_marks.values()) / len(subjects_marks) if subjects_marks else 0
        
        # Identify strong and weak subjects
        sorted_subjects = sorted(subjects_marks.items(), key=lambda x: x[1], reverse=True)
        strong_subjects = [s[0] for s in sorted_subjects[:3]] if len(sorted_subjects) >= 3 else [s[0] for s in sorted_subjects]
        weak_subjects = [s[0] for s in sorted_subjects[-2:]] if len(sorted_subjects) >= 2 else []
        
        student_profile = {
            'course': student.course.name if student.course else 'N/A',
            'cgpa': round(avg_marks / 10, 2),
            'strong_subjects': strong_subjects,
            'weak_subjects': weak_subjects,
            'skills': [],  # Can be expanded with a Skills model
            'interests': [],  # Can be expanded with an Interests model
            'projects': []  # Can be expanded with a Projects model
        }
        
        result = GeminiAIService.career_counseling(student_profile)
        
        if result['success']:
            context = {
                'page_title': 'AI Career Counseling',
                'student_profile': student_profile,
                'counseling': result['counseling']
            }
            return render(request, 'student_template/ai_career_counseling.html', context)
        else:
            messages.error(request, f'Error generating career counseling: {result.get("error", "Unknown error")}')
            return redirect('student_home')
            
    except Student.DoesNotExist:
        messages.error(request, 'Student profile not found')
        return redirect('student_home')
    except Exception as e:
        messages.error(request, f'Error: {str(e)}')
        return redirect('student_home')


@login_required
def ai_chatbot_interface(request):
    """
    Chatbot interface for all users
    """
    context = {
        'page_title': 'AI Assistant Chatbot'
    }
    
    # Determine template based on user role
    if request.user.user_type == '1':
        template = 'hod_template/ai_chatbot.html'
    elif request.user.user_type == '2':
        template = 'staff_template/ai_chatbot.html'
    elif request.user.user_type == '3':
        template = 'student_template/ai_chatbot.html'
    else:
        template = 'management_template/ai_chatbot.html'
    
    return render(request, template, context)


from django.utils import timezone

