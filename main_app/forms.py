from django import forms
from django.forms.widgets import DateInput, TextInput

from .models import *


class FormSettings(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(FormSettings, self).__init__(*args, **kwargs)
        # Here make some changes such as:
        for field in self.visible_fields():
            field.field.widget.attrs['class'] = 'form-control'


class CustomUserForm(FormSettings):
    email = forms.EmailField(required=True)
    gender = forms.ChoiceField(choices=[('M', 'Male'), ('F', 'Female')])
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    address = forms.CharField(widget=forms.Textarea)
    password = forms.CharField(widget=forms.PasswordInput)
    widget = {
        'password': forms.PasswordInput(),
    }

    def __init__(self, *args, **kwargs):
        super(CustomUserForm, self).__init__(*args, **kwargs)

        if kwargs.get('instance'):
            instance = kwargs.get('instance').admin.__dict__
            self.fields['password'].required = False
            for field in CustomUserForm.Meta.fields:
                self.fields[field].initial = instance.get(field)
            if self.instance.pk is not None:
                self.fields['password'].widget.attrs['placeholder'] = "Fill this only if you wish to update password"

    def clean_email(self, *args, **kwargs):
        formEmail = self.cleaned_data['email'].lower()
        if self.instance.pk is None:  # Insert
            if CustomUser.objects.filter(email=formEmail).exists():
                raise forms.ValidationError(
                    "The given email is already registered")
        else:  # Update
            dbEmail = self.Meta.model.objects.get(
                id=self.instance.pk).admin.email.lower()
            if dbEmail != formEmail:  # There has been changes
                if CustomUser.objects.filter(email=formEmail).exists():
                    raise forms.ValidationError("The given email is already registered")

        return formEmail

    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'gender',  'password', 'address' ]


class StudentForm(CustomUserForm):
    def __init__(self, *args, **kwargs):
        super(StudentForm, self).__init__(*args, **kwargs)

    class Meta(CustomUserForm.Meta):
        model = Student
        fields = CustomUserForm.Meta.fields + \
            ['course', 'session']


class AdminForm(CustomUserForm):
    def __init__(self, *args, **kwargs):
        super(AdminForm, self).__init__(*args, **kwargs)

    class Meta(CustomUserForm.Meta):
        model = Admin
        fields = CustomUserForm.Meta.fields


class ManagementForm(CustomUserForm):
    designation = forms.CharField(required=False)
    employee_id = forms.CharField(required=False)
    department = forms.CharField(required=False)
    mobile_number = forms.CharField(required=False)
    
    def __init__(self, *args, **kwargs):
        super(ManagementForm, self).__init__(*args, **kwargs)

    class Meta(CustomUserForm.Meta):
        model = Management
        fields = CustomUserForm.Meta.fields + ['designation', 'employee_id', 'department', 'mobile_number']


class StaffForm(CustomUserForm):
    def __init__(self, *args, **kwargs):
        super(StaffForm, self).__init__(*args, **kwargs)

    class Meta(CustomUserForm.Meta):
        model = Staff
        fields = CustomUserForm.Meta.fields + \
            ['course' ]


class CourseForm(FormSettings):
    def __init__(self, *args, **kwargs):
        super(CourseForm, self).__init__(*args, **kwargs)

    class Meta:
        fields = ['name']
        model = Course


class SubjectForm(FormSettings):

    def __init__(self, *args, **kwargs):
        super(SubjectForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Subject
        fields = ['name', 'staff', 'course']


class SessionForm(FormSettings):
    def __init__(self, *args, **kwargs):
        super(SessionForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Session
        fields = '__all__'
        widgets = {
            'start_year': DateInput(attrs={'type': 'date'}),
            'end_year': DateInput(attrs={'type': 'date'}),
        }


class LeaveReportStaffForm(FormSettings):
    def __init__(self, *args, **kwargs):
        super(LeaveReportStaffForm, self).__init__(*args, **kwargs)

    class Meta:
        model = LeaveReportStaff
        fields = ['date', 'message']
        widgets = {
            'date': DateInput(attrs={'type': 'date'}),
        }


class FeedbackStaffForm(FormSettings):

    def __init__(self, *args, **kwargs):
        super(FeedbackStaffForm, self).__init__(*args, **kwargs)

    class Meta:
        model = FeedbackStaff
        fields = ['feedback']


class LeaveReportStudentForm(FormSettings):
    def __init__(self, *args, **kwargs):
        super(LeaveReportStudentForm, self).__init__(*args, **kwargs)

    class Meta:
        model = LeaveReportStudent
        fields = ['date', 'message']
        widgets = {
            'date': DateInput(attrs={'type': 'date'}),
        }


class FeedbackStudentForm(FormSettings):

    def __init__(self, *args, **kwargs):
        super(FeedbackStudentForm, self).__init__(*args, **kwargs)

    class Meta:
        model = FeedbackStudent
        fields = ['feedback']


class StudentEditForm(CustomUserForm):
    def __init__(self, *args, **kwargs):
        super(StudentEditForm, self).__init__(*args, **kwargs)

    class Meta(CustomUserForm.Meta):
        model = Student
        fields = CustomUserForm.Meta.fields 


class StaffEditForm(CustomUserForm):
    def __init__(self, *args, **kwargs):
        super(StaffEditForm, self).__init__(*args, **kwargs)

    class Meta(CustomUserForm.Meta):
        model = Staff
        fields = CustomUserForm.Meta.fields


class EditResultForm(FormSettings):
    session_list = Session.objects.all()
    session_year = forms.ModelChoiceField(
        label="Session Year", queryset=session_list, required=True)

    def __init__(self, *args, **kwargs):
        super(EditResultForm, self).__init__(*args, **kwargs)

    class Meta:
        model = StudentResult
        fields = ['session_year', 'subject', 'student', 'test', 'exam']


# ==================== NEW ERP FORMS ====================

class DepartmentForm(FormSettings):
    class Meta:
        model = Department
        fields = ['name', 'code', 'hod', 'contact_email', 'contact_number', 'description', 'established_year']


class ProgramForm(FormSettings):
    class Meta:
        model = Program
        fields = ['name', 'code', 'program_type', 'department', 'duration_years', 
                  'total_semesters', 'total_credits', 'eligibility_criteria', 'syllabus_document', 'is_active']
        widgets = {
            'eligibility_criteria': forms.Textarea(attrs={'rows': 3}),
        }


class ExamForm(FormSettings):
    class Meta:
        model = Exam
        fields = ['name', 'exam_type', 'session', 'semester', 'start_date', 'end_date']
        widgets = {
            'start_date': DateInput(attrs={'type': 'date'}),
            'end_date': DateInput(attrs={'type': 'date'}),
        }


class ExamScheduleForm(FormSettings):
    class Meta:
        model = ExamSchedule
        fields = ['exam', 'subject', 'exam_date', 'start_time', 'end_time', 'room_number', 'max_marks']
        widgets = {
            'exam_date': DateInput(attrs={'type': 'date'}),
            'start_time': forms.TimeInput(attrs={'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'type': 'time'}),
        }


class TimetableForm(FormSettings):
    class Meta:
        model = Timetable
        fields = ['session', 'course', 'semester', 'weekday', 'period', 'start_time', 
                  'end_time', 'subject', 'staff', 'room_number', 'is_lab']
        widgets = {
            'start_time': forms.TimeInput(attrs={'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'type': 'time'}),
        }


class CompanyForm(FormSettings):
    class Meta:
        model = Company
        fields = ['name', 'company_type', 'website', 'description', 'hr_name', 
                  'hr_email', 'hr_contact', 'address', 'logo', 'is_active']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'address': forms.Textarea(attrs={'rows': 2}),
        }


class PlacementDriveForm(FormSettings):
    class Meta:
        model = PlacementDrive
        fields = ['company', 'session', 'drive_type', 'job_title', 'job_description',
                  'eligible_courses', 'min_cgpa', 'allowed_backlogs', 'salary_package',
                  'bond_years', 'registration_deadline', 'aptitude_test_date',
                  'interview_date', 'selection_process', 'number_of_openings',
                  'jd_document', 'is_active']
        widgets = {
            'job_description': forms.Textarea(attrs={'rows': 3}),
            'selection_process': forms.Textarea(attrs={'rows': 2}),
            'registration_deadline': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'aptitude_test_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'interview_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }


class PlacementApplicationForm(FormSettings):
    class Meta:
        model = PlacementApplication
        fields = ['resume', 'cover_letter']
        widgets = {
            'cover_letter': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Why should we hire you?'}),
        }


class FeeStructureForm(FormSettings):
    class Meta:
        model = FeeStructure
        fields = ['course', 'course_type', 'semester', 'session', 'tuition_fee',
                  'development_fee', 'lab_fee', 'library_fee', 'exam_fee', 'other_fee']


class FeePaymentForm(FormSettings):
    class Meta:
        model = FeePayment
        fields = ['student', 'fee_structure', 'amount_paid', 'payment_date',
                  'payment_method', 'transaction_id', 'receipt_number', 'status', 'remarks']
        widgets = {
            'payment_date': DateInput(attrs={'type': 'date'}),
            'remarks': forms.Textarea(attrs={'rows': 2}),
        }


class ScholarshipForm(FormSettings):
    class Meta:
        model = Scholarship
        fields = ['name', 'scholarship_type', 'description', 'eligibility_criteria',
                  'amount', 'max_recipients', 'application_deadline', 'is_active']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'eligibility_criteria': forms.Textarea(attrs={'rows': 3}),
            'application_deadline': DateInput(attrs={'type': 'date'}),
        }


class ScholarshipApplicationForm(FormSettings):
    class Meta:
        model = ScholarshipApplication
        fields = ['scholarship', 'reason', 'supporting_documents']
        widgets = {
            'reason': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Why do you deserve this scholarship?'}),
        }


class HostelForm(FormSettings):
    class Meta:
        model = Hostel
        fields = ['name', 'hostel_type', 'warden_name', 'warden_contact',
                  'total_rooms', 'occupied_rooms', 'address']
        widgets = {
            'address': forms.Textarea(attrs={'rows': 2}),
        }


class HostelAllocationForm(FormSettings):
    class Meta:
        model = HostelAllocation
        fields = ['student', 'hostel', 'room_number', 'rent_per_semester', 'is_active']


class TransportForm(FormSettings):
    class Meta:
        model = Transport
        fields = ['route_name', 'bus_number', 'driver_name', 'driver_contact',
                  'route_details', 'fee_per_semester', 'total_seats', 'occupied_seats']
        widgets = {
            'route_details': forms.Textarea(attrs={'rows': 3}),
        }


class TransportAllocationForm(FormSettings):
    class Meta:
        model = TransportAllocation
        fields = ['student', 'transport', 'pickup_point', 'is_active']


class LibraryBookForm(FormSettings):
    class Meta:
        model = Library
        fields = ['title', 'author', 'isbn', 'publisher', 'published_year', 'category',
                  'subject', 'total_copies', 'available_copies', 'shelf_number',
                  'description', 'cover_image']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 2}),
        }


class LibraryIssueForm(FormSettings):
    class Meta:
        model = LibraryIssue
        fields = ['book', 'student', 'due_date', 'remarks']
        widgets = {
            'due_date': DateInput(attrs={'type': 'date'}),
            'remarks': forms.Textarea(attrs={'rows': 2}),
        }


class GrievanceForm(FormSettings):
    class Meta:
        model = Grievance
        fields = ['grievance_type', 'subject', 'description', 'priority', 'attachment']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Describe your grievance in detail'}),
        }


class SemesterResultForm(FormSettings):
    class Meta:
        model = SemesterResult
        fields = ['student', 'session', 'semester', 'total_credits', 'credits_earned',
                  'sgpa', 'cgpa', 'total_marks', 'marks_obtained', 'percentage',
                  'has_backlogs', 'number_of_backlogs', 'remarks']
        widgets = {
            'remarks': forms.Textarea(attrs={'rows': 2}),
        }


class SubjectResultForm(FormSettings):
    class Meta:
        model = SubjectResult
        fields = ['semester_result', 'subject', 'internal_marks', 'external_marks',
                  'max_marks', 'grade', 'credits']


# NEW ECAP FEATURES FORMS

class OnlineExamForm(FormSettings):
    class Meta:
        model = OnlineExam
        fields = ['title', 'subject', 'course', 'duration_minutes', 'total_marks',
                  'passing_marks', 'start_datetime', 'end_datetime', 'instructions',
                  'shuffle_questions', 'show_result_immediately']
        widgets = {
            'start_datetime': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'end_datetime': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'instructions': forms.Textarea(attrs={'rows': 3}),
        }


class OnlineExamQuestionForm(FormSettings):
    class Meta:
        model = OnlineExamQuestion
        fields = ['question_text', 'question_type', 'marks', 'option_a', 'option_b',
                  'option_c', 'option_d', 'correct_answer', 'explanation']
        widgets = {
            'question_text': forms.Textarea(attrs={'rows': 3}),
            'explanation': forms.Textarea(attrs={'rows': 2}),
        }


class CertificateForm(FormSettings):
    class Meta:
        model = Certificate
        fields = ['student', 'certificate_type', 'certificate_number', 'title',
                  'description', 'issued_date', 'valid_until']
        widgets = {
            'issued_date': forms.DateInput(attrs={'type': 'date'}),
            'valid_until': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 3}),
        }


class AlumniForm(FormSettings):
    class Meta:
        model = Alumni
        fields = ['passout_year', 'final_cgpa', 'current_company', 'current_designation',
                  'current_location', 'current_salary_package', 'current_email',
                  'current_mobile', 'linkedin_profile', 'is_willing_to_mentor',
                  'is_recruiter', 'achievements', 'testimonial']
        widgets = {
            'achievements': forms.Textarea(attrs={'rows': 3}),
            'testimonial': forms.Textarea(attrs={'rows': 3}),
        }


class InternshipForm(FormSettings):
    class Meta:
        model = Internship
        fields = ['company_name', 'internship_type', 'role', 'start_date', 'end_date',
                  'duration_months', 'stipend', 'location', 'supervisor_name',
                  'supervisor_contact', 'description']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 3}),
        }


class MedicalRecordForm(FormSettings):
    class Meta:
        model = MedicalRecord
        fields = ['student', 'complaint', 'diagnosis', 'treatment', 'doctor_name',
                  'follow_up_required', 'follow_up_date', 'remarks']
        widgets = {
            'complaint': forms.Textarea(attrs={'rows': 2}),
            'diagnosis': forms.Textarea(attrs={'rows': 2}),
            'treatment': forms.Textarea(attrs={'rows': 2}),
            'follow_up_date': forms.DateInput(attrs={'type': 'date'}),
            'remarks': forms.Textarea(attrs={'rows': 2}),
        }


class GatePassForm(FormSettings):
    class Meta:
        model = GatePass
        fields = ['pass_type', 'reason', 'from_date', 'to_date', 'destination',
                  'parent_consent', 'parent_contact']
        widgets = {
            'from_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'to_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'reason': forms.Textarea(attrs={'rows': 3}),
        }


class DisciplinaryActionForm(FormSettings):
    class Meta:
        model = DisciplinaryAction
        fields = ['student', 'incident_date', 'incident_description', 'severity',
                  'action_taken', 'action_description', 'fine_amount',
                  'suspension_from', 'suspension_to']
        widgets = {
            'incident_date': forms.DateInput(attrs={'type': 'date'}),
            'incident_description': forms.Textarea(attrs={'rows': 3}),
            'action_description': forms.Textarea(attrs={'rows': 3}),
            'suspension_from': forms.DateInput(attrs={'type': 'date'}),
            'suspension_to': forms.DateInput(attrs={'type': 'date'}),
        }


class SportsActivityForm(FormSettings):
    class Meta:
        model = SportsActivity
        fields = ['name', 'activity_type', 'description', 'start_date', 'end_date',
                  'venue', 'coordinator', 'max_participants', 'registration_deadline']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'registration_deadline': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 3}),
        }


class ActivityParticipationForm(FormSettings):
    class Meta:
        model = ActivityParticipation
        fields = ['activity', 'achievement_level', 'certificate_number', 'remarks']
        widgets = {
            'remarks': forms.Textarea(attrs={'rows': 2}),
        }


class ResearchForm(FormSettings):
    class Meta:
        model = Research
        fields = ['title', 'publication_type', 'authors', 'publication_name', 'publisher',
                  'publication_date', 'volume', 'issue', 'page_numbers', 'doi',
                  'isbn_issn', 'abstract', 'keywords', 'citation_count',
                  'impact_factor', 'is_peer_reviewed']
        widgets = {
            'publication_date': forms.DateInput(attrs={'type': 'date'}),
            'abstract': forms.Textarea(attrs={'rows': 3}),
        }


class AntiRaggingForm(FormSettings):
    class Meta:
        model = AntiRaggingCommittee
        fields = ['incident_number', 'incident_date', 'incident_description', 'location',
                  'severity', 'accused_students', 'witnesses', 'is_anonymous']
        widgets = {
            'incident_date': forms.DateInput(attrs={'type': 'date'}),
            'incident_description': forms.Textarea(attrs={'rows': 3}),
            'accused_students': forms.Textarea(attrs={'rows': 2}),
            'witnesses': forms.Textarea(attrs={'rows': 2}),
        }


class StudentCouncilForm(FormSettings):
    class Meta:
        model = StudentCouncil
        fields = ['student', 'session', 'position', 'department', 'election_date',
                  'term_start', 'term_end', 'manifesto', 'achievements']
        widgets = {
            'election_date': forms.DateInput(attrs={'type': 'date'}),
            'term_start': forms.DateInput(attrs={'type': 'date'}),
            'term_end': forms.DateInput(attrs={'type': 'date'}),
            'manifesto': forms.Textarea(attrs={'rows': 3}),
            'achievements': forms.Textarea(attrs={'rows': 3}),
        }


class ParentGuardianForm(forms.ModelForm):
    class Meta:
        model = ParentGuardian
        fields = ['student', 'parent_name', 'relation', 'email', 'mobile_number']
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'parent_name': forms.TextInput(attrs={'class': 'form-control'}),
            'mobile_number': forms.TextInput(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super(ParentGuardianForm, self).__init__(*args, **kwargs)
        for field in self.visible_fields():
            field.field.widget.attrs['class'] = 'form-control'


# Classroom Management Forms

class ClassroomForm(FormSettings):
    class Meta:
        model = Classroom
        fields = ['room_number', 'room_name', 'room_type', 'building', 'floor', 'capacity',
                  'department', 'has_projector', 'has_ac', 'has_wifi', 'has_audio_system',
                  'has_whiteboard', 'has_computers', 'computer_count', 'is_available',
                  'is_under_maintenance', 'remarks']
        widgets = {
            'remarks': forms.Textarea(attrs={'rows': 2}),
        }


class ClassroomBookingForm(FormSettings):
    class Meta:
        model = ClassroomBooking
        fields = ['classroom', 'booking_type', 'purpose', 'booking_date', 'start_time',
                  'end_time', 'expected_attendees', 'subject', 'course', 'special_requirements']
        widgets = {
            'booking_date': forms.DateInput(attrs={'type': 'date'}),
            'start_time': forms.TimeInput(attrs={'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'type': 'time'}),
            'special_requirements': forms.Textarea(attrs={'rows': 2}),
        }


class ClassroomMaintenanceForm(FormSettings):
    class Meta:
        model = ClassroomMaintenance
        fields = ['classroom', 'issue_type', 'issue_description', 'estimated_cost',
                  'assigned_to', 'remarks']
        widgets = {
            'issue_description': forms.Textarea(attrs={'rows': 3}),
            'remarks': forms.Textarea(attrs={'rows': 2}),
        }