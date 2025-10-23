"""
Learning Management System (LMS) Models
Handles course modules, quizzes, assignments, and progress tracking
"""
from django.db import models
from django.utils import timezone
from .models import Student, Staff, Course, Subject, CustomUser


class CourseModule(models.Model):
    """Course modules/chapters"""
    MODULE_TYPE_CHOICES = (
        ('video', 'Video Lesson'),
        ('text', 'Text Content'),
        ('quiz', 'Quiz'),
        ('assignment', 'Assignment'),
        ('resource', 'Resource'),
        ('discussion', 'Discussion'),
    )
    
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='modules')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='modules')
    created_by = models.ForeignKey(Staff, on_delete=models.CASCADE, related_name='created_modules')
    
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    module_type = models.CharField(max_length=20, choices=MODULE_TYPE_CHOICES, default='text')
    order = models.IntegerField(default=1)
    
    # Content
    content = models.TextField(blank=True, help_text="Text content or instructions")
    video_url = models.URLField(blank=True, help_text="YouTube or video URL")
    attachment = models.FileField(upload_to='lms/modules/', blank=True, null=True)
    
    # Settings
    is_published = models.BooleanField(default=False)
    is_required = models.BooleanField(default=True)
    estimated_duration = models.IntegerField(default=0, help_text="Duration in minutes")
    
    # Prerequisites
    prerequisites = models.ManyToManyField('self', blank=True, symmetrical=False, related_name='dependent_modules')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['course', 'subject', 'order']
        indexes = [
            models.Index(fields=['course', 'is_published']),
            models.Index(fields=['subject', 'module_type']),
        ]
    
    def __str__(self):
        return f"{self.course.name} - {self.title}"


class Quiz(models.Model):
    """Quizzes and assessments"""
    DIFFICULTY_CHOICES = (
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard'),
    )
    
    module = models.OneToOneField(CourseModule, on_delete=models.CASCADE, related_name='quiz')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    
    # Settings
    time_limit = models.IntegerField(default=0, help_text="Time limit in minutes (0 = no limit)")
    max_attempts = models.IntegerField(default=1)
    passing_score = models.IntegerField(default=60, help_text="Passing percentage")
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES, default='medium')
    
    # Display settings
    show_correct_answers = models.BooleanField(default=True)
    show_results_immediately = models.BooleanField(default=True)
    randomize_questions = models.BooleanField(default=False)
    
    # Availability
    available_from = models.DateTimeField(null=True, blank=True)
    available_until = models.DateTimeField(null=True, blank=True)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['is_active', 'available_from']),
            models.Index(fields=['difficulty']),
        ]
    
    def __str__(self):
        return f"{self.module.title} - {self.title}"
    
    @property
    def is_available(self):
        now = timezone.now()
        if not self.is_active:
            return False
        if self.available_from and now < self.available_from:
            return False
        if self.available_until and now > self.available_until:
            return False
        return True


class Question(models.Model):
    """Quiz questions"""
    QUESTION_TYPE_CHOICES = (
        ('multiple_choice', 'Multiple Choice'),
        ('true_false', 'True/False'),
        ('short_answer', 'Short Answer'),
        ('essay', 'Essay'),
        ('fill_blank', 'Fill in the Blank'),
    )
    
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    question_text = models.TextField()
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPE_CHOICES, default='multiple_choice')
    order = models.IntegerField(default=1)
    
    # Scoring
    points = models.IntegerField(default=1)
    explanation = models.TextField(blank=True, help_text="Explanation for the correct answer")
    
    # Settings
    is_required = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['quiz', 'order']
        indexes = [
            models.Index(fields=['quiz', 'question_type']),
        ]
    
    def __str__(self):
        return f"{self.quiz.title} - Q{self.order}"


class QuestionOption(models.Model):
    """Options for multiple choice questions"""
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='options')
    option_text = models.TextField()
    is_correct = models.BooleanField(default=False)
    order = models.IntegerField(default=1)
    
    class Meta:
        ordering = ['question', 'order']
    
    def __str__(self):
        return f"{self.question.question_text[:50]} - Option {self.order}"


class QuizAttempt(models.Model):
    """Student quiz attempts"""
    STATUS_CHOICES = (
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('abandoned', 'Abandoned'),
    )
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='quiz_attempts')
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='attempts')
    
    attempt_number = models.IntegerField(default=1)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='in_progress')
    
    # Timing
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    time_taken = models.IntegerField(default=0, help_text="Time taken in seconds")
    
    # Scoring
    score = models.FloatField(default=0)
    max_score = models.FloatField(default=0)
    percentage = models.FloatField(default=0)
    passed = models.BooleanField(default=False)
    
    # Answers
    answers = models.JSONField(default=dict, blank=True, help_text="Student answers in JSON format")
    
    class Meta:
        ordering = ['-started_at']
        unique_together = ['student', 'quiz', 'attempt_number']
        indexes = [
            models.Index(fields=['student', 'quiz']),
            models.Index(fields=['status', 'started_at']),
        ]
    
    def __str__(self):
        return f"{self.student.admin.get_full_name()} - {self.quiz.title} (Attempt {self.attempt_number})"
    
    def save(self, *args, **kwargs):
        if self.max_score > 0:
            self.percentage = (self.score / self.max_score) * 100
            self.passed = self.percentage >= self.quiz.passing_score
        super().save(*args, **kwargs)


class StudentProgress(models.Model):
    """Track student progress through course modules"""
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='course_progress')
    module = models.ForeignKey(CourseModule, on_delete=models.CASCADE, related_name='student_progress')
    
    # Progress tracking
    is_started = models.BooleanField(default=False)
    is_completed = models.BooleanField(default=False)
    completion_percentage = models.FloatField(default=0)
    
    # Timing
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    last_accessed = models.DateTimeField(auto_now=True)
    time_spent = models.IntegerField(default=0, help_text="Time spent in seconds")
    
    # Notes and bookmarks
    notes = models.TextField(blank=True)
    bookmarked = models.BooleanField(default=False)
    
    class Meta:
        unique_together = ['student', 'module']
        indexes = [
            models.Index(fields=['student', 'is_completed']),
            models.Index(fields=['module', 'is_completed']),
        ]
    
    def __str__(self):
        return f"{self.student.admin.get_full_name()} - {self.module.title}"


class CourseEnrollment(models.Model):
    """Student enrollment in courses"""
    ENROLLMENT_STATUS_CHOICES = (
        ('enrolled', 'Enrolled'),
        ('completed', 'Completed'),
        ('dropped', 'Dropped'),
        ('suspended', 'Suspended'),
    )
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='course_enrollments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    enrolled_by = models.ForeignKey(Staff, on_delete=models.SET_NULL, null=True, blank=True, related_name='enrolled_students')
    
    status = models.CharField(max_length=20, choices=ENROLLMENT_STATUS_CHOICES, default='enrolled')
    enrolled_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # Progress tracking
    overall_progress = models.FloatField(default=0)
    modules_completed = models.IntegerField(default=0)
    total_modules = models.IntegerField(default=0)
    
    # Performance
    average_quiz_score = models.FloatField(default=0)
    total_time_spent = models.IntegerField(default=0, help_text="Total time in seconds")
    
    class Meta:
        unique_together = ['student', 'course']
        indexes = [
            models.Index(fields=['student', 'status']),
            models.Index(fields=['course', 'status']),
        ]
    
    def __str__(self):
        return f"{self.student.admin.get_full_name()} - {self.course.name}"
    
    def update_progress(self):
        """Update overall progress based on module completion"""
        total_modules = self.course.modules.filter(is_published=True).count()
        completed_modules = StudentProgress.objects.filter(
            student=self.student,
            module__course=self.course,
            is_completed=True
        ).count()
        
        self.total_modules = total_modules
        self.modules_completed = completed_modules
        self.overall_progress = (completed_modules / total_modules * 100) if total_modules > 0 else 0
        
        # Check if course is completed
        if self.overall_progress >= 100 and self.status == 'enrolled':
            self.status = 'completed'
            self.completed_at = timezone.now()
        
        self.save()


class DiscussionForum(models.Model):
    """Discussion forums for courses"""
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='forums')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='forums')
    created_by = models.ForeignKey(Staff, on_delete=models.CASCADE, related_name='created_forums')
    
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    
    # Settings
    is_active = models.BooleanField(default=True)
    allow_student_posts = models.BooleanField(default=True)
    require_approval = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['course', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.course.name} - {self.title}"


class DiscussionPost(models.Model):
    """Discussion forum posts"""
    forum = models.ForeignKey(DiscussionForum, on_delete=models.CASCADE, related_name='posts')
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='discussion_posts')
    parent_post = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    
    title = models.CharField(max_length=200, blank=True)
    content = models.TextField()
    
    # Status
    is_approved = models.BooleanField(default=True)
    is_pinned = models.BooleanField(default=False)
    is_locked = models.BooleanField(default=False)
    
    # Engagement
    likes = models.ManyToManyField(CustomUser, related_name='liked_posts', blank=True)
    views = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-is_pinned', '-created_at']
        indexes = [
            models.Index(fields=['forum', 'is_approved']),
            models.Index(fields=['author', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.forum.title} - {self.title or self.content[:50]}"


class LMSAssignment(models.Model):
    """Course assignments for LMS"""
    ASSIGNMENT_TYPE_CHOICES = (
        ('individual', 'Individual'),
        ('group', 'Group'),
        ('peer_review', 'Peer Review'),
    )
    
    SUBMISSION_TYPE_CHOICES = (
        ('file', 'File Upload'),
        ('text', 'Text Submission'),
        ('both', 'File and Text'),
    )
    
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='lms_assignments')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='lms_assignments')
    created_by = models.ForeignKey(Staff, on_delete=models.CASCADE, related_name='created_lms_assignments')
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    assignment_type = models.CharField(max_length=20, choices=ASSIGNMENT_TYPE_CHOICES, default='individual')
    submission_type = models.CharField(max_length=20, choices=SUBMISSION_TYPE_CHOICES, default='file')
    
    # Requirements
    max_marks = models.IntegerField(default=100)
    word_limit = models.IntegerField(default=0, help_text="Word limit for text submissions")
    file_size_limit = models.IntegerField(default=10, help_text="File size limit in MB")
    allowed_file_types = models.CharField(max_length=200, default='pdf,doc,docx', help_text="Comma-separated file extensions")
    
    # Timing
    assigned_date = models.DateTimeField(auto_now_add=True)
    due_date = models.DateTimeField()
    late_submission_allowed = models.BooleanField(default=False)
    late_penalty_percentage = models.FloatField(default=0)
    
    # Settings
    is_published = models.BooleanField(default=True)
    allow_resubmission = models.BooleanField(default=False)
    max_resubmissions = models.IntegerField(default=0)
    
    # Instructions and resources
    instructions = models.TextField(blank=True)
    resources = models.ManyToManyField(CourseModule, blank=True, related_name='lms_assignments')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-due_date']
        indexes = [
            models.Index(fields=['course', 'is_published']),
            models.Index(fields=['due_date', 'is_published']),
        ]
    
    def __str__(self):
        return f"{self.course.name} - {self.title}"
    
    @property
    def is_overdue(self):
        return timezone.now() > self.due_date


class LMSAssignmentSubmission(models.Model):
    """Student assignment submissions for LMS"""
    SUBMISSION_STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('late', 'Late'),
        ('graded', 'Graded'),
        ('returned', 'Returned'),
    )
    
    assignment = models.ForeignKey(LMSAssignment, on_delete=models.CASCADE, related_name='submissions')
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='lms_assignment_submissions')
    
    # Submission content
    text_content = models.TextField(blank=True)
    file_upload = models.FileField(upload_to='lms/assignments/', blank=True, null=True)
    
    # Status and timing
    status = models.CharField(max_length=20, choices=SUBMISSION_STATUS_CHOICES, default='draft')
    submitted_at = models.DateTimeField(null=True, blank=True)
    is_late = models.BooleanField(default=False)
    
    # Grading
    marks_obtained = models.FloatField(default=0)
    feedback = models.TextField(blank=True)
    graded_by = models.ForeignKey(Staff, on_delete=models.SET_NULL, null=True, blank=True, related_name='graded_lms_submissions')
    graded_at = models.DateTimeField(null=True, blank=True)
    
    # Version control
    submission_number = models.IntegerField(default=1)
    is_resubmission = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-submitted_at']
        unique_together = ['assignment', 'student', 'submission_number']
        indexes = [
            models.Index(fields=['assignment', 'status']),
            models.Index(fields=['student', 'submitted_at']),
        ]
    
    def __str__(self):
        return f"{self.student.admin.get_full_name()} - {self.assignment.title}"
    
    def save(self, *args, **kwargs):
        if self.submitted_at and self.assignment.due_date:
            self.is_late = self.submitted_at > self.assignment.due_date
            if self.is_late:
                self.status = 'late'
        super().save(*args, **kwargs)


