"""
Audit logging models for tracking sensitive operations
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.utils import timezone
import json

User = get_user_model()


class AuditLog(models.Model):
    """
    Audit log for tracking all sensitive operations
    """
    
    ACTION_TYPES = (
        ('create', 'Create'),
        ('read', 'Read'),
        ('update', 'Update'),
        ('delete', 'Delete'),
        ('login', 'Login'),
        ('logout', 'Logout'),
        ('password_change', 'Password Change'),
        ('permission_change', 'Permission Change'),
        ('data_export', 'Data Export'),
        ('bulk_operation', 'Bulk Operation'),
        ('file_upload', 'File Upload'),
        ('file_download', 'File Download'),
        ('payment', 'Payment'),
        ('grade_change', 'Grade Change'),
        ('attendance_override', 'Attendance Override'),
        ('fee_waiver', 'Fee Waiver'),
        ('scholarship_approval', 'Scholarship Approval'),
        ('disciplinary_action', 'Disciplinary Action'),
        ('system_config', 'System Configuration'),
    )
    
    SEVERITY_LEVELS = (
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    )
    
    # Basic audit information
    timestamp = models.DateTimeField(default=timezone.now, db_index=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='audit_logs')
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    session_key = models.CharField(max_length=40, blank=True)
    
    # Action details
    action_type = models.CharField(max_length=50, choices=ACTION_TYPES, db_index=True)
    severity = models.CharField(max_length=20, choices=SEVERITY_LEVELS, default='medium')
    description = models.TextField()
    
    # Object information (for CRUD operations)
    content_type = models.ForeignKey(ContentType, on_delete=models.SET_NULL, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    
    # Additional data
    old_values = models.JSONField(null=True, blank=True, help_text="Previous values for updates")
    new_values = models.JSONField(null=True, blank=True, help_text="New values for creates/updates")
    metadata = models.JSONField(null=True, blank=True, help_text="Additional context data")
    
    # Request information
    request_path = models.CharField(max_length=500, blank=True)
    request_method = models.CharField(max_length=10, blank=True)
    
    # Status
    success = models.BooleanField(default=True, db_index=True)
    error_message = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['timestamp'], name='audit_log_time_idx'),
            models.Index(fields=['user', 'timestamp'], name='audit_log_user_time_idx'),
            models.Index(fields=['action_type', 'timestamp'], name='audit_log_action_time_idx'),
            models.Index(fields=['severity', 'timestamp'], name='audit_log_severity_time_idx'),
            models.Index(fields=['ip_address', 'timestamp'], name='audit_log_ip_time_idx'),
            models.Index(fields=['success', 'timestamp'], name='audit_log_success_time_idx'),
        ]
        verbose_name = "Audit Log Entry"
        verbose_name_plural = "Audit Log Entries"
    
    def __str__(self):
        user_str = self.user.username if self.user else 'Anonymous'
        return f"{self.timestamp} - {user_str} - {self.get_action_type_display()} - {self.description[:50]}"
    
    @classmethod
    def log_action(cls, user, action_type, description, **kwargs):
        """
        Convenience method to create audit log entries
        """
        return cls.objects.create(
            user=user,
            action_type=action_type,
            description=description,
            **kwargs
        )
    
    @classmethod
    def log_crud_action(cls, user, action_type, obj, old_values=None, new_values=None, **kwargs):
        """
        Log CRUD operations with object details
        """
        content_type = ContentType.objects.get_for_model(obj)
        
        return cls.objects.create(
            user=user,
            action_type=action_type,
            content_type=content_type,
            object_id=obj.pk,
            description=f"{action_type.title()} {content_type.model}: {obj}",
            old_values=old_values,
            new_values=new_values,
            **kwargs
        )


class SecurityEvent(models.Model):
    """
    Track security-related events and anomalies
    """
    
    EVENT_TYPES = (
        ('failed_login', 'Failed Login Attempt'),
        ('multiple_failed_logins', 'Multiple Failed Logins'),
        ('suspicious_request', 'Suspicious Request'),
        ('unauthorized_access', 'Unauthorized Access Attempt'),
        ('data_breach_attempt', 'Data Breach Attempt'),
        ('sql_injection_attempt', 'SQL Injection Attempt'),
        ('xss_attempt', 'XSS Attempt'),
        ('file_upload_attempt', 'Malicious File Upload'),
        ('rate_limit_exceeded', 'Rate Limit Exceeded'),
        ('concurrent_session_limit', 'Concurrent Session Limit'),
        ('admin_access_denied', 'Admin Access Denied'),
        ('bulk_data_access', 'Bulk Data Access'),
        ('export_large_dataset', 'Large Dataset Export'),
        ('permission_escalation', 'Permission Escalation Attempt'),
        ('session_hijack_attempt', 'Session Hijack Attempt'),
    )
    
    SEVERITY_LEVELS = (
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    )
    
    # Event details
    timestamp = models.DateTimeField(default=timezone.now, db_index=True)
    event_type = models.CharField(max_length=50, choices=EVENT_TYPES, db_index=True)
    severity = models.CharField(max_length=20, choices=SEVERITY_LEVELS, db_index=True)
    
    # User and IP information
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True, db_index=True)
    user_agent = models.TextField(blank=True)
    session_key = models.CharField(max_length=40, blank=True)
    
    # Event details
    description = models.TextField()
    request_path = models.CharField(max_length=500, blank=True)
    request_method = models.CharField(max_length=10, blank=True)
    request_data = models.JSONField(null=True, blank=True)
    
    # Response information
    response_status = models.IntegerField(null=True, blank=True)
    response_message = models.TextField(blank=True)
    
    # Additional context
    metadata = models.JSONField(null=True, blank=True)
    
    # Resolution
    is_resolved = models.BooleanField(default=False, db_index=True)
    resolved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='resolved_security_events')
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolution_notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['timestamp'], name='sec_event_time_idx'),
            models.Index(fields=['event_type', 'timestamp'], name='sec_event_type_time_idx'),
            models.Index(fields=['severity', 'timestamp'], name='sec_event_sev_time_idx'),
            models.Index(fields=['ip_address', 'timestamp'], name='sec_event_ip_time_idx'),
            models.Index(fields=['is_resolved', 'timestamp'], name='sec_event_res_time_idx'),
        ]
        verbose_name = "Security Event"
        verbose_name_plural = "Security Events"
    
    def __str__(self):
        user_str = self.user.username if self.user else 'Anonymous'
        return f"{self.timestamp} - {self.get_event_type_display()} - {user_str} - {self.ip_address}"
    
    def resolve(self, resolved_by, notes=""):
        """Mark event as resolved"""
        self.is_resolved = True
        self.resolved_by = resolved_by
        self.resolved_at = timezone.now()
        self.resolution_notes = notes
        self.save()
    
    @classmethod
    def create_event(cls, event_type, severity, description, **kwargs):
        """
        Convenience method to create security events
        """
        return cls.objects.create(
            event_type=event_type,
            severity=severity,
            description=description,
            **kwargs
        )


class DataAccessLog(models.Model):
    """
    Log access to sensitive data
    """
    
    ACCESS_TYPES = (
        ('view', 'View'),
        ('export', 'Export'),
        ('print', 'Print'),
        ('download', 'Download'),
        ('bulk_access', 'Bulk Access'),
    )
    
    DATA_TYPES = (
        ('student_personal', 'Student Personal Data'),
        ('staff_personal', 'Staff Personal Data'),
        ('financial', 'Financial Data'),
        ('academic_records', 'Academic Records'),
        ('attendance_data', 'Attendance Data'),
        ('exam_results', 'Exam Results'),
        ('fee_records', 'Fee Records'),
        ('library_records', 'Library Records'),
        ('placement_data', 'Placement Data'),
        ('medical_records', 'Medical Records'),
        ('disciplinary_records', 'Disciplinary Records'),
    )
    
    # Access details
    timestamp = models.DateTimeField(default=timezone.now, db_index=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='data_access_logs')
    access_type = models.CharField(max_length=20, choices=ACCESS_TYPES)
    data_type = models.CharField(max_length=30, choices=DATA_TYPES)
    
    # Object information
    content_type = models.ForeignKey(ContentType, on_delete=models.SET_NULL, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    
    # Access details
    record_count = models.IntegerField(default=1, help_text="Number of records accessed")
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    session_key = models.CharField(max_length=40, blank=True)
    
    # Additional context
    reason = models.TextField(blank=True, help_text="Reason for access")
    metadata = models.JSONField(null=True, blank=True)
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['timestamp'], name='data_access_time_idx'),
            models.Index(fields=['user', 'timestamp'], name='data_access_user_time_idx'),
            models.Index(fields=['data_type', 'timestamp'], name='data_access_data_type_idx'),
            models.Index(fields=['access_type', 'timestamp'], name='data_access_access_type_idx'),
            models.Index(fields=['ip_address', 'timestamp'], name='data_access_ip_time_idx'),
        ]
        verbose_name = "Data Access Log"
        verbose_name_plural = "Data Access Logs"
    
    def __str__(self):
        return f"{self.timestamp} - {self.user.username} - {self.get_access_type_display()} - {self.get_data_type_display()}"
    
    @classmethod
    def log_access(cls, user, access_type, data_type, **kwargs):
        """
        Convenience method to log data access
        """
        return cls.objects.create(
            user=user,
            access_type=access_type,
            data_type=data_type,
            **kwargs
        )


