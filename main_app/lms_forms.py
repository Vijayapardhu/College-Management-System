"""
Forms for Learning Management System (LMS)
"""
from django import forms
from django.utils import timezone
from .models import Course, Subject, Staff, Student
from .lms_models import (
    CourseModule, Quiz, Question, QuestionOption, QuizAttempt,
    StudentProgress, CourseEnrollment, DiscussionForum, DiscussionPost,
    LMSAssignment, LMSAssignmentSubmission
)


class CourseModuleForm(forms.ModelForm):
    """Form for creating/editing course modules"""
    class Meta:
        model = CourseModule
        fields = [
            'course', 'subject', 'title', 'description', 'module_type',
            'content', 'video_url', 'attachment', 'is_published',
            'is_required', 'estimated_duration', 'prerequisites', 'order'
        ]
        widgets = {
            'course': forms.Select(attrs={'class': 'form-control'}),
            'subject': forms.Select(attrs={'class': 'form-control'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'module_type': forms.Select(attrs={'class': 'form-control'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 10}),
            'video_url': forms.URLInput(attrs={'class': 'form-control'}),
            'estimated_duration': forms.NumberInput(attrs={'class': 'form-control'}),
            'order': forms.NumberInput(attrs={'class': 'form-control'}),
            'prerequisites': forms.SelectMultiple(attrs={'class': 'form-control'}),
        }


class QuizForm(forms.ModelForm):
    """Form for creating/editing quizzes"""
    class Meta:
        model = Quiz
        fields = [
            'title', 'description', 'time_limit', 'max_attempts',
            'passing_score', 'difficulty', 'show_correct_answers',
            'show_results_immediately', 'randomize_questions',
            'available_from', 'available_until', 'is_active'
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'time_limit': forms.NumberInput(attrs={'class': 'form-control'}),
            'max_attempts': forms.NumberInput(attrs={'class': 'form-control'}),
            'passing_score': forms.NumberInput(attrs={'class': 'form-control'}),
            'difficulty': forms.Select(attrs={'class': 'form-control'}),
            'available_from': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'available_until': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
        }


class QuestionForm(forms.ModelForm):
    """Form for creating/editing quiz questions"""
    class Meta:
        model = Question
        fields = [
            'question_text', 'question_type', 'points', 'explanation',
            'is_required', 'order'
        ]
        widgets = {
            'question_text': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'question_type': forms.Select(attrs={'class': 'form-control'}),
            'points': forms.NumberInput(attrs={'class': 'form-control'}),
            'explanation': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'order': forms.NumberInput(attrs={'class': 'form-control'}),
        }


class QuestionOptionForm(forms.ModelForm):
    """Form for creating/editing question options"""
    class Meta:
        model = QuestionOption
        fields = ['option_text', 'is_correct', 'order']
        widgets = {
            'option_text': forms.TextInput(attrs={'class': 'form-control'}),
            'order': forms.NumberInput(attrs={'class': 'form-control'}),
        }


class AssignmentForm(forms.ModelForm):
    """Form for creating/editing assignments"""
    class Meta:
        model = LMSAssignment
        fields = [
            'course', 'subject', 'title', 'description', 'assignment_type',
            'submission_type', 'max_marks', 'word_limit', 'file_size_limit',
            'allowed_file_types', 'due_date', 'late_submission_allowed',
            'late_penalty_percentage', 'is_published', 'allow_resubmission',
            'max_resubmissions', 'instructions', 'resources'
        ]
        widgets = {
            'course': forms.Select(attrs={'class': 'form-control'}),
            'subject': forms.Select(attrs={'class': 'form-control'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'assignment_type': forms.Select(attrs={'class': 'form-control'}),
            'submission_type': forms.Select(attrs={'class': 'form-control'}),
            'max_marks': forms.NumberInput(attrs={'class': 'form-control'}),
            'word_limit': forms.NumberInput(attrs={'class': 'form-control'}),
            'file_size_limit': forms.NumberInput(attrs={'class': 'form-control'}),
            'allowed_file_types': forms.TextInput(attrs={'class': 'form-control'}),
            'due_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'late_penalty_percentage': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'max_resubmissions': forms.NumberInput(attrs={'class': 'form-control'}),
            'instructions': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'resources': forms.SelectMultiple(attrs={'class': 'form-control'}),
        }


class DiscussionForumForm(forms.ModelForm):
    """Form for creating/editing discussion forums"""
    class Meta:
        model = DiscussionForum
        fields = [
            'course', 'subject', 'title', 'description',
            'allow_student_posts', 'require_approval', 'is_active'
        ]
        widgets = {
            'course': forms.Select(attrs={'class': 'form-control'}),
            'subject': forms.Select(attrs={'class': 'form-control'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class DiscussionPostForm(forms.ModelForm):
    """Form for creating/editing discussion posts"""
    class Meta:
        model = DiscussionPost
        fields = ['title', 'content', 'is_pinned']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 6}),
        }


class CourseEnrollmentForm(forms.ModelForm):
    """Form for enrolling students in courses"""
    class Meta:
        model = CourseEnrollment
        fields = ['student', 'course', 'status']
        widgets = {
            'student': forms.Select(attrs={'class': 'form-control'}),
            'course': forms.Select(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }


class QuizAttemptForm(forms.Form):
    """Form for quiz attempts"""
    def __init__(self, *args, **kwargs):
        self.quiz = kwargs.pop('quiz', None)
        self.student = kwargs.pop('student', None)
        super().__init__(*args, **kwargs)
        
        if self.quiz:
            for question in self.quiz.questions.all():
                if question.question_type == 'multiple_choice':
                    choices = [(option.id, option.option_text) for option in question.options.all()]
                    self.fields[f'question_{question.id}'] = forms.ChoiceField(
                        choices=choices,
                        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
                        required=question.is_required,
                        label=question.question_text
                    )
                elif question.question_type == 'true_false':
                    self.fields[f'question_{question.id}'] = forms.ChoiceField(
                        choices=[(True, 'True'), (False, 'False')],
                        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
                        required=question.is_required,
                        label=question.question_text
                    )
                elif question.question_type == 'short_answer':
                    self.fields[f'question_{question.id}'] = forms.CharField(
                        widget=forms.TextInput(attrs={'class': 'form-control'}),
                        required=question.is_required,
                        label=question.question_text
                    )
                elif question.question_type == 'essay':
                    self.fields[f'question_{question.id}'] = forms.CharField(
                        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
                        required=question.is_required,
                        label=question.question_text
                    )


class AssignmentSubmissionForm(forms.ModelForm):
    """Form for assignment submissions"""
    class Meta:
        model = LMSAssignmentSubmission
        fields = ['text_content', 'file_upload']
        widgets = {
            'text_content': forms.Textarea(attrs={'class': 'form-control', 'rows': 8}),
        }


class StudentProgressForm(forms.ModelForm):
    """Form for updating student progress"""
    class Meta:
        model = StudentProgress
        fields = ['notes', 'bookmarked']
        widgets = {
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class LMSearchForm(forms.Form):
    """Search form for LMS content"""
    search_query = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Search...'})
    )
    
    content_type = forms.ChoiceField(
        choices=[
            ('', 'All Content'),
            ('module', 'Modules'),
            ('quiz', 'Quizzes'),
            ('assignment', 'Assignments'),
            ('discussion', 'Discussions'),
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    course = forms.ModelChoiceField(
        queryset=Course.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
        empty_label="All Courses"
    )
    
    subject = forms.ModelChoiceField(
        queryset=Subject.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
        empty_label="All Subjects"
    )
    
    difficulty = forms.ChoiceField(
        choices=[
            ('', 'All Levels'),
            ('easy', 'Easy'),
            ('medium', 'Medium'),
            ('hard', 'Hard'),
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )


class BulkEnrollmentForm(forms.Form):
    """Form for bulk student enrollment"""
    course = forms.ModelChoiceField(
        queryset=Course.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    students = forms.ModelMultipleChoiceField(
        queryset=Student.objects.all(),
        widget=forms.SelectMultiple(attrs={'class': 'form-control', 'size': '10'})
    )
    
    status = forms.ChoiceField(
        choices=CourseEnrollment.ENROLLMENT_STATUS_CHOICES,
        initial='enrolled',
        widget=forms.Select(attrs={'class': 'form-control'})
    )


class GradeAssignmentForm(forms.Form):
    """Form for grading assignments"""
    marks_obtained = forms.FloatField(
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'})
    )
    
    feedback = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        required=False
    )


