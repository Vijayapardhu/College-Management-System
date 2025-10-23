"""
Forms for Placement & Career Portal
"""
from django import forms
from django.utils import timezone
from .models import Company, PlacementDrive, PlacementApplication, Course, Session, Student
from .placement_models import (
    InterviewRound, InterviewSlot, InterviewFeedback, PlacementOffer,
    StudentPlacementProfile, PlacementCoordinator, CompanyVisit
)


class CompanyForm(forms.ModelForm):
    """Form for adding/editing companies"""
    class Meta:
        model = Company
        fields = [
            'name', 'company_type', 'website', 'description',
            'hr_name', 'hr_email', 'hr_contact', 'address',
            'logo', 'is_active'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'company_type': forms.Select(attrs={'class': 'form-control'}),
            'website': forms.URLInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'hr_name': forms.TextInput(attrs={'class': 'form-control'}),
            'hr_email': forms.EmailInput(attrs={'class': 'form-control'}),
            'hr_contact': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class PlacementDriveForm(forms.ModelForm):
    """Form for creating placement drives"""
    class Meta:
        model = PlacementDrive
        fields = [
            'company', 'session', 'drive_type', 'job_title', 'job_description',
            'eligible_courses', 'min_cgpa', 'allowed_backlogs',
            'salary_package', 'bond_years', 'registration_deadline',
            'aptitude_test_date', 'interview_date', 'selection_process',
            'number_of_openings', 'jd_document', 'coordinator', 'is_active'
        ]
        widgets = {
            'company': forms.Select(attrs={'class': 'form-control'}),
            'session': forms.Select(attrs={'class': 'form-control'}),
            'drive_type': forms.Select(attrs={'class': 'form-control'}),
            'job_title': forms.TextInput(attrs={'class': 'form-control'}),
            'job_description': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'eligible_courses': forms.SelectMultiple(attrs={'class': 'form-control'}),
            'min_cgpa': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'allowed_backlogs': forms.NumberInput(attrs={'class': 'form-control'}),
            'salary_package': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'bond_years': forms.NumberInput(attrs={'class': 'form-control'}),
            'registration_deadline': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'aptitude_test_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'interview_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'selection_process': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'number_of_openings': forms.NumberInput(attrs={'class': 'form-control'}),
            'coordinator': forms.Select(attrs={'class': 'form-control'}),
        }


class InterviewRoundForm(forms.ModelForm):
    """Form for creating interview rounds"""
    class Meta:
        model = InterviewRound
        fields = [
            'placement_drive', 'round_name', 'round_type', 'round_number',
            'mode', 'venue', 'scheduled_date', 'start_time', 'end_time',
            'duration_minutes', 'instructions'
        ]
        widgets = {
            'placement_drive': forms.Select(attrs={'class': 'form-control'}),
            'round_name': forms.TextInput(attrs={'class': 'form-control'}),
            'round_type': forms.Select(attrs={'class': 'form-control'}),
            'round_number': forms.NumberInput(attrs={'class': 'form-control'}),
            'mode': forms.Select(attrs={'class': 'form-control'}),
            'venue': forms.TextInput(attrs={'class': 'form-control'}),
            'scheduled_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'start_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'duration_minutes': forms.NumberInput(attrs={'class': 'form-control'}),
            'instructions': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }


class InterviewSlotForm(forms.ModelForm):
    """Form for creating interview slots"""
    class Meta:
        model = InterviewSlot
        fields = [
            'interview_round', 'slot_time', 'meeting_link', 'room_number', 'notes'
        ]
        widgets = {
            'interview_round': forms.Select(attrs={'class': 'form-control'}),
            'slot_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'meeting_link': forms.URLInput(attrs={'class': 'form-control'}),
            'room_number': forms.TextInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class InterviewFeedbackForm(forms.ModelForm):
    """Form for interview feedback"""
    class Meta:
        model = InterviewFeedback
        fields = [
            'interviewer_name', 'interviewer_email',
            'technical_skills', 'communication_skills', 'problem_solving', 'attitude',
            'overall_rating', 'recommendation',
            'strengths', 'weaknesses', 'comments'
        ]
        widgets = {
            'interviewer_name': forms.TextInput(attrs={'class': 'form-control'}),
            'interviewer_email': forms.EmailInput(attrs={'class': 'form-control'}),
            'technical_skills': forms.Select(attrs={'class': 'form-control'}),
            'communication_skills': forms.Select(attrs={'class': 'form-control'}),
            'problem_solving': forms.Select(attrs={'class': 'form-control'}),
            'attitude': forms.Select(attrs={'class': 'form-control'}),
            'overall_rating': forms.Select(attrs={'class': 'form-control'}),
            'recommendation': forms.Select(attrs={'class': 'form-control'}),
            'strengths': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'weaknesses': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'comments': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }


class PlacementOfferForm(forms.ModelForm):
    """Form for creating placement offers"""
    class Meta:
        model = PlacementOffer
        fields = [
            'application', 'offer_type', 'job_title', 'job_location',
            'ctc', 'stipend', 'joining_date', 'offer_letter', 'expiry_date'
        ]
        widgets = {
            'application': forms.Select(attrs={'class': 'form-control'}),
            'offer_type': forms.Select(attrs={'class': 'form-control'}),
            'job_title': forms.TextInput(attrs={'class': 'form-control'}),
            'job_location': forms.TextInput(attrs={'class': 'form-control'}),
            'ctc': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'stipend': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'joining_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'expiry_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }


class StudentPlacementProfileForm(forms.ModelForm):
    """Form for student placement profile"""
    class Meta:
        model = StudentPlacementProfile
        fields = [
            'tenth_percentage', 'twelfth_percentage', 'diploma_percentage', 'current_cgpa',
            'technical_skills', 'programming_languages', 'certifications',
            'internship_experience', 'project_experience',
            'resume', 'preferred_job_locations', 'preferred_job_roles', 'expected_ctc',
            'is_active_for_placement'
        ]
        widgets = {
            'tenth_percentage': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'twelfth_percentage': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'diploma_percentage': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'current_cgpa': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'technical_skills': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'programming_languages': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'certifications': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'internship_experience': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'project_experience': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'preferred_job_locations': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'preferred_job_roles': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'expected_ctc': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }


class PlacementApplicationForm(forms.ModelForm):
    """Form for student placement application"""
    class Meta:
        model = PlacementApplication
        fields = ['placement_drive', 'resume']
        widgets = {
            'placement_drive': forms.Select(attrs={'class': 'form-control'}),
        }


class CompanyVisitForm(forms.ModelForm):
    """Form for scheduling company visits"""
    class Meta:
        model = CompanyVisit
        fields = [
            'company', 'session', 'visit_date', 'visit_time', 'venue',
            'purpose', 'coordinator', 'notes'
        ]
        widgets = {
            'company': forms.Select(attrs={'class': 'form-control'}),
            'session': forms.Select(attrs={'class': 'form-control'}),
            'visit_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'visit_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'venue': forms.TextInput(attrs={'class': 'form-control'}),
            'purpose': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'coordinator': forms.Select(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class PlacementSearchForm(forms.Form):
    """Search and filter form for placements"""
    search_query = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Search...'}))
    
    company = forms.ModelChoiceField(
        queryset=Company.objects.filter(is_active=True),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
        empty_label="All Companies"
    )
    
    course = forms.ModelChoiceField(
        queryset=Course.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
        empty_label="All Courses"
    )
    
    session = forms.ModelChoiceField(
        queryset=Session.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
        empty_label="All Sessions"
    )
    
    status = forms.ChoiceField(
        choices=[('', 'All Status')] + list(PlacementApplication.APPLICATION_STATUS_CHOICES),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    min_package = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Min Package (LPA)', 'step': '0.01'})
    )
    
    max_package = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Max Package (LPA)', 'step': '0.01'})
    )


class BulkSlotCreationForm(forms.Form):
    """Form for creating multiple interview slots at once"""
    interview_round = forms.ModelChoiceField(
        queryset=InterviewRound.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    start_time = forms.TimeField(
        widget=forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'})
    )
    
    end_time = forms.TimeField(
        widget=forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'})
    )
    
    slot_duration = forms.IntegerField(
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Duration in minutes'}),
        help_text="Duration of each slot in minutes"
    )
    
    meeting_link = forms.URLField(
        required=False,
        widget=forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'Meeting link (for online interviews)'})
    )
    
    room_number = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Room number (for offline interviews)'})
    )



