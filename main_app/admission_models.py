"""
Admissions Management Models for College ERP
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
import uuid

User = get_user_model()


class AdmissionSession(models.Model):
    """
    Admission intake sessions (e.g., 2024-25, 2025-26)
    """
    STATUS_CHOICES = (
        ('upcoming', 'Upcoming'),
        ('active', 'Active'),
        ('closed', 'Closed'),
        ('completed', 'Completed'),
    )
    
    name = models.CharField(max_length=100, unique=True, help_text="e.g., 2024-25 Academic Year")
    intake_year = models.IntegerField(help_text="Academic year for intake")
    application_start_date = models.DateTimeField()
    application_end_date = models.DateTimeField()
    merit_list_date = models.DateTimeField(null=True, blank=True)
    counselling_start_date = models.DateTimeField(null=True, blank=True)
    counselling_end_date = models.DateTimeField(null=True, blank=True)
    classes_start_date = models.DateField(null=True, blank=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='upcoming')
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-intake_year']
        indexes = [
            models.Index(fields=['intake_year'], name='adm_session_year_idx'),
            models.Index(fields=['status'], name='adm_session_status_idx'),
            models.Index(fields=['application_start_date'], name='adm_session_start_idx'),
            models.Index(fields=['application_end_date'], name='adm_session_end_idx'),
        ]
    
    def __str__(self):
        return f"{self.name} - {self.get_status_display()}"
    
    @property
    def is_application_open(self):
        now = timezone.now()
        return self.application_start_date <= now <= self.application_end_date and self.status == 'active'


class AdmissionProgram(models.Model):
    """
    Programs available for admission in a session
    """
    PROGRAM_TYPE_CHOICES = (
        ('btech', 'B.Tech'),
        ('mtech', 'M.Tech'),
        ('mba', 'MBA'),
        ('mca', 'MCA'),
        ('phd', 'Ph.D'),
        ('diploma', 'Diploma'),
    )
    
    session = models.ForeignKey(AdmissionSession, on_delete=models.CASCADE, related_name='programs')
    program_type = models.CharField(max_length=20, choices=PROGRAM_TYPE_CHOICES)
    program_name = models.CharField(max_length=200)
    department = models.ForeignKey('main_app.Department', on_delete=models.CASCADE)
    
    # Seat Information
    total_seats = models.IntegerField(validators=[MinValueValidator(1)])
    general_seats = models.IntegerField(validators=[MinValueValidator(0)])
    obc_seats = models.IntegerField(validators=[MinValueValidator(0)])
    sc_seats = models.IntegerField(validators=[MinValueValidator(0)])
    st_seats = models.IntegerField(validators=[MinValueValidator(0)])
    ews_seats = models.IntegerField(validators=[MinValueValidator(0)])
    management_seats = models.IntegerField(validators=[MinValueValidator(0)], default=0)
    nri_seats = models.IntegerField(validators=[MinValueValidator(0)], default=0)
    
    # Eligibility Criteria
    min_qualification = models.CharField(max_length=100, help_text="e.g., 10+2 with 60%")
    entrance_exam_required = models.BooleanField(default=True)
    entrance_exam_name = models.CharField(max_length=100, blank=True, help_text="e.g., JEE Main, GATE")
    min_entrance_score = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    
    # Fee Information
    application_fee = models.DecimalField(max_digits=10, decimal_places=2)
    tuition_fee = models.DecimalField(max_digits=10, decimal_places=2)
    development_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    other_fees = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Status
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['session', 'program_type', 'department']
        indexes = [
            models.Index(fields=['session', 'program_type'], name='adm_prog_session_type_idx'),
            models.Index(fields=['department'], name='adm_prog_dept_idx'),
            models.Index(fields=['is_active'], name='adm_prog_active_idx'),
        ]
    
    def __str__(self):
        return f"{self.program_name} - {self.session.name}"
    
    @property
    def total_available_seats(self):
        return (self.general_seats + self.obc_seats + self.sc_seats + 
                self.st_seats + self.ews_seats + self.management_seats + self.nri_seats)
    
    @property
    def total_fee(self):
        return self.tuition_fee + self.development_fee + self.other_fees


class AdmissionApplication(models.Model):
    """
    Student admission applications
    """
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('under_review', 'Under Review'),
        ('shortlisted', 'Shortlisted'),
        ('selected', 'Selected'),
        ('rejected', 'Rejected'),
        ('waitlisted', 'Waitlisted'),
        ('counselling', 'Counselling'),
        ('admitted', 'Admitted'),
        ('withdrawn', 'Withdrawn'),
    )
    
    CATEGORY_CHOICES = (
        ('general', 'General'),
        ('obc', 'OBC'),
        ('sc', 'SC'),
        ('st', 'ST'),
        ('ews', 'EWS'),
    )
    
    GENDER_CHOICES = (
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    )
    
    # Application Details
    application_number = models.CharField(max_length=50, unique=True, default=uuid.uuid4().hex[:12].upper())
    session = models.ForeignKey(AdmissionSession, on_delete=models.CASCADE, related_name='applications')
    program = models.ForeignKey(AdmissionProgram, on_delete=models.CASCADE, related_name='applications')
    
    # Personal Information
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, blank=True)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    nationality = models.CharField(max_length=50, default='Indian')
    category = models.CharField(max_length=10, choices=CATEGORY_CHOICES)
    
    # Contact Information
    email = models.EmailField()
    phone_number = models.CharField(max_length=15)
    alternate_phone = models.CharField(max_length=15, blank=True)
    
    # Address
    permanent_address = models.TextField()
    permanent_city = models.CharField(max_length=100)
    permanent_state = models.CharField(max_length=100)
    permanent_pincode = models.CharField(max_length=10)
    current_address = models.TextField(blank=True)
    current_city = models.CharField(max_length=100, blank=True)
    current_state = models.CharField(max_length=100, blank=True)
    current_pincode = models.CharField(max_length=10, blank=True)
    
    # Academic Information
    tenth_board = models.CharField(max_length=100)
    tenth_school = models.CharField(max_length=200)
    tenth_year = models.IntegerField(validators=[MinValueValidator(1990), MaxValueValidator(2030)])
    tenth_percentage = models.DecimalField(max_digits=5, decimal_places=2, validators=[MinValueValidator(0), MaxValueValidator(100)])
    
    twelfth_board = models.CharField(max_length=100, blank=True)
    twelfth_school = models.CharField(max_length=200, blank=True)
    twelfth_year = models.IntegerField(null=True, blank=True, validators=[MinValueValidator(1990), MaxValueValidator(2030)])
    twelfth_percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, validators=[MinValueValidator(0), MaxValueValidator(100)])
    
    # Entrance Exam Information
    entrance_exam_name = models.CharField(max_length=100, blank=True)
    entrance_exam_year = models.IntegerField(null=True, blank=True)
    entrance_exam_score = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    entrance_exam_rank = models.IntegerField(null=True, blank=True)
    entrance_exam_category_rank = models.IntegerField(null=True, blank=True)
    
    # Guardian Information
    father_name = models.CharField(max_length=200)
    father_occupation = models.CharField(max_length=100, blank=True)
    father_mobile = models.CharField(max_length=15, blank=True)
    mother_name = models.CharField(max_length=200)
    mother_occupation = models.CharField(max_length=100, blank=True)
    mother_mobile = models.CharField(max_length=15, blank=True)
    guardian_name = models.CharField(max_length=200, blank=True)
    guardian_relation = models.CharField(max_length=50, blank=True)
    guardian_mobile = models.CharField(max_length=15, blank=True)
    
    # Application Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    merit_rank = models.IntegerField(null=True, blank=True)
    counselling_rank = models.IntegerField(null=True, blank=True)
    
    # Payment Information
    application_fee_paid = models.BooleanField(default=False)
    application_fee_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    payment_transaction_id = models.CharField(max_length=100, blank=True)
    payment_date = models.DateTimeField(null=True, blank=True)
    
    # Additional Information
    is_physically_disabled = models.BooleanField(default=False)
    disability_percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    blood_group = models.CharField(max_length=5, blank=True)
    aadhaar_number = models.CharField(max_length=12, blank=True)
    
    # Timestamps
    submitted_at = models.DateTimeField(null=True, blank=True)
    last_modified = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Review Information
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_applications')
    reviewed_at = models.DateTimeField(null=True, blank=True)
    review_notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['application_number'], name='adm_app_number_idx'),
            models.Index(fields=['session', 'program'], name='adm_app_session_prog_idx'),
            models.Index(fields=['status'], name='adm_app_status_idx'),
            models.Index(fields=['email'], name='adm_app_email_idx'),
            models.Index(fields=['phone_number'], name='adm_app_phone_idx'),
            models.Index(fields=['merit_rank'], name='adm_app_merit_rank_idx'),
            models.Index(fields=['submitted_at'], name='adm_app_submitted_idx'),
        ]
    
    def __str__(self):
        return f"{self.application_number} - {self.first_name} {self.last_name}"
    
    @property
    def full_name(self):
        if self.middle_name:
            return f"{self.first_name} {self.middle_name} {self.last_name}"
        return f"{self.first_name} {self.last_name}"
    
    @property
    def age(self):
        today = timezone.now().date()
        return today.year - self.date_of_birth.year - ((today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))


class AdmissionDocument(models.Model):
    """
    Documents uploaded with admission applications
    """
    DOCUMENT_TYPE_CHOICES = (
        ('photo', 'Photograph'),
        ('signature', 'Signature'),
        ('tenth_marksheet', '10th Marksheet'),
        ('twelfth_marksheet', '12th Marksheet'),
        ('entrance_scorecard', 'Entrance Exam Scorecard'),
        ('aadhaar_card', 'Aadhaar Card'),
        ('caste_certificate', 'Caste Certificate'),
        ('income_certificate', 'Income Certificate'),
        ('disability_certificate', 'Disability Certificate'),
        ('transfer_certificate', 'Transfer Certificate'),
        ('migration_certificate', 'Migration Certificate'),
        ('character_certificate', 'Character Certificate'),
        ('other', 'Other'),
    )
    
    application = models.ForeignKey(AdmissionApplication, on_delete=models.CASCADE, related_name='documents')
    document_type = models.CharField(max_length=30, choices=DOCUMENT_TYPE_CHOICES)
    document_name = models.CharField(max_length=200)
    file = models.FileField(upload_to='admission_documents/')
    file_size = models.IntegerField(help_text="File size in bytes")
    
    # Verification Status
    is_verified = models.BooleanField(default=False)
    verified_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    verified_at = models.DateTimeField(null=True, blank=True)
    verification_notes = models.TextField(blank=True)
    
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['application', 'document_type'], name='adm_doc_app_type_idx'),
            models.Index(fields=['is_verified'], name='adm_doc_verified_idx'),
            models.Index(fields=['uploaded_at'], name='adm_doc_uploaded_idx'),
        ]
    
    def __str__(self):
        return f"{self.application.application_number} - {self.get_document_type_display()}"


class AdmissionTest(models.Model):
    """
    Entrance exam and interview results
    """
    TEST_TYPE_CHOICES = (
        ('entrance_exam', 'Entrance Exam'),
        ('interview', 'Interview'),
        ('group_discussion', 'Group Discussion'),
        ('written_test', 'Written Test'),
        ('practical_test', 'Practical Test'),
    )
    
    application = models.ForeignKey(AdmissionApplication, on_delete=models.CASCADE, related_name='tests')
    test_type = models.CharField(max_length=20, choices=TEST_TYPE_CHOICES)
    test_name = models.CharField(max_length=100)
    test_date = models.DateTimeField()
    venue = models.CharField(max_length=200, blank=True)
    
    # Scores
    max_score = models.DecimalField(max_digits=8, decimal_places=2)
    obtained_score = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    rank = models.IntegerField(null=True, blank=True)
    
    # Status
    is_passed = models.BooleanField(default=False)
    is_qualified = models.BooleanField(default=False)
    remarks = models.TextField(blank=True)
    
    conducted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['application', 'test_type'], name='adm_test_app_type_idx'),
            models.Index(fields=['test_date'], name='adm_test_date_idx'),
            models.Index(fields=['is_qualified'], name='adm_test_qualified_idx'),
        ]
    
    def __str__(self):
        return f"{self.application.application_number} - {self.test_name}"


class AdmissionPayment(models.Model):
    """
    Payment records for admission applications
    """
    PAYMENT_STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    )
    
    PAYMENT_METHOD_CHOICES = (
        ('online', 'Online Payment'),
        ('card', 'Credit/Debit Card'),
        ('net_banking', 'Net Banking'),
        ('upi', 'UPI'),
        ('wallet', 'Digital Wallet'),
    )
    
    application = models.ForeignKey(AdmissionApplication, on_delete=models.CASCADE, related_name='payments')
    payment_type = models.CharField(max_length=20, default='application_fee')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Payment Details
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    transaction_id = models.CharField(max_length=100, unique=True)
    payment_gateway = models.CharField(max_length=50, blank=True)
    gateway_transaction_id = models.CharField(max_length=100, blank=True)
    
    # Status
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    payment_date = models.DateTimeField(null=True, blank=True)
    
    # Receipt Information
    receipt_number = models.CharField(max_length=50, blank=True)
    receipt_generated = models.BooleanField(default=False)
    
    # Additional Information
    failure_reason = models.TextField(blank=True)
    refund_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    refund_date = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['application'], name='adm_payment_app_idx'),
            models.Index(fields=['transaction_id'], name='adm_payment_txn_idx'),
            models.Index(fields=['status'], name='adm_payment_status_idx'),
            models.Index(fields=['payment_date'], name='adm_payment_date_idx'),
        ]
    
    def __str__(self):
        return f"{self.application.application_number} - {self.transaction_id}"


class AdmissionMeritList(models.Model):
    """
    Merit lists for admission programs
    """
    LIST_TYPE_CHOICES = (
        ('provisional', 'Provisional'),
        ('final', 'Final'),
        ('waitlist', 'Wait List'),
        ('counselling', 'Counselling List'),
    )
    
    program = models.ForeignKey(AdmissionProgram, on_delete=models.CASCADE, related_name='merit_lists')
    list_type = models.CharField(max_length=20, choices=LIST_TYPE_CHOICES)
    list_name = models.CharField(max_length=200)
    published_date = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['program', 'list_type'], name='adm_merit_prog_type_idx'),
            models.Index(fields=['published_date'], name='adm_merit_published_idx'),
            models.Index(fields=['is_active'], name='adm_merit_active_idx'),
        ]
    
    def __str__(self):
        return f"{self.program} - {self.list_name}"


class AdmissionMeritEntry(models.Model):
    """
    Individual entries in merit lists
    """
    merit_list = models.ForeignKey(AdmissionMeritList, on_delete=models.CASCADE, related_name='entries')
    application = models.ForeignKey(AdmissionApplication, on_delete=models.CASCADE)
    rank = models.IntegerField()
    score = models.DecimalField(max_digits=8, decimal_places=2)
    category_rank = models.IntegerField(null=True, blank=True)
    
    # Counselling Information
    counselling_attended = models.BooleanField(default=False)
    counselling_date = models.DateTimeField(null=True, blank=True)
    seat_allotted = models.BooleanField(default=False)
    seat_category = models.CharField(max_length=20, blank=True)
    
    # Admission Status
    admission_offered = models.BooleanField(default=False)
    admission_accepted = models.BooleanField(default=False)
    admission_declined = models.BooleanField(default=False)
    admission_withdrawn = models.BooleanField(default=False)
    
    remarks = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['rank']
        unique_together = ['merit_list', 'application']
        indexes = [
            models.Index(fields=['merit_list', 'rank'], name='adm_merit_entry_rank_idx'),
            models.Index(fields=['application'], name='adm_merit_entry_app_idx'),
            models.Index(fields=['counselling_attended'], name='adm_merit_counselling_idx'),
            models.Index(fields=['seat_allotted'], name='adm_merit_entry_seat_idx'),
        ]
    
    def __str__(self):
        return f"{self.merit_list} - Rank {self.rank} - {self.application.application_number}"


