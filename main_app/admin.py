from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import *
# Register your models here.


class UserModel(UserAdmin):
    ordering = ('email',)


admin.site.register(CustomUser, UserModel)
admin.site.register(Admin)
admin.site.register(Management)
admin.site.register(Staff)
@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('admin', 'roll_number', 'course', 'department', 'current_semester')
    search_fields = ('admin__first_name', 'admin__last_name', 'roll_number', 'admin__email')
    list_filter = ('department', 'course', 'current_semester', 'student_status')
admin.site.register(Course)
admin.site.register(Subject)
admin.site.register(Session)

# Proctor System
admin.site.register(ProctorAssignment)

# Event Management
admin.site.register(Event)
admin.site.register(EventParticipation)

# Messaging
admin.site.register(Message)

# WhatsApp-like Chat System
admin.site.register(ChatGroup)
admin.site.register(ChatGroupMember)
admin.site.register(ChatMessage)
admin.site.register(MessageAttachment)
admin.site.register(MessageReadReceipt)
admin.site.register(ChatConversation)

# Attendance
admin.site.register(Attendance)
admin.site.register(AttendanceReport)

# Results
admin.site.register(StudentResult)

# Leave Reports
admin.site.register(LeaveReportStudent)
admin.site.register(LeaveReportStaff)

# Feedback
@admin.register(FeedbackStudent)
class FeedbackStudentAdmin(admin.ModelAdmin):
    list_display = ['student', 'category', 'rating', 'has_reply', 'created_at']
    list_filter = ['category', 'rating', 'created_at']
    search_fields = ['student__admin__first_name', 'student__admin__last_name', 'feedback']
    readonly_fields = ['created_at', 'updated_at']
    
    def has_reply(self, obj):
        return bool(obj.reply)
    has_reply.boolean = True
    has_reply.short_description = 'Replied'

@admin.register(FeedbackStaff)
class FeedbackStaffAdmin(admin.ModelAdmin):
    list_display = ['staff', 'has_reply', 'created_at']
    list_filter = ['created_at']
    search_fields = ['staff__admin__first_name', 'staff__admin__last_name', 'feedback']
    readonly_fields = ['created_at', 'updated_at']
    
    def has_reply(self, obj):
        return bool(obj.reply)
    has_reply.boolean = True
    has_reply.short_description = 'Replied'

# Notifications
admin.site.register(NotificationStudent)
admin.site.register(NotificationStaff)

# Study Materials & Resources
admin.site.register(StudyMaterial)
admin.site.register(ResourceRating)
admin.site.register(ResourceBookmark)
admin.site.register(ResourceDownloadLog)

# Assignments
admin.site.register(Assignment)
admin.site.register(AssignmentSubmission)

# Announcements & Discussions
admin.site.register(Announcement)
admin.site.register(Discussion)
admin.site.register(DiscussionReply)

# University Management
admin.site.register(Department)
admin.site.register(Program)
# New academic linkage models
@admin.register(ClassGroup)
class ClassGroupAdmin(admin.ModelAdmin):
    list_display = ('department', 'course', 'academic_year', 'section', 'session', 'class_teacher', 'proctor', 'is_active')
    list_filter = ('department', 'course', 'academic_year', 'section', 'session', 'is_active')
    search_fields = ('department__name', 'course__name', 'section__name', 'session__session_name')

@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('student', 'subject', 'enrolled_at')
    list_filter = ('subject__department', 'subject__semester')
    search_fields = ('student__admin__first_name', 'student__admin__last_name', 'subject__name')

@admin.register(Curriculum)
class CurriculumAdmin(admin.ModelAdmin):
    list_display = ('session_year', 'version', 'is_active', 'created_at')
    list_filter = ('session_year', 'is_active')
    search_fields = ('version',)

@admin.register(Marks)
class MarksAdmin(admin.ModelAdmin):
    list_display = ('student', 'subject', 'assessment_type', 'marks_obtained', 'total_marks', 'assessed_on')
    list_filter = ('assessment_type', 'subject__department', 'subject__semester')
    search_fields = ('student__admin__first_name', 'student__admin__last_name', 'subject__name')
admin.site.register(Hostel)
admin.site.register(HostelAllocation)
admin.site.register(HostelVisitorLog)
admin.site.register(Transport)
admin.site.register(TransportAllocation)
admin.site.register(FeeStructure)
admin.site.register(FeePayment)
admin.site.register(Scholarship)
admin.site.register(ScholarshipApplication)
admin.site.register(SemesterResult)
admin.site.register(SubjectResult)
admin.site.register(Library)
admin.site.register(LibraryIssue)

# Exam Management
admin.site.register(Exam)
admin.site.register(ExamSchedule)
admin.site.register(Invigilator)
admin.site.register(AdmitCard)
@admin.register(Timetable)
class TimetableAdmin(admin.ModelAdmin):
    list_display = ('session', 'course', 'semester', 'department', 'class_group', 'weekday', 'period', 'subject', 'staff')
    list_filter = ('session', 'course', 'semester', 'department', 'class_group', 'weekday')
    search_fields = ('subject__name', 'staff__admin__first_name', 'staff__admin__last_name')

# Placement Cell
admin.site.register(Company)
admin.site.register(PlacementDrive)
admin.site.register(PlacementApplication)

# Grievance & Activity
admin.site.register(Grievance)
admin.site.register(ActivityLog)

# New ECAP Features
admin.site.register(ParentGuardian)
admin.site.register(OnlineExam)
admin.site.register(OnlineExamQuestion)
admin.site.register(OnlineExamAttempt)
admin.site.register(Certificate)
admin.site.register(Alumni)
admin.site.register(Internship)
admin.site.register(MedicalRecord)
admin.site.register(GatePass)
admin.site.register(DisciplinaryAction)
admin.site.register(SportsActivity)
admin.site.register(ActivityParticipation)
admin.site.register(Research)
admin.site.register(AntiRaggingCommittee)
admin.site.register(StudentCouncil)

# Classroom Management
admin.site.register(Classroom)
admin.site.register(ClassroomBooking)
admin.site.register(ClassroomMaintenance)

# OTP Authentication
admin.site.register(OTP)
