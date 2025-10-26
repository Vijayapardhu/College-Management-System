from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import UserManager
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator




class CustomUserManager(UserManager):
    def _create_user(self, email, password, **extra_fields):
        email = self.normalize_email(email)
        user = CustomUser(email=email, **extra_fields)
        user.password = make_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        assert extra_fields["is_staff"]
        assert extra_fields["is_superuser"]
        return self._create_user(email, password, **extra_fields)


class Session(models.Model):
    start_year = models.DateField()
    end_year = models.DateField()

    def __str__(self):
        return "From " + str(self.start_year) + " to " + str(self.end_year)


class CustomUser(AbstractUser):
    USER_TYPE = ((1, "HOD"), (2, "Staff"), (3, "Student"), (4, "Management"))
    GENDER = [("M", "Male"), ("F", "Female")]
    
    
    username = models.CharField(max_length=150, unique=True, null=True, blank=True, help_text="Unique ID: Roll Number, Employee ID, etc.")
    email = models.EmailField(unique=True)
    user_type = models.CharField(default=1, choices=USER_TYPE, max_length=1)
    gender = models.CharField(max_length=1, choices=GENDER, default="M")
    profile_pic = models.ImageField(upload_to='', blank=True, default='')
    address = models.TextField(default="")
    fcm_token = models.TextField(default="")  # For firebase notifications
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []
    objects = CustomUserManager()

    def __str__(self):
        return self.last_name + ", " + self.first_name


class Admin(models.Model):
    admin = models.OneToOneField(CustomUser, on_delete=models.CASCADE)


class Management(models.Model):
    """Management/Administrative Staff - Handles non-academic operations"""
    admin = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    designation = models.CharField(max_length=100, blank=True, help_text="e.g., Registrar, Finance Officer, Admin Officer")
    employee_id = models.CharField(max_length=50, unique=True, null=True, blank=True)
    department = models.CharField(max_length=100, blank=True, help_text="e.g., Finance, Administration, Facilities")
    mobile_number = models.CharField(max_length=15, blank=True)
    
    def __str__(self):
        return f"{self.admin.first_name} {self.admin.last_name} ({self.designation})"



class Department(models.Model):
    """University Departments"""
    name = models.CharField(max_length=200, unique=True)
    code = models.CharField(max_length=20, unique=True)
    hod = models.ForeignKey('Staff', on_delete=models.SET_NULL, null=True, blank=True, related_name='headed_department')
    contact_email = models.EmailField(blank=True)
    contact_number = models.CharField(max_length=15, blank=True)
    description = models.TextField(blank=True)
    established_year = models.IntegerField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.code} - {self.name}"
    
    class Meta:
        ordering = ['name']


class Program(models.Model):
    """Degree Programs (B.Tech CSE, M.Tech VLSI, etc.)"""
    PROGRAM_TYPE_CHOICES = (
        ('diploma', 'Diploma'),
        ('btech', 'B.Tech'),
        ('mtech', 'M.Tech'),
        ('phd', 'Ph.D'),
        ('mca', 'MCA'),
        ('mba', 'MBA'),
    )
    
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=20, unique=True)
    program_type = models.CharField(max_length=20, choices=PROGRAM_TYPE_CHOICES)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='programs')
    duration_years = models.IntegerField(help_text="Program duration in years")
    total_semesters = models.IntegerField()
    total_credits = models.IntegerField(default=0)
    
    eligibility_criteria = models.TextField(blank=True)
    syllabus_document = models.FileField(upload_to='program_syllabus/', blank=True, null=True)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.get_program_type_display()} - {self.name}"
    
    class Meta:
        ordering = ['program_type', 'name']
        unique_together = ('name', 'program_type', 'department')


class Course(models.Model):
    """Legacy Course model - now mapped to Program"""
    name = models.CharField(max_length=120)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Student(models.Model):
    COURSE_TYPE_CHOICES = (
        ('diploma', 'Diploma'),
        ('btech', 'B.Tech'),
        ('mtech', 'M.Tech'),
        ('phd', 'Ph.D'),
    )
    
    CATEGORY_CHOICES = (
        ('general', 'General'),
        ('obc', 'OBC'),
        ('sc', 'SC'),
        ('st', 'ST'),
        ('ews', 'EWS'),
    )
    
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('graduated', 'Graduated'),
        ('suspended', 'Suspended'),
        ('dropped', 'Dropped Out'),
        ('transferred', 'Transferred'),
    )
    
    # Basic Information (linked to CustomUser)
    admin = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    
    # Academic Information
    course = models.ForeignKey(Course, on_delete=models.DO_NOTHING, null=True, blank=False, verbose_name="Program/Branch")
    session = models.ForeignKey(Session, on_delete=models.DO_NOTHING, null=True)
    course_type = models.CharField(max_length=20, choices=COURSE_TYPE_CHOICES, default='btech')
    admission_year = models.IntegerField(null=True, blank=True)
    roll_number = models.CharField(max_length=50, unique=True, null=True, blank=True)
    admission_number = models.CharField(max_length=50, unique=True, null=True, blank=True)
    current_semester = models.IntegerField(default=1, help_text="Current semester number")
    
    # Personal Details
    date_of_birth = models.DateField(null=True, blank=True)
    nationality = models.CharField(max_length=50, default="Indian")
    religion = models.CharField(max_length=50, blank=True)
    blood_group = models.CharField(max_length=5, blank=True)
    mobile_number = models.CharField(max_length=15, blank=True)
    alternate_mobile = models.CharField(max_length=15, blank=True)
    aadhaar_number = models.CharField(max_length=12, blank=True, unique=True, null=True)
    
    # Category & Scholarship
    caste_category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='general')
    income_certificate_number = models.CharField(max_length=50, blank=True)
    annual_family_income = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    is_disabled = models.BooleanField(default=False)
    disability_percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    
    # Address
    permanent_address = models.TextField(blank=True)
    permanent_city = models.CharField(max_length=100, blank=True)
    permanent_state = models.CharField(max_length=100, blank=True)
    permanent_pincode = models.CharField(max_length=10, blank=True)
    current_address = models.TextField(blank=True)
    current_city = models.CharField(max_length=100, blank=True)
    current_state = models.CharField(max_length=100, blank=True)
    current_pincode = models.CharField(max_length=10, blank=True)
    
    # Guardian/Parent Information
    father_name = models.CharField(max_length=200, blank=True)
    father_occupation = models.CharField(max_length=100, blank=True)
    father_mobile = models.CharField(max_length=15, blank=True)
    mother_name = models.CharField(max_length=200, blank=True)
    mother_occupation = models.CharField(max_length=100, blank=True)
    mother_mobile = models.CharField(max_length=15, blank=True)
    guardian_name = models.CharField(max_length=200, blank=True)
    guardian_relation = models.CharField(max_length=50, blank=True)
    guardian_mobile = models.CharField(max_length=15, blank=True)
    
    # Academic Background
    tenth_board = models.CharField(max_length=100, blank=True, verbose_name="10th Board")
    tenth_school = models.CharField(max_length=200, blank=True, verbose_name="10th School Name")
    tenth_year = models.IntegerField(null=True, blank=True, verbose_name="10th Passing Year")
    tenth_marks_total = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    tenth_marks_obtained = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    tenth_percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    tenth_cgpa = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    
    
    # Entrance Exam Details
    entrance_exam_name = models.CharField(max_length=100, blank=True, help_text="E.g., JEE Main, EAMCET, GATE")
    entrance_exam_year = models.IntegerField(null=True, blank=True)
    entrance_exam_rank = models.IntegerField(null=True, blank=True)
    entrance_exam_score = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    entrance_category_rank = models.IntegerField(null=True, blank=True)
    
    # Document Upload Paths
    photo = models.ImageField(upload_to='student_photos/', blank=True, null=True)
    signature = models.ImageField(upload_to='student_signatures/', blank=True, null=True)
    tenth_certificate = models.FileField(upload_to='certificates/10th/', blank=True, null=True)
    transfer_certificate = models.FileField(upload_to='certificates/tc/', blank=True, null=True)
    migration_certificate = models.FileField(upload_to='certificates/migration/', blank=True, null=True)
    character_certificate = models.FileField(upload_to='certificates/character/', blank=True, null=True)
    caste_certificate = models.FileField(upload_to='certificates/caste/', blank=True, null=True)
    income_certificate = models.FileField(upload_to='certificates/income/', blank=True, null=True)
    disability_certificate = models.FileField(upload_to='certificates/disability/', blank=True, null=True)
    
    # Additional Required Documents
    aadhaar_card = models.FileField(upload_to='documents/aadhaar/', blank=True, null=True)
    bank_passbook = models.FileField(upload_to='documents/bank_passbook/', blank=True, null=True)
    birth_certificate = models.FileField(upload_to='documents/birth/', blank=True, null=True)
    entrance_exam_scorecard = models.FileField(upload_to='documents/entrance/', blank=True, null=True)
    
    # Status & Graduation
    student_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    date_of_graduation = models.DateField(null=True, blank=True)
    graduation_cgpa = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    
    # Additional Info
    hostel_required = models.BooleanField(default=False)
    transport_required = models.BooleanField(default=False)
    scholarship_applied = models.BooleanField(default=False)
    scholarship_name = models.CharField(max_length=200, blank=True)
    bank_account_number = models.CharField(max_length=50, blank=True)
    bank_ifsc_code = models.CharField(max_length=20, blank=True)
    bank_name = models.CharField(max_length=100, blank=True)
    
    # Additional Required Fields for College Enrollment
    
    # Medical Information
    medical_conditions = models.TextField(blank=True, help_text="Any medical conditions or allergies")
    
    # Language Proficiency
    mother_tongue = models.CharField(max_length=50, blank=True)
    
    # Extracurricular Activities
    hobbies = models.TextField(blank=True)
    achievements = models.TextField(blank=True, help_text="Academic and extracurricular achievements")
    
    # Admission Specific
    admission_mode = models.CharField(max_length=20, choices=[('Direct', 'Direct'), ('Merit', 'Merit'), ('Management', 'Management'), ('NRI', 'NRI'), ('Sports', 'Sports'), ('Cultural', 'Cultural')], default='Merit')
    admission_quota = models.CharField(max_length=20, choices=[('General', 'General'), ('SC', 'SC'), ('ST', 'ST'), ('OBC', 'OBC'), ('EWS', 'EWS'), ('PH', 'PH'), ('NRI', 'NRI')], default='General')
    admission_fee_paid = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    admission_date = models.DateField(null=True, blank=True)
    
    # Verification Status
    documents_verified = models.BooleanField(default=False)
    fee_paid = models.BooleanField(default=False)
    library_card_issued = models.BooleanField(default=False)
    id_card_issued = models.BooleanField(default=False)
    
    # Emergency Contact
    emergency_contact_name = models.CharField(max_length=200, blank=True)
    emergency_contact_relation = models.CharField(max_length=50, blank=True)
    emergency_contact_mobile = models.CharField(max_length=15, blank=True)
    
    # Remarks & Notes
    remarks = models.TextField(blank=True)
    
    def __str__(self):
        return self.admin.last_name + ", " + self.admin.first_name
    
    class Meta:
        indexes = [
            models.Index(fields=['roll_number'], name='student_roll_number_idx'),
            models.Index(fields=['admission_number'], name='student_admission_number_idx'),
            models.Index(fields=['course', 'session'], name='student_course_session_idx'),
            models.Index(fields=['admission_year'], name='student_admission_year_idx'),
            models.Index(fields=['current_semester'], name='student_current_semester_idx'),
            models.Index(fields=['mobile_number'], name='student_mobile_number_idx'),
            models.Index(fields=['aadhaar_number'], name='student_aadhaar_number_idx'),
            models.Index(fields=['student_status'], name='student_status_idx'),
        ]
    
    @property
    def full_name(self):
        return f"{self.admin.first_name} {self.admin.last_name}"
    
    @property
    def age(self):
        if self.date_of_birth:
            from datetime import date
            today = date.today()
            return today.year - self.date_of_birth.year - ((today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))
        return None
    


class Staff(models.Model):
    """Faculty/Staff Members"""
    DESIGNATION_CHOICES = (
        ('professor', 'Professor'),
        ('associate_professor', 'Associate Professor'),
        ('assistant_professor', 'Assistant Professor'),
        ('lecturer', 'Lecturer'),
        ('lab_assistant', 'Lab Assistant'),
        ('hod', 'Head of Department'),
        ('dean', 'Dean'),
        ('principal', 'Principal'),
        ('librarian', 'Librarian'),
        ('accountant', 'Accountant'),
        ('admin_staff', 'Administrative Staff'),
    )
    
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('on_leave', 'On Leave'),
        ('retired', 'Retired'),
        ('resigned', 'Resigned'),
        ('terminated', 'Terminated'),
    )
    
    admin = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    
    # Legacy field for backward compatibility
    course = models.ForeignKey(Course, on_delete=models.DO_NOTHING, null=True, blank=True)
    
    # New department mapping
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True, related_name='staff_members')
    
    # Professional Information
    designation = models.CharField(max_length=50, choices=DESIGNATION_CHOICES, default='assistant_professor')
    employee_id = models.CharField(max_length=50, unique=True, null=True, blank=True)
    qualification = models.CharField(max_length=200, blank=True, help_text="e.g., Ph.D in Computer Science")
    specialization = models.CharField(max_length=200, blank=True)
    experience_years = models.IntegerField(default=0)
    
    # Contact Information
    mobile_number = models.CharField(max_length=15, blank=True)
    alternate_mobile = models.CharField(max_length=15, blank=True)
    emergency_contact = models.CharField(max_length=15, blank=True)
    
    # Date Information
    date_of_birth = models.DateField(null=True, blank=True)
    date_of_joining = models.DateField(null=True, blank=True)
    date_of_retirement = models.DateField(null=True, blank=True)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    
    # Documents
    photo = models.ImageField(upload_to='staff_photos/', blank=True, null=True)
    resume = models.FileField(upload_to='staff_resumes/', blank=True, null=True)
    
    # Proctor flag
    is_proctor = models.BooleanField(default=False, help_text="Enable proctor features for this staff")
    
    # Permissions
    can_approve_events = models.BooleanField(default=False)
    can_manage_library = models.BooleanField(default=False)
    can_manage_exam = models.BooleanField(default=False)
    can_manage_placement = models.BooleanField(default=False)
    
    # Additional Info
    blood_group = models.CharField(max_length=5, blank=True)
    aadhaar_number = models.CharField(max_length=12, blank=True, unique=True, null=True)
    
    # Bank Details
    bank_account_number = models.CharField(max_length=50, blank=True)
    bank_ifsc_code = models.CharField(max_length=20, blank=True)
    bank_name = models.CharField(max_length=100, blank=True)
    
    remarks = models.TextField(blank=True)

    def __str__(self):
        return self.admin.last_name + " " + self.admin.first_name
    
    class Meta:
        indexes = [
            models.Index(fields=['employee_id'], name='staff_employee_id_idx'),
            models.Index(fields=['department'], name='staff_department_idx'),
            models.Index(fields=['designation'], name='staff_designation_idx'),
            models.Index(fields=['mobile_number'], name='staff_mobile_number_idx'),
            models.Index(fields=['aadhaar_number'], name='staff_aadhaar_number_idx'),
            models.Index(fields=['date_of_joining'], name='staff_joining_date_idx'),
        ]
    
    @property
    def full_name(self):
        return f"{self.admin.first_name} {self.admin.last_name}"
    
    @property
    def designation_display(self):
        return self.get_designation_display()


class Subject(models.Model):
    name = models.CharField(max_length=120)
    staff = models.ForeignKey(Staff,on_delete=models.CASCADE,)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Attendance(models.Model):
    session = models.ForeignKey(Session, on_delete=models.DO_NOTHING)
    subject = models.ForeignKey(Subject, on_delete=models.DO_NOTHING)
    date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['date'], name='attendance_date_idx'),
            models.Index(fields=['subject', 'date'], name='attendance_subject_date_idx'),
            models.Index(fields=['session', 'date'], name='attendance_session_date_idx'),
            models.Index(fields=['created_at'], name='attendance_created_at_idx'),
        ]
        unique_together = ['subject', 'date', 'session']


class AttendanceReport(models.Model):
    student = models.ForeignKey(Student, on_delete=models.DO_NOTHING)
    attendance = models.ForeignKey(Attendance, on_delete=models.CASCADE)
    status = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class LeaveReportStudent(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    date = models.CharField(max_length=60)
    message = models.TextField()
    status = models.SmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class LeaveReportStaff(models.Model):
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE)
    date = models.CharField(max_length=60)
    message = models.TextField()
    status = models.SmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class FeedbackStudent(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    feedback = models.TextField()
    reply = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class FeedbackStaff(models.Model):
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE)
    feedback = models.TextField()
    reply = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class NotificationStaff(models.Model):
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class NotificationStudent(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class StudentResult(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    test = models.FloatField(default=0)
    exam = models.FloatField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class ProctorAssignment(models.Model):
    """Links staff (acting as proctors) to their assigned students"""
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE, related_name='mentee_students', limit_choices_to={'is_proctor': True})
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='assigned_proctors')
    assigned_date = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ('staff', 'student')
        verbose_name = "Proctor Assignment"
        verbose_name_plural = "Proctor Assignments"
    
    def __str__(self):
        return f"{self.staff} → {self.student}"


class Event(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('completed', 'Completed'),
    )
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    event_date = models.DateTimeField()
    venue = models.CharField(max_length=200)
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='events_created')
    approved_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='events_approved')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    course = models.ForeignKey(Course, on_delete=models.SET_NULL, null=True, blank=True)
    max_participants = models.IntegerField(default=0, help_text="0 means unlimited")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.title
    
    @property
    def participant_count(self):
        return self.participants.count()


class EventParticipation(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='participants')
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='event_participations')
    registered_at = models.DateTimeField(auto_now_add=True)
    attended = models.BooleanField(default=False)
    
    class Meta:
        unique_together = ('event', 'student')
    
    def __str__(self):
        return f"{self.student} - {self.event.title}"


class Message(models.Model):
    sender = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='received_messages')
    subject = models.CharField(max_length=200)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    parent_message = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='replies')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.sender} to {self.receiver}: {self.subject}"


class StudyMaterial(models.Model):
    MATERIAL_TYPE = (
        ('document', 'Document'),
        ('link', 'Reference Link'),
        ('video', 'Video/YouTube'),
    )
    
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    material_type = models.CharField(max_length=20, choices=MATERIAL_TYPE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='materials')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='materials')
    uploaded_by = models.ForeignKey(Staff, on_delete=models.CASCADE, related_name='uploaded_materials')
    
    # For documents
    file = models.FileField(upload_to='study_materials/', blank=True, null=True)
    
    # For links and videos
    url = models.URLField(blank=True, null=True, help_text="For reference links or YouTube URLs")
    
    # Version control
    version = models.CharField(max_length=10, default='1.0')
    is_archived = models.BooleanField(default=False)
    replaces = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='replaced_by')
    
    # Metadata
    tags = models.CharField(max_length=200, blank=True, help_text="Comma-separated tags")
    download_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Study Material"
        verbose_name_plural = "Study Materials"
    
    def __str__(self):
        return f"{self.title} - {self.subject.name}"
    
    @property
    def average_rating(self):
        ratings = self.ratings.aggregate(avg=models.Avg('rating'))
        return round(ratings['avg'], 2) if ratings['avg'] else 0


class ResourceRating(models.Model):
    material = models.ForeignKey(StudyMaterial, on_delete=models.CASCADE, related_name='ratings')
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])  # 1-5 stars
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('material', 'student')
    
    def __str__(self):
        return f"{self.student} rated {self.material.title}: {self.rating}/5"


class ResourceBookmark(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='bookmarks')
    material = models.ForeignKey(StudyMaterial, on_delete=models.CASCADE, related_name='bookmarked_by')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('student', 'material')
    
    def __str__(self):
        return f"{self.student} bookmarked {self.material.title}"


class ResourceDownloadLog(models.Model):
    material = models.ForeignKey(StudyMaterial, on_delete=models.CASCADE, related_name='download_logs')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    downloaded_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.user} downloaded {self.material.title}"


class Assignment(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='assignments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='assignments')
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE, related_name='created_assignments')
    
    # Files
    attachment = models.FileField(upload_to='assignments/', blank=True, null=True)
    
    # Deadlines
    assigned_date = models.DateTimeField(auto_now_add=True)
    due_date = models.DateTimeField()
    max_marks = models.IntegerField(default=100)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-due_date']
    
    def __str__(self):
        return f"{self.title} - {self.subject.name}"
    
    @property
    def is_overdue(self):
        from django.utils import timezone
        return timezone.now() > self.due_date


class AssignmentSubmission(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('submitted', 'Submitted'),
        ('graded', 'Graded'),
        ('late', 'Late Submission'),
    )
    
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='submissions')
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='assignment_submissions')
    submission_file = models.FileField(upload_to='assignment_submissions/')
    remarks = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Grading
    marks_obtained = models.FloatField(null=True, blank=True)
    feedback = models.TextField(blank=True)
    graded_by = models.ForeignKey(Staff, on_delete=models.SET_NULL, null=True, blank=True, related_name='graded_submissions')
    graded_at = models.DateTimeField(null=True, blank=True)
    
    submitted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('assignment', 'student')
        ordering = ['-submitted_at']
    
    def __str__(self):
        return f"{self.student} - {self.assignment.title}"
    
    def save(self, *args, **kwargs):
        # Auto-detect late submission
        if self.submitted_at and self.assignment.due_date and self.submitted_at > self.assignment.due_date:
            self.status = 'late'
        elif self.marks_obtained is not None:
            self.status = 'graded'
        elif self.submission_file:
            self.status = 'submitted'
        super().save(*args, **kwargs)


class Announcement(models.Model):
    PRIORITY_CHOICES = (
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    )
    
    TARGET_AUDIENCE = (
        ('all', 'Everyone'),
        ('staff', 'Staff Only'),
        ('students', 'Students Only'),
        ('course', 'Specific Course'),
    )
    
    title = models.CharField(max_length=200)
    message = models.TextField()
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    target_audience = models.CharField(max_length=20, choices=TARGET_AUDIENCE, default='all')
    course = models.ForeignKey(Course, on_delete=models.SET_NULL, null=True, blank=True, help_text="Required if target is specific course")
    
    posted_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='announcements')
    attachment = models.FileField(upload_to='announcements/', blank=True, null=True)
    
    is_active = models.BooleanField(default=True)
    expires_at = models.DateTimeField(null=True, blank=True, help_text="Optional expiry date")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title


class Discussion(models.Model):
    """Discussion forum for study materials or general topics"""
    title = models.CharField(max_length=200)
    content = models.TextField()
    material = models.ForeignKey(StudyMaterial, on_delete=models.CASCADE, null=True, blank=True, related_name='discussions')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='discussions')
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='discussions')
    
    is_pinned = models.BooleanField(default=False)
    is_locked = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-is_pinned', '-updated_at']
    
    def __str__(self):
        return self.title


class DiscussionReply(models.Model):
    discussion = models.ForeignKey(Discussion, on_delete=models.CASCADE, related_name='replies')
    content = models.TextField()
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='discussion_replies')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['created_at']
        verbose_name_plural = "Discussion Replies"
    
    def __str__(self):
        return f"Reply by {self.created_by} on {self.discussion.title}"


class Hostel(models.Model):
    """Hostel/Dormitory Management"""
    name = models.CharField(max_length=100)
    hostel_type = models.CharField(max_length=10, choices=(('boys', 'Boys'), ('girls', 'Girls')))
    warden_name = models.CharField(max_length=200)
    warden_contact = models.CharField(max_length=15)
    total_rooms = models.IntegerField()
    occupied_rooms = models.IntegerField(default=0)
    address = models.TextField()
    
    def __str__(self):
        return f"{self.name} ({self.hostel_type})"
    
    @property
    def available_rooms(self):
        return self.total_rooms - self.occupied_rooms


class HostelAllocation(models.Model):
    """Student Hostel Room Allocation"""
    student = models.OneToOneField(Student, on_delete=models.CASCADE, related_name='hostel_allocation')
    hostel = models.ForeignKey(Hostel, on_delete=models.CASCADE, related_name='allocations')
    room_number = models.CharField(max_length=20)
    allocated_date = models.DateField(auto_now_add=True)
    rent_per_semester = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.student} - {self.hostel.name} Room {self.room_number}"


class Transport(models.Model):
    """University Transport/Bus Routes"""
    route_name = models.CharField(max_length=100)
    bus_number = models.CharField(max_length=20)
    driver_name = models.CharField(max_length=200)
    driver_contact = models.CharField(max_length=15)
    route_details = models.TextField(help_text="Stops and timings")
    fee_per_semester = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_seats = models.IntegerField(default=40)
    occupied_seats = models.IntegerField(default=0)
    
    def __str__(self):
        return f"{self.route_name} - {self.bus_number}"
    
    @property
    def available_seats(self):
        return self.total_seats - self.occupied_seats


class TransportAllocation(models.Model):
    """Student Transport Registration"""
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='transport_allocation')
    transport = models.ForeignKey(Transport, on_delete=models.CASCADE, related_name='allocations')
    pickup_point = models.CharField(max_length=200)
    registered_date = models.DateField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ('student', 'transport')
    
    def __str__(self):
        return f"{self.student} - {self.transport.route_name}"


class FeeStructure(models.Model):
    """Fee Structure for Different Programs"""
    SEMESTER_CHOICES = [(i, f"Semester {i}") for i in range(1, 11)]
    
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='fee_structures')
    course_type = models.CharField(max_length=20, choices=Student.COURSE_TYPE_CHOICES)
    semester = models.IntegerField(choices=SEMESTER_CHOICES)
    session = models.ForeignKey(Session, on_delete=models.CASCADE, related_name='fee_structures')
    
    tuition_fee = models.DecimalField(max_digits=10, decimal_places=2)
    development_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    lab_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    library_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    exam_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    other_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    class Meta:
        unique_together = ('course', 'course_type', 'semester', 'session')
        verbose_name = "Fee Structure"
        verbose_name_plural = "Fee Structures"
    
    def __str__(self):
        return f"{self.course.name} - {self.get_course_type_display()} - Sem {self.semester}"
    
    @property
    def total_fee(self):
        return (self.tuition_fee + self.development_fee + self.lab_fee + 
                self.library_fee + self.exam_fee + self.other_fee)


class FeePayment(models.Model):
    """Student Fee Payment Records"""
    PAYMENT_STATUS = (
        ('pending', 'Pending'),
        ('partial', 'Partial'),
        ('paid', 'Paid'),
        ('overdue', 'Overdue'),
    )
    
    PAYMENT_METHOD = (
        ('cash', 'Cash'),
        ('cheque', 'Cheque'),
        ('dd', 'Demand Draft'),
        ('online', 'Online/UPI'),
        ('card', 'Credit/Debit Card'),
    )
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='fee_payments')
    fee_structure = models.ForeignKey(FeeStructure, on_delete=models.CASCADE, related_name='payments')
    
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateField()
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD, default='online')
    transaction_id = models.CharField(max_length=100, blank=True)
    payment_gateway = models.CharField(max_length=50, blank=True, help_text="Razorpay, PayU, etc.")
    receipt_number = models.CharField(max_length=50, unique=True)
    payment_proof = models.FileField(upload_to='payment_proofs/%Y/%m/%d/', blank=True, null=True)
    
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='pending')
    remarks = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-payment_date']
        indexes = [
            models.Index(fields=['payment_date'], name='fee_payment_date_idx'),
            models.Index(fields=['student', 'payment_date'], name='fee_payment_student_date_idx'),
            models.Index(fields=['status'], name='fee_payment_status_idx'),
            models.Index(fields=['receipt_number'], name='fee_payment_receipt_idx'),
            models.Index(fields=['created_at'], name='fee_payment_created_at_idx'),
        ]
    
    def __str__(self):
        return f"{self.student} - {self.receipt_number}"
    
    def get_payment_status_display_color(self):
        """Return color class for payment status"""
        colors = {
            'pending': 'warning',
            'partial': 'info',
            'paid': 'success',
            'overdue': 'danger',
        }
        return colors.get(self.status, 'secondary')
    
    def is_online_payment(self):
        """Check if payment was made online"""
        return self.payment_method in ['online', 'card']


class FeeReminder(models.Model):
    """Automated fee reminder system"""
    REMINDER_TYPE = (
        ('email', 'Email'),
        ('sms', 'SMS'),
        ('both', 'Email & SMS'),
    )
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='fee_reminders')
    fee_structure = models.ForeignKey(FeeStructure, on_delete=models.CASCADE)
    reminder_date = models.DateTimeField()
    reminder_type = models.CharField(max_length=10, choices=REMINDER_TYPE, default='email')
    sent_status = models.BooleanField(default=False)
    sent_date = models.DateTimeField(null=True, blank=True)
    message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Reminder for {self.student} - {self.reminder_date.strftime('%Y-%m-%d')}"
    
    class Meta:
        ordering = ['-reminder_date']


class FeeConcession(models.Model):
    """Fee discounts and scholarships"""
    CONCESSION_TYPE = (
        ('scholarship', 'Scholarship'),
        ('merit', 'Merit Based'),
        ('need', 'Need Based'),
        ('sports', 'Sports'),
        ('cultural', 'Cultural'),
        ('other', 'Other'),
    )
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='fee_concessions')
    concession_type = models.CharField(max_length=20, choices=CONCESSION_TYPE)
    amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    reason = models.TextField()
    approved_by = models.ForeignKey(Staff, on_delete=models.SET_NULL, null=True, blank=True)
    approval_date = models.DateTimeField(null=True, blank=True)
    is_approved = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.student} - {self.get_concession_type_display()}"
    
    class Meta:
        ordering = ['-created_at']


class FeeInstallment(models.Model):
    """Split fee payments into installments"""
    INSTALLMENT_STATUS = (
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('overdue', 'Overdue'),
        ('cancelled', 'Cancelled'),
    )
    
    fee_structure = models.ForeignKey(FeeStructure, on_delete=models.CASCADE, related_name='installments')
    installment_number = models.PositiveIntegerField()
    due_date = models.DateField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=INSTALLMENT_STATUS, default='pending')
    paid_date = models.DateField(null=True, blank=True)
    payment_reference = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Installment {self.installment_number} - {self.fee_structure}"
    
    class Meta:
        ordering = ['installment_number']
        unique_together = ['fee_structure', 'installment_number']


class Scholarship(models.Model):
    """Scholarship Programs"""
    SCHOLARSHIP_TYPE = (
        ('merit', 'Merit Based'),
        ('need', 'Need Based'),
        ('sports', 'Sports'),
        ('minority', 'Minority'),
        ('govt', 'Government'),
        ('private', 'Private'),
    )
    
    name = models.CharField(max_length=200)
    scholarship_type = models.CharField(max_length=20, choices=SCHOLARSHIP_TYPE)
    description = models.TextField()
    eligibility_criteria = models.TextField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    max_recipients = models.IntegerField()
    application_deadline = models.DateField()
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.name


class ScholarshipApplication(models.Model):
    """Student Scholarship Applications"""
    APPLICATION_STATUS = (
        ('applied', 'Applied'),
        ('under_review', 'Under Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('disbursed', 'Disbursed'),
    )
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='scholarship_applications')
    scholarship = models.ForeignKey(Scholarship, on_delete=models.CASCADE, related_name='applications')
    application_date = models.DateField(auto_now_add=True)
    
    reason = models.TextField(help_text="Why you deserve this scholarship")
    supporting_documents = models.FileField(upload_to='scholarship_docs/', blank=True, null=True)
    
    status = models.CharField(max_length=20, choices=APPLICATION_STATUS, default='applied')
    reviewed_by = models.ForeignKey(Staff, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_scholarships')
    review_remarks = models.TextField(blank=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    
    disbursement_date = models.DateField(null=True, blank=True)
    disbursement_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    class Meta:
        ordering = ['-application_date']
    
    def __str__(self):
        return f"{self.student} - {self.scholarship.name}"


class SemesterResult(models.Model):
    """Semester-wise Student Results"""
    SEMESTER_CHOICES = [(i, f"Semester {i}") for i in range(1, 11)]
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='semester_results')
    session = models.ForeignKey(Session, on_delete=models.CASCADE, related_name='semester_results')
    semester = models.IntegerField(choices=SEMESTER_CHOICES)
    
    total_credits = models.IntegerField(default=0)
    credits_earned = models.IntegerField(default=0)
    sgpa = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True, verbose_name="SGPA")
    cgpa = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True, verbose_name="CGPA")
    
    total_marks = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    marks_obtained = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    
    has_backlogs = models.BooleanField(default=False)
    number_of_backlogs = models.IntegerField(default=0)
    
    is_published = models.BooleanField(default=False)
    published_date = models.DateTimeField(null=True, blank=True)
    
    remarks = models.TextField(blank=True)
    
    class Meta:
        unique_together = ('student', 'session', 'semester')
        ordering = ['student', 'semester']
    
    def __str__(self):
        return f"{self.student} - Sem {self.semester} - SGPA: {self.sgpa}"


class SubjectResult(models.Model):
    """Subject-wise marks for students"""
    GRADE_CHOICES = (
        ('O', 'O (Outstanding)'),
        ('A+', 'A+ (Excellent)'),
        ('A', 'A (Very Good)'),
        ('B+', 'B+ (Good)'),
        ('B', 'B (Above Average)'),
        ('C', 'C (Average)'),
        ('P', 'P (Pass)'),
        ('F', 'F (Fail)'),
        ('AB', 'AB (Absent)'),
    )
    
    semester_result = models.ForeignKey(SemesterResult, on_delete=models.CASCADE, related_name='subject_results')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='subject_results')
    
    internal_marks = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    external_marks = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    total_marks = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    max_marks = models.DecimalField(max_digits=5, decimal_places=2, default=100)
    
    grade = models.CharField(max_length=5, choices=GRADE_CHOICES, blank=True)
    credits = models.IntegerField(default=3)
    is_pass = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ('semester_result', 'subject')
    
    def __str__(self):
        return f"{self.semester_result.student} - {self.subject.name} - {self.total_marks}"
    
    def save(self, *args, **kwargs):
        self.total_marks = self.internal_marks + self.external_marks
        # Auto-determine pass/fail (passing marks = 40%)
        self.is_pass = self.total_marks >= (self.max_marks * 0.4)
        super().save(*args, **kwargs)


class Library(models.Model):
    """Library Book Management"""
    BOOK_CATEGORY = (
        ('textbook', 'Text Book'),
        ('reference', 'Reference Book'),
        ('journal', 'Journal'),
        ('magazine', 'Magazine'),
        ('ebook', 'E-Book'),
    )
    
    title = models.CharField(max_length=300)
    author = models.CharField(max_length=200)
    isbn = models.CharField(max_length=20, unique=True, blank=True, null=True)
    publisher = models.CharField(max_length=200)
    published_year = models.IntegerField()
    category = models.CharField(max_length=20, choices=BOOK_CATEGORY)
    subject = models.ForeignKey(Subject, on_delete=models.SET_NULL, null=True, blank=True, related_name='library_books')
    
    total_copies = models.IntegerField(default=1)
    available_copies = models.IntegerField(default=1)
    
    shelf_number = models.CharField(max_length=50, blank=True)
    description = models.TextField(blank=True)
    cover_image = models.ImageField(upload_to='library/covers/', blank=True, null=True)
    
    def __str__(self):
        return f"{self.title} by {self.author}"
    
    @property
    def is_available(self):
        return self.available_copies > 0


class LibraryIssue(models.Model):
    """Book Issue/Return Tracking"""
    STATUS_CHOICES = (
        ('issued', 'Issued'),
        ('returned', 'Returned'),
        ('overdue', 'Overdue'),
        ('lost', 'Lost'),
    )
    
    book = models.ForeignKey(Library, on_delete=models.CASCADE, related_name='issues')
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='library_issues')
    
    issue_date = models.DateField(auto_now_add=True)
    due_date = models.DateField()
    return_date = models.DateField(null=True, blank=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='issued')
    fine_amount = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    remarks = models.TextField(blank=True)
    
    issued_by = models.ForeignKey(Staff, on_delete=models.SET_NULL, null=True, related_name='library_issues')
    
    class Meta:
        ordering = ['-issue_date']
    
    def __str__(self):
        return f"{self.book.title} - {self.student}"


class Exam(models.Model):
    """Examination Management"""
    EXAM_TYPE_CHOICES = (
        ('mid_term', 'Mid Term'),
        ('end_term', 'End Term / Final'),
        ('internal', 'Internal Assessment'),
        ('practical', 'Practical Exam'),
        ('viva', 'Viva Voce'),
        ('quiz', 'Quiz'),
    )
    
    name = models.CharField(max_length=200)
    exam_type = models.CharField(max_length=20, choices=EXAM_TYPE_CHOICES)
    session = models.ForeignKey(Session, on_delete=models.CASCADE, related_name='exams')
    semester = models.IntegerField(choices=SemesterResult.SEMESTER_CHOICES)
    
    start_date = models.DateField()
    end_date = models.DateField()
    
    created_by = models.ForeignKey(Staff, on_delete=models.SET_NULL, null=True, related_name='created_exams')
    is_published = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} - {self.session}"
    
    class Meta:
        ordering = ['-start_date']
        indexes = [
            models.Index(fields=['exam_type'], name='exam_type_idx'),
            models.Index(fields=['session', 'semester'], name='exam_session_semester_idx'),
            models.Index(fields=['start_date'], name='exam_start_date_idx'),
            models.Index(fields=['end_date'], name='exam_end_date_idx'),
            models.Index(fields=['is_published'], name='exam_published_idx'),
            models.Index(fields=['created_at'], name='exam_created_at_idx'),
        ]


class ExamSchedule(models.Model):
    """Individual Exam Time Table"""
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='schedules')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='exam_schedules')
    
    exam_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    room_number = models.CharField(max_length=50)
    max_marks = models.IntegerField(default=100)
    
    question_paper = models.FileField(upload_to='question_papers/', blank=True, null=True)
    answer_key = models.FileField(upload_to='answer_keys/', blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.exam.name} - {self.subject.name} on {self.exam_date}"
    
    class Meta:
        ordering = ['exam_date', 'start_time']
        unique_together = ('exam', 'subject')


class Invigilator(models.Model):
    """Exam Invigilator Assignment"""
    exam_schedule = models.ForeignKey(ExamSchedule, on_delete=models.CASCADE, related_name='invigilators')
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE, related_name='invigilation_duties')
    duty_type = models.CharField(max_length=20, choices=(('chief', 'Chief Invigilator'), ('assistant', 'Assistant')), default='assistant')
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.staff} - {self.exam_schedule}"
    
    class Meta:
        unique_together = ('exam_schedule', 'staff')


class AdmitCard(models.Model):
    """Exam Admit Cards"""
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='admit_cards')
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='admit_cards')
    
    admit_card_number = models.CharField(max_length=50, unique=True)
    is_generated = models.BooleanField(default=False)
    is_downloaded = models.BooleanField(default=False)
    downloaded_at = models.DateTimeField(null=True, blank=True)
    
    remarks = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.admit_card_number} - {self.student}"
    
    class Meta:
        unique_together = ('exam', 'student')


class Timetable(models.Model):
    """Weekly Timetable/Class Schedule"""
    WEEKDAY_CHOICES = (
        ('monday', 'Monday'),
        ('tuesday', 'Tuesday'),
        ('wednesday', 'Wednesday'),
        ('thursday', 'Thursday'),
        ('friday', 'Friday'),
        ('saturday', 'Saturday'),
    )
    
    PERIOD_CHOICES = (
        ('1', 'Period 1'),
        ('2', 'Period 2'),
        ('3', 'Period 3'),
        ('4', 'Period 4'),
        ('5', 'Period 5'),
        ('6', 'Period 6'),
        ('7', 'Period 7'),
        ('8', 'Period 8'),
    )
    
    session = models.ForeignKey(Session, on_delete=models.CASCADE, related_name='timetables')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='timetables')
    semester = models.IntegerField(choices=SemesterResult.SEMESTER_CHOICES)
    
    weekday = models.CharField(max_length=20, choices=WEEKDAY_CHOICES)
    period = models.CharField(max_length=5, choices=PERIOD_CHOICES)
    start_time = models.TimeField()
    end_time = models.TimeField()
    
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='timetable_slots')
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE, related_name='timetable_slots')
    room_number = models.CharField(max_length=50, blank=True)
    
    is_lab = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.course} - Sem {self.semester} - {self.weekday} P{self.period}"
    
    class Meta:
        ordering = ['weekday', 'period']
        unique_together = ('session', 'course', 'semester', 'weekday', 'period')


class Company(models.Model):
    """Companies for Placement"""
    COMPANY_TYPE_CHOICES = (
        ('product', 'Product Based'),
        ('service', 'Service Based'),
        ('startup', 'Startup'),
        ('mnc', 'MNC'),
        ('psu', 'PSU'),
        ('government', 'Government'),
    )
    
    name = models.CharField(max_length=200)
    company_type = models.CharField(max_length=20, choices=COMPANY_TYPE_CHOICES)
    website = models.URLField(blank=True)
    description = models.TextField(blank=True)
    
    hr_name = models.CharField(max_length=200, blank=True)
    hr_email = models.EmailField(blank=True)
    hr_contact = models.CharField(max_length=15, blank=True)
    
    address = models.TextField(blank=True)
    logo = models.ImageField(upload_to='company_logos/', blank=True, null=True)
    
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "Companies"
        ordering = ['name']


class PlacementDrive(models.Model):
    """Placement/Recruitment Drives"""
    DRIVE_TYPE_CHOICES = (
        ('campus', 'On Campus'),
        ('off_campus', 'Off Campus'),
        ('pool', 'Pool Campus'),
        ('virtual', 'Virtual'),
    )
    
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='placement_drives')
    session = models.ForeignKey(Session, on_delete=models.CASCADE, related_name='placement_drives')
    
    drive_type = models.CharField(max_length=20, choices=DRIVE_TYPE_CHOICES, default='campus')
    job_title = models.CharField(max_length=200)
    job_description = models.TextField()
    
    # Eligibility
    eligible_courses = models.ManyToManyField(Course, related_name='placement_drives')
    min_cgpa = models.DecimalField(max_digits=4, decimal_places=2, default=0)
    allowed_backlogs = models.IntegerField(default=0)
    
    # Package Details
    salary_package = models.DecimalField(max_digits=10, decimal_places=2, help_text="in LPA")
    bond_years = models.IntegerField(default=0, help_text="Service bond in years")
    
    # Important Dates
    registration_deadline = models.DateTimeField()
    aptitude_test_date = models.DateTimeField(null=True, blank=True)
    interview_date = models.DateTimeField(null=True, blank=True)
    
    # Selection Process
    selection_process = models.TextField(help_text="e.g., Aptitude -> Technical -> HR")
    number_of_openings = models.IntegerField(default=1)
    
    # Attachments
    jd_document = models.FileField(upload_to='placement/jds/', blank=True, null=True, verbose_name="Job Description Document")
    
    # Status
    is_active = models.BooleanField(default=True)
    
    # Managed by
    coordinator = models.ForeignKey(Staff, on_delete=models.SET_NULL, null=True, related_name='managed_placements')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.company.name} - {self.job_title}"
    
    class Meta:
        ordering = ['-created_at']


class PlacementApplication(models.Model):
    """Student Applications for Placements"""
    APPLICATION_STATUS_CHOICES = (
        ('registered', 'Registered'),
        ('shortlisted', 'Shortlisted'),
        ('aptitude_cleared', 'Aptitude Cleared'),
        ('technical_cleared', 'Technical Round Cleared'),
        ('hr_cleared', 'HR Round Cleared'),
        ('selected', 'Selected'),
        ('rejected', 'Rejected'),
        ('offer_accepted', 'Offer Accepted'),
        ('offer_declined', 'Offer Declined'),
    )
    
    placement_drive = models.ForeignKey(PlacementDrive, on_delete=models.CASCADE, related_name='applications')
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='placement_applications')
    
    applied_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=30, choices=APPLICATION_STATUS_CHOICES, default='registered')
    
    resume = models.FileField(upload_to='placement/resumes/')
    cover_letter = models.TextField(blank=True)
    
    # Test Scores
    aptitude_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    technical_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    hr_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    
    # Offer Details (if selected)
    offer_letter = models.FileField(upload_to='placement/offer_letters/', blank=True, null=True)
    offered_package = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    joining_date = models.DateField(null=True, blank=True)
    
    remarks = models.TextField(blank=True)
    
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.student} - {self.placement_drive.company.name}"
    
    class Meta:
        unique_together = ('placement_drive', 'student')
        ordering = ['-applied_at']


class Grievance(models.Model):
    """Student/Staff Grievance/Complaint Management"""
    GRIEVANCE_TYPE_CHOICES = (
        ('academic', 'Academic'),
        ('administrative', 'Administrative'),
        ('hostel', 'Hostel Related'),
        ('library', 'Library'),
        ('transport', 'Transport'),
        ('ragging', 'Ragging/Harassment'),
        ('fee', 'Fee Related'),
        ('other', 'Other'),
    )
    
    PRIORITY_CHOICES = (
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    )
    
    STATUS_CHOICES = (
        ('submitted', 'Submitted'),
        ('under_review', 'Under Review'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
        ('rejected', 'Rejected'),
    )
    
    grievance_number = models.CharField(max_length=50, unique=True)
    submitted_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='grievances')
    
    grievance_type = models.CharField(max_length=30, choices=GRIEVANCE_TYPE_CHOICES)
    subject = models.CharField(max_length=200)
    description = models.TextField()
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    
    attachment = models.FileField(upload_to='grievances/', blank=True, null=True)
    
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='submitted')
    assigned_to = models.ForeignKey(Staff, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_grievances')
    
    resolution = models.TextField(blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    
    submitted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.grievance_number} - {self.subject}"
    
    class Meta:
        ordering = ['-submitted_at']


class HostelVisitorLog(models.Model):
    """Hostel Visitor Entry/Exit Log"""
    hostel = models.ForeignKey(Hostel, on_delete=models.CASCADE, related_name='visitor_logs')
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='hostel_visitors')
    
    visitor_name = models.CharField(max_length=200)
    visitor_relation = models.CharField(max_length=100)
    visitor_contact = models.CharField(max_length=15)
    visitor_id_proof = models.CharField(max_length=100, help_text="ID type and number")
    
    entry_time = models.DateTimeField(auto_now_add=True)
    exit_time = models.DateTimeField(null=True, blank=True)
    purpose = models.TextField()
    
    approved_by = models.ForeignKey(Staff, on_delete=models.SET_NULL, null=True, related_name='approved_visitors')
    
    def __str__(self):
        return f"{self.visitor_name} visiting {self.student} at {self.hostel}"
    
    class Meta:
        ordering = ['-entry_time']


class ActivityLog(models.Model):
    """System Activity/Audit Log"""
    ACTION_CHOICES = (
        ('create', 'Created'),
        ('update', 'Updated'),
        ('delete', 'Deleted'),
        ('login', 'Logged In'),
        ('logout', 'Logged Out'),
        ('view', 'Viewed'),
        ('download', 'Downloaded'),
        ('upload', 'Uploaded'),
    )
    
    user = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, related_name='activity_logs')
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    model_name = models.CharField(max_length=100, blank=True)
    object_id = models.IntegerField(null=True, blank=True)
    description = models.TextField()
    
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user} - {self.action} - {self.timestamp}"
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['-timestamp']),
            models.Index(fields=['user', '-timestamp']),
        ]


class ParentGuardian(models.Model):
    """Parent/Guardian Portal Access"""
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='parent_accounts')
    parent_name = models.CharField(max_length=200)
    relation = models.CharField(max_length=50, choices=(('father', 'Father'), ('mother', 'Mother'), ('guardian', 'Guardian')))
    email = models.EmailField(unique=True)
    password_hash = models.CharField(max_length=255)
    mobile_number = models.CharField(max_length=15)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.parent_name} ({self.relation}) - {self.student}"
    
    class Meta:
        verbose_name = "Parent/Guardian"
        verbose_name_plural = "Parents/Guardians"


class OnlineExam(models.Model):
    """Online Examination Module"""
    title = models.CharField(max_length=200)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='online_exams')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='online_exams')
    created_by = models.ForeignKey(Staff, on_delete=models.CASCADE, related_name='created_online_exams')
    
    duration_minutes = models.IntegerField(help_text="Exam duration in minutes")
    total_marks = models.IntegerField()
    passing_marks = models.IntegerField()
    
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()
    
    instructions = models.TextField(blank=True)
    is_published = models.BooleanField(default=False)
    shuffle_questions = models.BooleanField(default=True)
    show_result_immediately = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.title} - {self.subject.name}"


class OnlineExamQuestion(models.Model):
    """Questions for Online Exam"""
    QUESTION_TYPE = (
        ('mcq', 'Multiple Choice'),
        ('true_false', 'True/False'),
        ('short', 'Short Answer'),
        ('long', 'Long Answer'),
    )
    
    exam = models.ForeignKey(OnlineExam, on_delete=models.CASCADE, related_name='questions')
    question_text = models.TextField()
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPE, default='mcq')
    marks = models.IntegerField(default=1)
    
    option_a = models.CharField(max_length=500, blank=True)
    option_b = models.CharField(max_length=500, blank=True)
    option_c = models.CharField(max_length=500, blank=True)
    option_d = models.CharField(max_length=500, blank=True)
    correct_answer = models.CharField(max_length=500)
    
    explanation = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.exam.title} - Q{self.id}"


class OnlineExamAttempt(models.Model):
    """Student's Online Exam Attempt"""
    exam = models.ForeignKey(OnlineExam, on_delete=models.CASCADE, related_name='attempts')
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='online_exam_attempts')
    
    start_time = models.DateTimeField(auto_now_add=True)
    submit_time = models.DateTimeField(null=True, blank=True)
    
    marks_obtained = models.IntegerField(default=0)
    is_passed = models.BooleanField(default=False)
    
    answers = models.JSONField(default=dict)  # Store student's answers
    
    class Meta:
        unique_together = ('exam', 'student')
    
    def __str__(self):
        return f"{self.student} - {self.exam.title}"


class StudentCertificate(models.Model):
    """Student's Personal Certificate Storage"""
    CERTIFICATE_TYPES = (
        ('10th', '10th Grade Certificate'),
        ('12th', '12th Grade Certificate'),
        ('diploma', 'Diploma Certificate'),
        ('degree', 'Degree Certificate'),
        ('transfer', 'Transfer Certificate'),
        ('migration', 'Migration Certificate'),
        ('conduct', 'Conduct Certificate'),
        ('bonafide', 'Bonafide Certificate'),
        ('character', 'Character Certificate'),
        ('experience', 'Experience Certificate'),
        ('achievement', 'Achievement Certificate'),
        ('other', 'Other'),
    )
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='uploaded_certificates')
    certificate_type = models.CharField(max_length=50, choices=CERTIFICATE_TYPES)
    certificate_title = models.CharField(max_length=200)
    certificate_file = models.FileField(upload_to='student_certificates/%Y/%m/')
    issue_date = models.DateField(null=True, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.student.admin.username} - {self.certificate_title}"
    
    class Meta:
        ordering = ['-uploaded_at']


class Certificate(models.Model):
    """Certificate Generation & Management"""
    CERTIFICATE_TYPE = (
        ('course_completion', 'Course Completion'),
        ('degree', 'Degree Certificate'),
        ('provisional', 'Provisional Certificate'),
        ('character', 'Character Certificate'),
        ('bonafide', 'Bonafide Certificate'),
        ('transfer', 'Transfer Certificate'),
        ('participation', 'Event Participation'),
        ('achievement', 'Achievement Certificate'),
    )
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='official_certificates')
    certificate_type = models.CharField(max_length=30, choices=CERTIFICATE_TYPE)
    certificate_number = models.CharField(max_length=50, unique=True)
    
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    
    issued_date = models.DateField()
    valid_until = models.DateField(null=True, blank=True)
    
    issued_by = models.ForeignKey(Staff, on_delete=models.SET_NULL, null=True, related_name='issued_certificates')
    verified_by = models.ForeignKey(Staff, on_delete=models.SET_NULL, null=True, blank=True, related_name='verified_certificates')
    
    certificate_file = models.FileField(upload_to='certificates/generated/', blank=True, null=True)
    qr_code = models.ImageField(upload_to='certificates/qr/', blank=True, null=True)
    
    is_verified = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.certificate_number} - {self.student}"


class Alumni(models.Model):
    """Enhanced Alumni Management"""
    student = models.OneToOneField(Student, on_delete=models.CASCADE, related_name='alumni_profile')
    
    passout_year = models.IntegerField()
    final_cgpa = models.DecimalField(max_digits=4, decimal_places=2)
    
    # Current Information
    current_company = models.CharField(max_length=200, blank=True)
    current_designation = models.CharField(max_length=200, blank=True)
    current_location = models.CharField(max_length=200, blank=True)
    current_salary_package = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Enhanced Professional Information
    industry = models.CharField(max_length=100, blank=True, help_text="Industry sector")
    work_experience_years = models.IntegerField(null=True, blank=True, help_text="Years of work experience")
    job_function = models.CharField(max_length=100, blank=True, help_text="Job function/role")
    company_size = models.CharField(max_length=50, blank=True, choices=[
        ('startup', 'Startup (1-50 employees)'),
        ('small', 'Small (51-200 employees)'),
        ('medium', 'Medium (201-1000 employees)'),
        ('large', 'Large (1000+ employees)'),
        ('mnc', 'Multinational Corporation'),
    ])
    
    # Contact Information
    current_email = models.EmailField(blank=True)
    current_mobile = models.CharField(max_length=15, blank=True)
    linkedin_profile = models.URLField(blank=True)
    twitter_handle = models.CharField(max_length=100, blank=True)
    personal_website = models.URLField(blank=True)
    
    # Engagement & Volunteering
    is_willing_to_mentor = models.BooleanField(default=False)
    is_available_for_placement_talks = models.BooleanField(default=False)
    is_recruiter = models.BooleanField(default=False)
    is_willing_to_host_interns = models.BooleanField(default=False)
    is_willing_to_sponsor_events = models.BooleanField(default=False)
    
    # Mentorship Preferences
    mentorship_areas = models.JSONField(default=list, blank=True, help_text="Areas where alumni can mentor")
    mentorship_availability = models.CharField(max_length=20, choices=[
        ('available', 'Available'),
        ('limited', 'Limited Availability'),
        ('unavailable', 'Currently Unavailable'),
    ], default='available')
    max_mentees = models.IntegerField(default=2, help_text="Maximum number of mentees")
    
    # Social Media & Online Presence
    facebook_profile = models.URLField(blank=True)
    instagram_handle = models.CharField(max_length=100, blank=True)
    github_profile = models.URLField(blank=True)
    portfolio_url = models.URLField(blank=True)
    
    # Achievements & Recognition
    achievements = models.TextField(blank=True)
    awards_received = models.TextField(blank=True, help_text="Awards and recognitions")
    publications = models.TextField(blank=True, help_text="Research publications or articles")
    patents = models.TextField(blank=True, help_text="Patents filed or granted")
    
    # Testimonial & Feedback
    testimonial = models.TextField(blank=True)
    college_impact_story = models.TextField(blank=True, help_text="How college impacted their career")
    advice_for_current_students = models.TextField(blank=True)
    
    # Engagement Metrics
    event_participation_count = models.IntegerField(default=0)
    mentorship_sessions_count = models.IntegerField(default=0)
    total_donations = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    last_engagement_date = models.DateTimeField(null=True, blank=True)
    
    # Privacy & Communication Preferences
    profile_visibility = models.CharField(max_length=20, choices=[
        ('public', 'Public'),
        ('alumni_only', 'Alumni Only'),
        ('private', 'Private'),
    ], default='alumni_only')
    newsletter_subscription = models.BooleanField(default=True)
    event_notifications = models.BooleanField(default=True)
    mentorship_requests = models.BooleanField(default=True)
    
    # Profile Completion
    profile_completion_percentage = models.IntegerField(default=0)
    is_profile_verified = models.BooleanField(default=False)
    verification_date = models.DateTimeField(null=True, blank=True)
    
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.student} - Batch {self.passout_year}"
    
    @property
    def full_name(self):
        """Get alumni full name"""
        return f"{self.student.admin.first_name} {self.student.admin.last_name}"
    
    @property
    def is_active_mentor(self):
        """Check if alumni is an active mentor"""
        return (self.is_willing_to_mentor and 
                self.mentorship_availability == 'available' and
                self.mentorship_sessions_count < self.max_mentees)
    
    class Meta:
        ordering = ['-passout_year', 'student__admin__first_name']
        indexes = [
            models.Index(fields=['passout_year'], name='alumni_passout_year_idx'),
            models.Index(fields=['current_company'], name='alumni_company_idx'),
            models.Index(fields=['is_willing_to_mentor'], name='alumni_mentor_idx'),
            models.Index(fields=['is_recruiter'], name='alumni_recruiter_idx'),
            models.Index(fields=['industry'], name='alumni_industry_idx'),
            models.Index(fields=['profile_visibility'], name='alumni_visibility_idx'),
        ]


class Internship(models.Model):
    """Internship Management"""
    INTERNSHIP_TYPE = (
        ('summer', 'Summer Internship'),
        ('winter', 'Winter Internship'),
        ('full_time', 'Full Time'),
        ('part_time', 'Part Time'),
    )
    
    STATUS_CHOICES = (
        ('applied', 'Applied'),
        ('ongoing', 'Ongoing'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='internships')
    
    company_name = models.CharField(max_length=200)
    internship_type = models.CharField(max_length=20, choices=INTERNSHIP_TYPE)
    role = models.CharField(max_length=200)
    
    start_date = models.DateField()
    end_date = models.DateField()
    duration_months = models.IntegerField()
    
    stipend = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    location = models.CharField(max_length=200)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='applied')
    
    offer_letter = models.FileField(upload_to='internships/offers/', blank=True, null=True)
    completion_certificate = models.FileField(upload_to='internships/certificates/', blank=True, null=True)
    
    supervisor_name = models.CharField(max_length=200, blank=True)
    supervisor_contact = models.CharField(max_length=15, blank=True)
    
    description = models.TextField(blank=True)
    feedback = models.TextField(blank=True)
    
    approved_by = models.ForeignKey(Staff, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_internships')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.student} - {self.company_name} ({self.role})"


class MedicalRecord(models.Model):
    """Student Medical Records"""
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='medical_records')
    
    record_date = models.DateField(auto_now_add=True)
    complaint = models.TextField()
    diagnosis = models.TextField(blank=True)
    treatment = models.TextField(blank=True)
    
    doctor_name = models.CharField(max_length=200, blank=True)
    prescription = models.FileField(upload_to='medical/prescriptions/', blank=True, null=True)
    
    follow_up_required = models.BooleanField(default=False)
    follow_up_date = models.DateField(null=True, blank=True)
    
    remarks = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.student} - {self.record_date}"


class GatePass(models.Model):
    """Student Gate Pass System"""
    PASS_TYPE = (
        ('outing', 'General Outing'),
        ('home', 'Home Visit'),
        ('medical', 'Medical Emergency'),
        ('official', 'Official Work'),
    )
    
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('used', 'Used'),
        ('expired', 'Expired'),
    )
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='gate_passes')
    pass_type = models.CharField(max_length=20, choices=PASS_TYPE)
    
    reason = models.TextField()
    from_date = models.DateTimeField()
    to_date = models.DateTimeField()
    destination = models.CharField(max_length=200)
    
    parent_consent = models.BooleanField(default=False)
    parent_contact = models.CharField(max_length=15, blank=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    approved_by = models.ForeignKey(Staff, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_gate_passes')
    approval_date = models.DateTimeField(null=True, blank=True)
    
    exit_time = models.DateTimeField(null=True, blank=True)
    entry_time = models.DateTimeField(null=True, blank=True)
    
    remarks = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.student} - {self.get_pass_type_display()} - {self.status}"


class DisciplinaryAction(models.Model):
    """Student Disciplinary Records"""
    SEVERITY = (
        ('minor', 'Minor'),
        ('moderate', 'Moderate'),
        ('major', 'Major'),
        ('severe', 'Severe'),
    )
    
    ACTION_TYPE = (
        ('warning', 'Warning'),
        ('fine', 'Fine'),
        ('suspension', 'Suspension'),
        ('expulsion', 'Expulsion'),
        ('community_service', 'Community Service'),
    )
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='disciplinary_actions')
    
    incident_date = models.DateField()
    incident_description = models.TextField()
    severity = models.CharField(max_length=20, choices=SEVERITY)
    
    action_taken = models.CharField(max_length=30, choices=ACTION_TYPE)
    action_description = models.TextField()
    
    fine_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    suspension_from = models.DateField(null=True, blank=True)
    suspension_to = models.DateField(null=True, blank=True)
    
    reported_by = models.ForeignKey(Staff, on_delete=models.SET_NULL, null=True, related_name='reported_incidents')
    action_by = models.ForeignKey(Staff, on_delete=models.SET_NULL, null=True, related_name='disciplinary_actions')
    
    is_resolved = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.student} - {self.get_severity_display()} - {self.incident_date}"


class SportsActivity(models.Model):
    """Sports & Cultural Activities"""
    ACTIVITY_TYPE = (
        ('sports', 'Sports'),
        ('cultural', 'Cultural'),
        ('technical', 'Technical'),
        ('social', 'Social Service'),
    )
    
    name = models.CharField(max_length=200)
    activity_type = models.CharField(max_length=20, choices=ACTIVITY_TYPE)
    description = models.TextField()
    
    start_date = models.DateField()
    end_date = models.DateField()
    venue = models.CharField(max_length=200)
    
    coordinator = models.ForeignKey(Staff, on_delete=models.SET_NULL, null=True, related_name='coordinated_activities')
    
    max_participants = models.IntegerField(default=100)
    registration_deadline = models.DateField()
    
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.name} ({self.get_activity_type_display()})"


class ActivityParticipation(models.Model):
    """Student Participation in Sports/Cultural Activities"""
    ACHIEVEMENT_LEVEL = (
        ('participated', 'Participated'),
        ('winner', '1st Place'),
        ('runner_up', '2nd Place'),
        ('third', '3rd Place'),
        ('consolation', 'Consolation'),
    )
    
    activity = models.ForeignKey(SportsActivity, on_delete=models.CASCADE, related_name='participants')
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='activity_participations')
    
    achievement_level = models.CharField(max_length=20, choices=ACHIEVEMENT_LEVEL, default='participated')
    certificate_issued = models.BooleanField(default=False)
    certificate_number = models.CharField(max_length=50, blank=True)
    
    remarks = models.TextField(blank=True)
    
    registered_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.student} - {self.activity.name}"


class Research(models.Model):
    """Faculty Research & Publications"""
    PUBLICATION_TYPE = (
        ('journal', 'Journal Paper'),
        ('conference', 'Conference Paper'),
        ('book', 'Book'),
        ('book_chapter', 'Book Chapter'),
        ('patent', 'Patent'),
    )
    
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE, related_name='research_publications')
    
    title = models.CharField(max_length=500)
    publication_type = models.CharField(max_length=20, choices=PUBLICATION_TYPE)
    
    authors = models.TextField(help_text="Comma-separated list of authors")
    publication_name = models.CharField(max_length=300, help_text="Journal/Conference name")
    publisher = models.CharField(max_length=200, blank=True)
    
    publication_date = models.DateField()
    volume = models.CharField(max_length=50, blank=True)
    issue = models.CharField(max_length=50, blank=True)
    page_numbers = models.CharField(max_length=50, blank=True)
    
    doi = models.CharField(max_length=200, blank=True, verbose_name="DOI")
    isbn_issn = models.CharField(max_length=50, blank=True, verbose_name="ISBN/ISSN")
    
    abstract = models.TextField(blank=True)
    keywords = models.CharField(max_length=500, blank=True)
    
    citation_count = models.IntegerField(default=0)
    impact_factor = models.DecimalField(max_digits=5, decimal_places=3, null=True, blank=True)
    
    pdf_file = models.FileField(upload_to='research/papers/', blank=True, null=True)
    
    is_peer_reviewed = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.title} ({self.publication_date.year})"


class AntiRaggingCommittee(models.Model):
    """Anti-Ragging Committee & Incidents"""
    INCIDENT_SEVERITY = (
        ('minor', 'Minor'),
        ('moderate', 'Moderate'),
        ('severe', 'Severe'),
    )
    
    STATUS_CHOICES = (
        ('reported', 'Reported'),
        ('investigating', 'Under Investigation'),
        ('action_taken', 'Action Taken'),
        ('closed', 'Closed'),
        ('false_complaint', 'False Complaint'),
    )
    
    incident_number = models.CharField(max_length=50, unique=True)
    reporter = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='ragging_reports')
    
    incident_date = models.DateField()
    incident_description = models.TextField()
    location = models.CharField(max_length=200)
    severity = models.CharField(max_length=20, choices=INCIDENT_SEVERITY)
    
    accused_students = models.TextField(help_text="Names of accused students")
    witnesses = models.TextField(blank=True)
    
    evidence = models.FileField(upload_to='ragging/evidence/', blank=True, null=True)
    
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='reported')
    investigating_officer = models.ForeignKey(Staff, on_delete=models.SET_NULL, null=True, related_name='ragging_investigations')
    
    action_taken = models.TextField(blank=True)
    closure_remarks = models.TextField(blank=True)
    
    is_anonymous = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.incident_number} - {self.severity}"


class StudentCouncil(models.Model):
    """Student Council/Body Management"""
    POSITION_CHOICES = (
        ('president', 'President'),
        ('vice_president', 'Vice President'),
        ('secretary', 'Secretary'),
        ('treasurer', 'Treasurer'),
        ('cultural_secretary', 'Cultural Secretary'),
        ('sports_secretary', 'Sports Secretary'),
        ('technical_secretary', 'Technical Secretary'),
        ('member', 'Member'),
    )
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='council_positions')
    session = models.ForeignKey(Session, on_delete=models.CASCADE, related_name='student_council')
    
    position = models.CharField(max_length=30, choices=POSITION_CHOICES)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True)
    
    election_date = models.DateField()
    term_start = models.DateField()
    term_end = models.DateField()
    
    manifesto = models.TextField(blank=True)
    achievements = models.TextField(blank=True)
    
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.student} - {self.get_position_display()} ({self.session})"


class Classroom(models.Model):
    """Classroom/Room Management"""
    ROOM_TYPE = (
        ('classroom', 'Regular Classroom'),
        ('lab', 'Laboratory'),
        ('seminar', 'Seminar Hall'),
        ('auditorium', 'Auditorium'),
        ('library', 'Library Reading Room'),
        ('staff_room', 'Staff Room'),
        ('tutorial', 'Tutorial Room'),
    )
    
    room_number = models.CharField(max_length=50, unique=True)
    room_name = models.CharField(max_length=200, blank=True)
    room_type = models.CharField(max_length=20, choices=ROOM_TYPE, default='classroom')
    
    building = models.CharField(max_length=100, blank=True)
    floor = models.IntegerField(default=0)
    
    capacity = models.IntegerField(help_text="Maximum number of students")
    
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True, related_name='classrooms')
    
    # Facilities
    has_projector = models.BooleanField(default=False)
    has_ac = models.BooleanField(default=False)
    has_wifi = models.BooleanField(default=True)
    has_audio_system = models.BooleanField(default=False)
    has_whiteboard = models.BooleanField(default=True)
    has_computers = models.BooleanField(default=False)
    computer_count = models.IntegerField(default=0, help_text="Number of computers (for labs)")
    
    is_available = models.BooleanField(default=True)
    is_under_maintenance = models.BooleanField(default=False)
    
    remarks = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.room_number} - {self.get_room_type_display()}"
    
    class Meta:
        ordering = ['building', 'floor', 'room_number']


class ClassroomBooking(models.Model):
    """Room Booking/Reservation System"""
    BOOKING_TYPE = (
        ('class', 'Regular Class'),
        ('exam', 'Examination'),
        ('event', 'Event/Seminar'),
        ('meeting', 'Meeting'),
        ('workshop', 'Workshop'),
        ('other', 'Other'),
    )
    
    STATUS_CHOICES = (
        ('pending', 'Pending Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )
    
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE, related_name='bookings')
    
    booking_type = models.CharField(max_length=20, choices=BOOKING_TYPE)
    purpose = models.CharField(max_length=200)
    
    booked_by = models.ForeignKey(Staff, on_delete=models.CASCADE, related_name='classroom_bookings')
    
    booking_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    
    expected_attendees = models.IntegerField(help_text="Number of expected participants")
    
    # For classes
    subject = models.ForeignKey(Subject, on_delete=models.SET_NULL, null=True, blank=True)
    course = models.ForeignKey(Course, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Approval
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    approved_by = models.ForeignKey(Staff, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_bookings')
    approval_date = models.DateTimeField(null=True, blank=True)
    
    special_requirements = models.TextField(blank=True, help_text="Any special setup needed")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.classroom.room_number} - {self.booking_date} ({self.start_time}-{self.end_time})"
    
    class Meta:
        ordering = ['-booking_date', 'start_time']


class ClassroomMaintenance(models.Model):
    """Track Classroom Maintenance & Issues"""
    ISSUE_TYPE = (
        ('electrical', 'Electrical'),
        ('furniture', 'Furniture'),
        ('cleaning', 'Cleaning'),
        ('equipment', 'Equipment'),
        ('structural', 'Structural'),
        ('other', 'Other'),
    )
    
    STATUS_CHOICES = (
        ('reported', 'Reported'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('pending_parts', 'Pending Parts'),
    )
    
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE, related_name='maintenance_records')
    
    issue_type = models.CharField(max_length=20, choices=ISSUE_TYPE)
    issue_description = models.TextField()
    
    reported_by = models.ForeignKey(Staff, on_delete=models.SET_NULL, null=True, related_name='reported_maintenance')
    reported_date = models.DateField(auto_now_add=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='reported')
    
    assigned_to = models.CharField(max_length=200, blank=True, help_text="Maintenance staff assigned")
    
    estimated_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    actual_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    completion_date = models.DateField(null=True, blank=True)
    
    remarks = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.classroom.room_number} - {self.get_issue_type_display()}"


class OTP(models.Model):
    """OTP Model for Two-Factor Authentication"""
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='otps')
    otp_code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    attempts = models.IntegerField(default=0, help_text="Number of failed verification attempts")
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'OTP'
        verbose_name_plural = 'OTPs'
    
    def __str__(self):
        return f"OTP for {self.user.email} - {self.otp_code}"
    
    def is_valid(self):
        """Check if OTP is still valid (not expired and not used)"""
        from django.utils import timezone
        return not self.is_used and timezone.now() < self.expires_at


@receiver(post_save, sender=CustomUser)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        if instance.user_type == 1:
            Admin.objects.create(admin=instance)
        if instance.user_type == 2:
            Staff.objects.create(admin=instance)
        if instance.user_type == 3:
            Student.objects.create(admin=instance)
        if instance.user_type == 4:
            Management.objects.create(admin=instance)


@receiver(post_save, sender=CustomUser)
def save_user_profile(sender, instance, **kwargs):
    if instance.user_type == 1:
        instance.admin.save()
    if instance.user_type == 2:
        instance.staff.save()
    if instance.user_type == 3:
        instance.student.save()
    if instance.user_type == 4:
        instance.management.save()


# ================================
# AUDIT AND SECURITY MODELS
# ================================

# Import audit models from separate file to avoid circular imports
from .audit_models import AuditLog, SecurityEvent, DataAccessLog

# Import admission models from separate file to avoid circular imports
from .admission_models import (
    AdmissionSession, AdmissionProgram, AdmissionApplication,
    AdmissionDocument, AdmissionTest, AdmissionPayment,
    AdmissionMeritList, AdmissionMeritEntry
)

# Payroll models are defined in this file
class PayrollStructure(models.Model):
    """Payroll structure for different employee categories"""
    name = models.CharField(max_length=100)
    basic_salary = models.DecimalField(max_digits=10, decimal_places=2)
    hra = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    da = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    medical_allowance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    transport_allowance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']


class EmployeeSalary(models.Model):
    """Employee salary details"""
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE, related_name='salaries')
    payroll_structure = models.ForeignKey(PayrollStructure, on_delete=models.CASCADE)
    basic_salary = models.DecimalField(max_digits=10, decimal_places=2)
    hra = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    da = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    medical_allowance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    transport_allowance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_salary = models.DecimalField(max_digits=10, decimal_places=2)
    effective_from = models.DateField()
    effective_to = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.staff.admin.first_name} - {self.total_salary}"
    
    class Meta:
        ordering = ['-effective_from']


class Payslip(models.Model):
    """Monthly payslip generation"""
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE, related_name='payslips')
    month = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(12)])
    year = models.IntegerField()
    basic_salary = models.DecimalField(max_digits=10, decimal_places=2)
    allowances = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    deductions = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    net_salary = models.DecimalField(max_digits=10, decimal_places=2)
    generated_date = models.DateTimeField(auto_now_add=True)
    is_paid = models.BooleanField(default=False)
    paid_date = models.DateField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.staff.admin.first_name} - {self.month}/{self.year}"
    
    class Meta:
        ordering = ['-year', '-month']
        unique_together = ['staff', 'month', 'year']


class TaxDeclaration(models.Model):
    """Employee tax declarations"""
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE, related_name='tax_declarations')
    financial_year = models.CharField(max_length=9)  # e.g., "2024-25"
    total_income = models.DecimalField(max_digits=10, decimal_places=2)
    tax_deducted = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    submitted_date = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)
    verified_by = models.ForeignKey(Staff, on_delete=models.SET_NULL, null=True, blank=True, related_name='verified_tax_declarations')
    verified_date = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.staff.admin.first_name} - {self.financial_year}"
    
    class Meta:
        ordering = ['-financial_year']


class LeaveBalance(models.Model):
    """Employee leave balance"""
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE, related_name='leave_balances')
    leave_type = models.CharField(max_length=50)
    total_leaves = models.IntegerField(default=0)
    used_leaves = models.IntegerField(default=0)
    remaining_leaves = models.IntegerField(default=0)
    year = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.staff.admin.first_name} - {self.leave_type} ({self.year})"
    
    class Meta:
        ordering = ['-year']
        unique_together = ['staff', 'leave_type', 'year']


class AttendanceRegister(models.Model):
    """Employee attendance register"""
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE, related_name='attendance_records', null=True, blank=True)
    date = models.DateField()
    check_in = models.TimeField(null=True, blank=True)
    check_out = models.TimeField(null=True, blank=True)
    hours_worked = models.DecimalField(max_digits=4, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=[
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('half_day', 'Half Day'),
        ('late', 'Late'),
        ('overtime', 'Overtime'),
    ], default='present')
    remarks = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        staff_name = self.staff.admin.first_name if self.staff else "Unknown"
        return f"{staff_name} - {self.date}"
    
    class Meta:
        ordering = ['-date']
        unique_together = ['staff', 'date']


class Bonus(models.Model):
    """Employee bonuses and incentives"""
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE, related_name='bonuses')
    bonus_type = models.CharField(max_length=50)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    reason = models.TextField(blank=True, default='')
    bonus_date = models.DateField(null=True, blank=True)
    approved_by = models.ForeignKey(Staff, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_bonuses')
    approved_date = models.DateTimeField(null=True, blank=True)
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.staff.admin.first_name} - {self.bonus_type}"
    
    class Meta:
        ordering = ['-bonus_date']


class Loan(models.Model):
    """Employee loans"""
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE, related_name='loans')
    loan_type = models.CharField(max_length=50)
    principal_amount = models.DecimalField(max_digits=10, decimal_places=2)
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2)
    tenure_months = models.IntegerField()
    monthly_emi = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    loan_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=[
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ], default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.staff.admin.first_name} - {self.loan_type}"
    
    class Meta:
        ordering = ['-loan_date']


class LoanEMI(models.Model):
    """Loan EMI payments"""
    loan = models.ForeignKey(Loan, on_delete=models.CASCADE, related_name='emis')
    emi_number = models.IntegerField()
    due_date = models.DateField()
    principal_amount = models.DecimalField(max_digits=10, decimal_places=2)
    interest_amount = models.DecimalField(max_digits=10, decimal_places=2)
    total_emi = models.DecimalField(max_digits=10, decimal_places=2)
    paid_date = models.DateField(null=True, blank=True)
    is_paid = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.loan.staff.admin.first_name} - EMI {self.emi_number}"
    
    class Meta:
        ordering = ['emi_number']
        unique_together = ['loan', 'emi_number']

# Import alumni models from separate file to avoid circular imports
from .alumni_models import (
    AlumniAchievement, AlumniEvent, AlumniEventRegistration, AlumniDonation,
    AlumniDonationTransaction, AlumniMentorship, AlumniJob, AlumniNewsletter
)

# Communication models are defined in this file

# Placement models are defined in this file

# Import LMS models from separate file
from .lms_models import (
    CourseModule, Quiz, Question, QuestionOption, QuizAttempt,
    StudentProgress, CourseEnrollment, DiscussionForum, DiscussionPost,
    LMSAssignment, LMSAssignmentSubmission
)


class PublicLink(models.Model):
    """Public links accessible to students on dashboard"""
    CATEGORY_CHOICES = [
        ('academic', 'Academic Resources'),
        ('administrative', 'Administrative Services'),
        ('external', 'External Resources'),
        ('internal', 'Internal Services'),
    ]
    
    LINK_TYPE_CHOICES = [
        ('website', 'Website'),
        ('portal', 'Portal'),
        ('resource', 'Resource'),
        ('service', 'Service'),
        ('course', 'Online Course'),
    ]
    
    TARGET_CHOICES = [
        ('_blank', 'New Tab'),
        ('_self', 'Same Tab'),
    ]
    
    title = models.CharField(max_length=200, help_text="Display name for the link")
    url = models.URLField(help_text="Full URL including http:// or https://")
    description = models.TextField(blank=True, help_text="Brief description of the link")
    icon = models.CharField(max_length=50, default='fas fa-link', help_text="FontAwesome icon class")
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='external')
    link_type = models.CharField(max_length=20, choices=LINK_TYPE_CHOICES, default='website')
    target = models.CharField(max_length=10, choices=TARGET_CHOICES, default='_blank')
    is_active = models.BooleanField(default=True, help_text="Show/hide this link")
    display_order = models.PositiveIntegerField(default=0, help_text="Order of display (lower numbers first)")
    is_featured = models.BooleanField(default=False, help_text="Show as featured/prominent link")
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='created_links')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['display_order', 'title']
        verbose_name = 'Public Link'
        verbose_name_plural = 'Public Links'
    
    def __str__(self):
        return f"{self.title} ({self.get_category_display()})"
    
    def get_icon_html(self):
        """Return formatted icon HTML"""
        return f'<i class="{self.icon}"></i>'
    
    def is_external(self):
        """Check if link is external (opens in new tab)"""
        return self.target == '_blank'


class DocumentType(models.Model):
    """Document types required for student enrollment"""
    DOCUMENT_CHOICES = (
        ('photo', 'Photo'),
        ('aadhar', 'Aadhar Card'),
        ('tenth_cert', '10th Certificate'),
        ('twelfth_cert', '12th Certificate'),
        ('transfer_cert', 'Transfer Certificate'),
        ('migration_cert', 'Migration Certificate'),
        ('caste_cert', 'Caste Certificate'),
        ('income_cert', 'Income Certificate'),
        ('medical_cert', 'Medical Certificate'),
        ('other', 'Other'),
    )
    
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    document_type = models.CharField(max_length=20, choices=DOCUMENT_CHOICES)
    is_mandatory = models.BooleanField(default=True)
    description = models.TextField(blank=True)
    max_file_size = models.IntegerField(default=5, help_text="Maximum file size in MB")
    allowed_formats = models.CharField(max_length=100, default="pdf,jpg,jpeg,png", help_text="Comma-separated file extensions")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, null=True, blank=True, help_text="Specific to course (null for all courses)")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} ({self.get_document_type_display()})"
    
    class Meta:
        ordering = ['name']


class StudentDocument(models.Model):
    """Student uploaded documents"""
    VERIFICATION_STATUS = (
        ('pending', 'Pending'),
        ('verified', 'Verified'),
        ('rejected', 'Rejected'),
        ('reupload_required', 'Re-upload Required'),
    )
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='documents')
    document_type = models.ForeignKey(DocumentType, on_delete=models.CASCADE)
    file = models.FileField(upload_to='student_documents/%Y/%m/%d/')
    uploaded_date = models.DateTimeField(auto_now_add=True)
    verified_status = models.CharField(max_length=20, choices=VERIFICATION_STATUS, default='pending')
    verified_by = models.ForeignKey(Staff, on_delete=models.SET_NULL, null=True, blank=True)
    verified_date = models.DateTimeField(null=True, blank=True)
    remarks = models.TextField(blank=True, help_text="Admin remarks for verification")
    is_active = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.student.admin.first_name} - {self.document_type.name}"
    
    class Meta:
        ordering = ['-uploaded_date']
        unique_together = ['student', 'document_type']
    
    def get_file_size(self):
        """Get file size in human readable format"""
        if self.file:
            size = self.file.size
            for unit in ['B', 'KB', 'MB', 'GB']:
                if size < 1024.0:
                    return f"{size:.1f} {unit}"
                size /= 1024.0
        return "0 B"
    
    def get_file_extension(self):
        """Get file extension"""
        if self.file:
            return self.file.name.split('.')[-1].lower()
        return ""
    
    def is_verified(self):
        """Check if document is verified"""
        return self.verified_status == 'verified'
    
    def is_pending(self):
        """Check if document is pending verification"""
        return self.verified_status == 'pending'
    
    def is_rejected(self):
        """Check if document is rejected"""
        return self.verified_status == 'rejected'
    class Meta:
        ordering = ['-uploaded_date']
        unique_together = ['student', 'document_type']
    
    def get_file_size(self):
        """Get file size in human readable format"""
        if self.file:
            size = self.file.size
            for unit in ['B', 'KB', 'MB', 'GB']:
                if size < 1024.0:
                    return f"{size:.1f} {unit}"
                size /= 1024.0
        return "0 B"
    
    def get_file_extension(self):
        """Get file extension"""
        if self.file:
            return self.file.name.split('.')[-1].lower()
        return ""
    
    def is_verified(self):
        """Check if document is verified"""
        return self.verified_status == 'verified'
    
    def is_pending(self):
        """Check if document is pending verification"""
        return self.verified_status == 'pending'
    
    def is_rejected(self):
        """Check if document is rejected"""
        return self.verified_status == 'rejected'



