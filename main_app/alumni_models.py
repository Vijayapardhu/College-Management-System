"""
Enhanced Alumni Management Models for College ERP
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from decimal import Decimal
import uuid

User = get_user_model()


class AlumniAchievement(models.Model):
    """
    Alumni achievements and recognitions
    """
    ACHIEVEMENT_TYPES = (
        ('academic', 'Academic Excellence'),
        ('professional', 'Professional Achievement'),
        ('entrepreneurial', 'Entrepreneurial Success'),
        ('social', 'Social Impact'),
        ('award', 'Award/Recognition'),
        ('publication', 'Research Publication'),
        ('patent', 'Patent/Innovation'),
        ('leadership', 'Leadership Role'),
        ('other', 'Other'),
    )
    
    alumni = models.ForeignKey('Alumni', on_delete=models.CASCADE, related_name='alumni_achievements')
    title = models.CharField(max_length=200, help_text="Achievement title")
    description = models.TextField(help_text="Detailed description of the achievement")
    achievement_type = models.CharField(max_length=20, choices=ACHIEVEMENT_TYPES)
    
    # Dates
    achieved_date = models.DateField()
    announced_date = models.DateField(null=True, blank=True)
    
    # Recognition details
    awarding_body = models.CharField(max_length=200, blank=True, help_text="Organization that recognized the achievement")
    award_level = models.CharField(max_length=100, blank=True, help_text="National, International, etc.")
    
    # Media
    certificate_image = models.ImageField(upload_to='alumni/achievements/', blank=True, null=True)
    supporting_documents = models.FileField(upload_to='alumni/achievements/docs/', blank=True, null=True)
    
    # Verification
    is_verified = models.BooleanField(default=False)
    verified_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    verified_at = models.DateTimeField(null=True, blank=True)
    
    # Visibility
    is_public = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-achieved_date']
        indexes = [
            models.Index(fields=['alumni', 'achieved_date'], name='alumni_ach_alumni_date_idx'),
            models.Index(fields=['achievement_type'], name='alumni_ach_type_idx'),
            models.Index(fields=['is_verified'], name='alumni_ach_verified_idx'),
            models.Index(fields=['is_featured'], name='alumni_ach_featured_idx'),
        ]
    
    def __str__(self):
        return f"{self.alumni} - {self.title}"


class AlumniEvent(models.Model):
    """
    Alumni events (reunions, networking, seminars)
    """
    EVENT_TYPES = (
        ('reunion', 'Reunion'),
        ('networking', 'Networking Event'),
        ('seminar', 'Seminar/Workshop'),
        ('conference', 'Conference'),
        ('social', 'Social Gathering'),
        ('fundraising', 'Fundraising Event'),
        ('mentorship', 'Mentorship Session'),
        ('career', 'Career Fair'),
        ('cultural', 'Cultural Event'),
        ('sports', 'Sports Event'),
        ('other', 'Other'),
    )
    
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('ongoing', 'Ongoing'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )
    
    event_id = models.UUIDField(default=uuid.uuid4, unique=True)
    title = models.CharField(max_length=200)
    description = models.TextField()
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES)
    
    # Event details
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    registration_deadline = models.DateTimeField(null=True, blank=True)
    
    # Location
    venue = models.CharField(max_length=200)
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    country = models.CharField(max_length=100, default='India')
    is_online = models.BooleanField(default=False)
    online_link = models.URLField(blank=True, null=True)
    
    # Capacity and pricing
    max_participants = models.IntegerField(null=True, blank=True)
    registration_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_free = models.BooleanField(default=True)
    
    # Organizer
    organized_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='organized_events')
    co_organizers = models.ManyToManyField(User, blank=True, related_name='co_organized_events')
    contact_email = models.EmailField()
    contact_phone = models.CharField(max_length=15, blank=True)
    
    # Media
    event_image = models.ImageField(upload_to='alumni/events/', blank=True, null=True)
    event_banner = models.ImageField(upload_to='alumni/events/banners/', blank=True, null=True)
    
    # Status and visibility
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    is_featured = models.BooleanField(default=False)
    requires_approval = models.BooleanField(default=False)
    
    # Additional information
    agenda = models.TextField(blank=True, help_text="Event agenda or schedule")
    requirements = models.TextField(blank=True, help_text="What participants should bring")
    benefits = models.TextField(blank=True, help_text="Benefits of attending")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-start_date']
        indexes = [
            models.Index(fields=['start_date'], name='alumni_event_start_date_idx'),
            models.Index(fields=['event_type'], name='alumni_event_type_idx'),
            models.Index(fields=['status'], name='alumni_event_status_idx'),
            models.Index(fields=['is_featured'], name='alumni_event_featured_idx'),
            models.Index(fields=['city', 'state'], name='alumni_event_location_idx'),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.start_date.strftime('%d %b %Y')}"
    
    @property
    def is_registration_open(self):
        """Check if registration is still open"""
        if not self.registration_deadline:
            return self.status == 'published' and timezone.now() < self.start_date
        return (self.status == 'published' and 
                timezone.now() < self.registration_deadline and 
                timezone.now() < self.start_date)
    
    @property
    def registered_count(self):
        """Get number of registered participants"""
        return self.registrations.filter(status='confirmed').count()
    
    @property
    def available_spots(self):
        """Get available spots for registration"""
        if not self.max_participants:
            return None
        return max(0, self.max_participants - self.registered_count)


class AlumniEventRegistration(models.Model):
    """
    Alumni event registrations
    """
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('waitlisted', 'Waitlisted'),
        ('attended', 'Attended'),
        ('no_show', 'No Show'),
    )
    
    event = models.ForeignKey(AlumniEvent, on_delete=models.CASCADE, related_name='registrations')
    alumni = models.ForeignKey('Alumni', on_delete=models.CASCADE, related_name='event_registrations')
    
    # Registration details
    registration_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Payment
    registration_fee_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    payment_method = models.CharField(max_length=50, blank=True)
    payment_reference = models.CharField(max_length=100, blank=True)
    payment_date = models.DateTimeField(null=True, blank=True)
    
    # Additional information
    dietary_requirements = models.TextField(blank=True)
    accommodation_required = models.BooleanField(default=False)
    transportation_required = models.BooleanField(default=False)
    emergency_contact = models.CharField(max_length=100, blank=True)
    emergency_phone = models.CharField(max_length=15, blank=True)
    
    # Check-in
    checked_in = models.BooleanField(default=False)
    check_in_time = models.DateTimeField(null=True, blank=True)
    check_in_notes = models.TextField(blank=True)
    
    # Feedback
    feedback_rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        null=True, blank=True
    )
    feedback_comments = models.TextField(blank=True)
    feedback_date = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-registration_date']
        indexes = [
            models.Index(fields=['event', 'alumni'], name='alumni_reg_event_alumni_idx'),
            models.Index(fields=['status'], name='alumni_reg_status_idx'),
            models.Index(fields=['registration_date'], name='alumni_reg_date_idx'),
        ]
        unique_together = ['event', 'alumni']
    
    def __str__(self):
        return f"{self.alumni} - {self.event.title}"


class AlumniDonation(models.Model):
    """
    Alumni donations and fundraising campaigns
    """
    DONATION_TYPES = (
        ('general', 'General Fund'),
        ('scholarship', 'Scholarship Fund'),
        ('infrastructure', 'Infrastructure Development'),
        ('research', 'Research Fund'),
        ('library', 'Library Fund'),
        ('sports', 'Sports Fund'),
        ('cultural', 'Cultural Activities'),
        ('emergency', 'Emergency Fund'),
        ('specific', 'Specific Project'),
        ('other', 'Other'),
    )
    
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('paused', 'Paused'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )
    
    campaign_id = models.UUIDField(default=uuid.uuid4, unique=True)
    title = models.CharField(max_length=200)
    description = models.TextField()
    donation_type = models.CharField(max_length=20, choices=DONATION_TYPES)
    
    # Campaign details
    target_amount = models.DecimalField(max_digits=12, decimal_places=2)
    current_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    minimum_donation = models.DecimalField(max_digits=10, decimal_places=2, default=100)
    
    # Dates
    start_date = models.DateTimeField()
    end_date = models.DateTimeField(null=True, blank=True)
    
    # Organizer
    organized_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='organized_campaigns')
    contact_email = models.EmailField()
    contact_phone = models.CharField(max_length=15, blank=True)
    
    # Media
    campaign_image = models.ImageField(upload_to='alumni/donations/', blank=True, null=True)
    campaign_video = models.FileField(upload_to='alumni/donations/videos/', blank=True, null=True)
    
    # Status and visibility
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    is_featured = models.BooleanField(default=False)
    is_anonymous_allowed = models.BooleanField(default=True)
    
    # Additional information
    impact_description = models.TextField(blank=True, help_text="How donations will be used")
    recognition_levels = models.JSONField(default=dict, blank=True, help_text="Recognition tiers based on donation amount")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-start_date']
        indexes = [
            models.Index(fields=['start_date'], name='alumni_don_start_date_idx'),
            models.Index(fields=['donation_type'], name='alumni_don_type_idx'),
            models.Index(fields=['status'], name='alumni_don_status_idx'),
            models.Index(fields=['is_featured'], name='alumni_don_featured_idx'),
        ]
    
    def __str__(self):
        return f"{self.title} - ₹{self.current_amount}/{self.target_amount}"
    
    @property
    def progress_percentage(self):
        """Calculate donation progress percentage"""
        if self.target_amount <= 0:
            return 0
        return min(100, (self.current_amount / self.target_amount) * 100)
    
    @property
    def is_active(self):
        """Check if campaign is currently active"""
        now = timezone.now()
        return (self.status == 'active' and 
                now >= self.start_date and 
                (not self.end_date or now <= self.end_date))
    
    @property
    def donor_count(self):
        """Get number of unique donors"""
        return self.donations.filter(status='completed').values('donor').distinct().count()


class AlumniDonationTransaction(models.Model):
    """
    Individual donation transactions
    """
    PAYMENT_STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
    )
    
    PAYMENT_METHODS = (
        ('online', 'Online Payment'),
        ('upi', 'UPI'),
        ('card', 'Credit/Debit Card'),
        ('netbanking', 'Net Banking'),
        ('wallet', 'Digital Wallet'),
        ('cheque', 'Cheque'),
        ('cash', 'Cash'),
        ('bank_transfer', 'Bank Transfer'),
        ('other', 'Other'),
    )
    
    campaign = models.ForeignKey(AlumniDonation, on_delete=models.CASCADE, related_name='donations')
    donor = models.ForeignKey('Alumni', on_delete=models.CASCADE, related_name='donations')
    
    # Transaction details
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    
    # Payment gateway details
    transaction_id = models.CharField(max_length=100, blank=True)
    payment_gateway_response = models.JSONField(default=dict, blank=True)
    
    # Anonymity
    is_anonymous = models.BooleanField(default=False)
    donor_name_display = models.CharField(max_length=100, blank=True, help_text="Name to display publicly")
    
    # Messages
    donor_message = models.TextField(blank=True, help_text="Message from donor")
    acknowledgment_sent = models.BooleanField(default=False)
    
    # Dates
    donation_date = models.DateTimeField(auto_now_add=True)
    payment_date = models.DateTimeField(null=True, blank=True)
    
    # Receipt
    receipt_number = models.CharField(max_length=50, blank=True)
    receipt_generated = models.BooleanField(default=False)
    receipt_sent = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-donation_date']
        indexes = [
            models.Index(fields=['campaign', 'donation_date'], name='alumni_don_txn_campaign_idx'),
            models.Index(fields=['donor'], name='alumni_don_txn_donor_idx'),
            models.Index(fields=['payment_status'], name='alumni_don_txn_status_idx'),
            models.Index(fields=['donation_date'], name='alumni_don_txn_date_idx'),
        ]
    
    def __str__(self):
        return f"{self.donor} - ₹{self.amount} - {self.campaign.title}"


class AlumniMentorship(models.Model):
    """
    Mentorship program connecting alumni with current students
    """
    MENTORSHIP_TYPES = (
        ('academic', 'Academic Guidance'),
        ('career', 'Career Guidance'),
        ('entrepreneurship', 'Entrepreneurship'),
        ('personal', 'Personal Development'),
        ('technical', 'Technical Skills'),
        ('leadership', 'Leadership Development'),
        ('research', 'Research Guidance'),
        ('other', 'Other'),
    )
    
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('paused', 'Paused'),
    )
    
    mentorship_id = models.UUIDField(default=uuid.uuid4, unique=True)
    mentor = models.ForeignKey('Alumni', on_delete=models.CASCADE, related_name='mentorship_roles')
    mentee = models.ForeignKey('Student', on_delete=models.CASCADE, related_name='mentorship_relationships')
    
    # Mentorship details
    mentorship_type = models.CharField(max_length=20, choices=MENTORSHIP_TYPES)
    title = models.CharField(max_length=200, help_text="Mentorship title or focus area")
    description = models.TextField(help_text="Mentorship objectives and scope")
    
    # Duration
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    expected_duration_months = models.IntegerField(null=True, blank=True)
    
    # Status and progress
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    progress_percentage = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        default=0
    )
    
    # Communication
    preferred_communication_method = models.CharField(
        max_length=50,
        choices=[
            ('email', 'Email'),
            ('phone', 'Phone'),
            ('video_call', 'Video Call'),
            ('in_person', 'In Person'),
            ('multiple', 'Multiple Methods'),
        ],
        default='email'
    )
    meeting_frequency = models.CharField(
        max_length=50,
        choices=[
            ('weekly', 'Weekly'),
            ('biweekly', 'Bi-weekly'),
            ('monthly', 'Monthly'),
            ('quarterly', 'Quarterly'),
            ('as_needed', 'As Needed'),
        ],
        default='monthly'
    )
    
    # Goals and outcomes
    goals = models.JSONField(default=list, blank=True, help_text="List of mentorship goals")
    outcomes = models.TextField(blank=True, help_text="Achieved outcomes and results")
    
    # Feedback
    mentor_feedback = models.TextField(blank=True)
    mentee_feedback = models.TextField(blank=True)
    overall_rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        null=True, blank=True
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-start_date']
        indexes = [
            models.Index(fields=['mentor', 'status'], name='alumni_mentor_mentor_idx'),
            models.Index(fields=['mentee', 'status'], name='alumni_mentor_mentee_idx'),
            models.Index(fields=['mentorship_type'], name='alumni_mentor_type_idx'),
            models.Index(fields=['start_date'], name='alumni_mentor_start_idx'),
        ]
        unique_together = ['mentor', 'mentee', 'start_date']
    
    def __str__(self):
        return f"{self.mentor} mentors {self.mentee} - {self.title}"


class AlumniJob(models.Model):
    """
    Job opportunities shared by alumni
    """
    JOB_TYPES = (
        ('full_time', 'Full Time'),
        ('part_time', 'Part Time'),
        ('contract', 'Contract'),
        ('internship', 'Internship'),
        ('freelance', 'Freelance'),
        ('consulting', 'Consulting'),
    )
    
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('closed', 'Closed'),
        ('expired', 'Expired'),
    )
    
    job_id = models.UUIDField(default=uuid.uuid4, unique=True)
    posted_by = models.ForeignKey('Alumni', on_delete=models.CASCADE, related_name='posted_jobs')
    
    # Job details
    title = models.CharField(max_length=200)
    company = models.CharField(max_length=200)
    location = models.CharField(max_length=200)
    job_type = models.CharField(max_length=20, choices=JOB_TYPES)
    
    # Description
    job_description = models.TextField()
    requirements = models.TextField()
    responsibilities = models.TextField()
    benefits = models.TextField(blank=True)
    
    # Compensation
    salary_range_min = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    salary_range_max = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    currency = models.CharField(max_length=3, default='INR')
    is_salary_negotiable = models.BooleanField(default=False)
    
    # Application details
    application_deadline = models.DateField(null=True, blank=True)
    application_email = models.EmailField()
    application_url = models.URLField(blank=True, null=True)
    contact_person = models.CharField(max_length=100)
    contact_phone = models.CharField(max_length=15, blank=True)
    
    # Status and visibility
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    is_featured = models.BooleanField(default=False)
    is_urgent = models.BooleanField(default=False)
    
    # Additional information
    experience_required = models.CharField(max_length=100, blank=True)
    skills_required = models.JSONField(default=list, blank=True)
    education_required = models.CharField(max_length=100, blank=True)
    
    # Dates
    posted_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-posted_date']
        indexes = [
            models.Index(fields=['posted_by'], name='alumni_job_posted_by_idx'),
            models.Index(fields=['job_type'], name='alumni_job_type_idx'),
            models.Index(fields=['status'], name='alumni_job_status_idx'),
            models.Index(fields=['is_featured'], name='alumni_job_featured_idx'),
            models.Index(fields=['posted_date'], name='alumni_job_posted_date_idx'),
        ]
    
    def __str__(self):
        return f"{self.title} at {self.company} - {self.posted_by}"
    
    @property
    def is_active(self):
        """Check if job posting is still active"""
        if self.status != 'published':
            return False
        if self.application_deadline:
            return timezone.now().date() <= self.application_deadline
        return True


class AlumniNewsletter(models.Model):
    """
    Alumni newsletter and communication system
    """
    NEWSLETTER_TYPES = (
        ('monthly', 'Monthly Newsletter'),
        ('quarterly', 'Quarterly Newsletter'),
        ('special', 'Special Edition'),
        ('event', 'Event Announcement'),
        ('achievement', 'Achievement Update'),
        ('fundraising', 'Fundraising Update'),
        ('general', 'General Update'),
    )
    
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('scheduled', 'Scheduled'),
        ('sent', 'Sent'),
        ('failed', 'Failed'),
    )
    
    newsletter_id = models.UUIDField(default=uuid.uuid4, unique=True)
    title = models.CharField(max_length=200)
    newsletter_type = models.CharField(max_length=20, choices=NEWSLETTER_TYPES)
    
    # Content
    content = models.TextField()
    html_content = models.TextField(blank=True, help_text="HTML formatted content")
    
    # Sender
    sent_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_newsletters')
    
    # Scheduling
    scheduled_date = models.DateTimeField(null=True, blank=True)
    sent_date = models.DateTimeField(null=True, blank=True)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    
    # Recipients
    recipient_count = models.IntegerField(default=0)
    opened_count = models.IntegerField(default=0)
    clicked_count = models.IntegerField(default=0)
    
    # Media
    featured_image = models.ImageField(upload_to='alumni/newsletters/', blank=True, null=True)
    attachments = models.JSONField(default=list, blank=True, help_text="List of attachment URLs")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['newsletter_type'], name='alumni_newsletter_type_idx'),
            models.Index(fields=['status'], name='alumni_newsletter_status_idx'),
            models.Index(fields=['scheduled_date'], name='alumni_newsletter_sched_idx'),
            models.Index(fields=['sent_date'], name='alumni_newsletter_sent_idx'),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.get_newsletter_type_display()}"
    
    @property
    def open_rate(self):
        """Calculate open rate percentage"""
        if self.recipient_count <= 0:
            return 0
        return (self.opened_count / self.recipient_count) * 100
    
    @property
    def click_rate(self):
        """Calculate click rate percentage"""
        if self.recipient_count <= 0:
            return 0
        return (self.clicked_count / self.recipient_count) * 100


