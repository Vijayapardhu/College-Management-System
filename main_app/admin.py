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
admin.site.register(Student)
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
admin.site.register(Timetable)

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
