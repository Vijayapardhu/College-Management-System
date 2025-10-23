from django import forms
from django.contrib.auth import get_user_model
from .communication_models import ChatRoom, ChatMessage
from .models import Student, Staff, Department, Course, Subject

User = get_user_model()


class CreateChatRoomForm(forms.ModelForm):
    """Form for creating a new chat room"""
    participants = forms.ModelMultipleChoiceField(
        queryset=User.objects.none(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        help_text="Select users to add to the chat room"
    )
    
    class Meta:
        model = ChatRoom
        fields = ['name', 'description', 'room_type']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter room name'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Enter room description (optional)'
            }),
            'room_type': forms.Select(attrs={
                'class': 'form-control'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if user:
            # Set available participants based on user type
            if user.user_type == '1':  # HOD
                # HOD can add anyone
                self.fields['participants'].queryset = User.objects.exclude(id=user.id)
            elif user.user_type == '2':  # Staff
                # Staff can add HOD, other staff, and students
                self.fields['participants'].queryset = User.objects.filter(
                    user_type__in=['1', '2', '3']
                ).exclude(id=user.id)
            elif user.user_type == '3':  # Student
                # Students can add HOD, staff, and other students
                self.fields['participants'].queryset = User.objects.filter(
                    user_type__in=['1', '2', '3']
                ).exclude(id=user.id)
            elif user.user_type == '4':  # Management
                # Management can add anyone
                self.fields['participants'].queryset = User.objects.exclude(id=user.id)
    
    def clean_name(self):
        name = self.cleaned_data.get('name')
        if name and len(name.strip()) < 3:
            raise forms.ValidationError("Room name must be at least 3 characters long.")
        return name.strip()


class ChatMessageForm(forms.ModelForm):
    """Form for sending chat messages"""
    message = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Type your message...',
            'id': 'message-input'
        }),
        max_length=1000,
        help_text="Maximum 1000 characters"
    )
    
    attachment = forms.FileField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'form-control-file',
            'accept': 'image/*,video/*,audio/*,.pdf,.doc,.docx,.txt,.ppt,.pptx'
        }),
        help_text="Upload an image, document, or media file (max 10MB)"
    )
    
    class Meta:
        model = ChatMessage
        fields = ['message', 'attachment']
    
    def clean_message(self):
        message = self.cleaned_data.get('message', '').strip()
        if not message and not self.cleaned_data.get('attachment'):
            raise forms.ValidationError("Either a message or attachment is required.")
        return message
    
    def clean_attachment(self):
        attachment = self.cleaned_data.get('attachment')
        if attachment:
            # Check file size (10MB limit)
            if attachment.size > 10 * 1024 * 1024:
                raise forms.ValidationError("File size cannot exceed 10MB.")
            
            # Check file type
            allowed_types = [
                'image/jpeg', 'image/png', 'image/gif', 'image/webp',
                'video/mp4', 'video/avi', 'video/mov', 'video/wmv',
                'audio/mp3', 'audio/wav', 'audio/ogg',
                'application/pdf', 'application/msword', 
                'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                'text/plain', 'application/vnd.ms-powerpoint',
                'application/vnd.openxmlformats-officedocument.presentationml.presentation'
            ]
            
            if attachment.content_type not in allowed_types:
                raise forms.ValidationError("File type not supported. Please upload images, videos, audio, or documents.")
        
        return attachment


class ChatSearchForm(forms.Form):
    """Form for searching chat messages"""
    query = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search messages...',
            'id': 'search-input'
        }),
        help_text="Search for messages by content"
    )
    
    room = forms.ModelChoiceField(
        queryset=ChatRoom.objects.none(),
        required=False,
        empty_label="All Rooms",
        widget=forms.Select(attrs={
            'class': 'form-control'
        }),
        help_text="Filter by specific room"
    )
    
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        }),
        help_text="Search from this date"
    )
    
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        }),
        help_text="Search until this date"
    )
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if user:
            # Set available rooms to user's rooms only
            self.fields['room'].queryset = ChatRoom.objects.filter(
                participants=user,
                is_active=True
            ).order_by('name')
    
    def clean(self):
        cleaned_data = super().clean()
        date_from = cleaned_data.get('date_from')
        date_to = cleaned_data.get('date_to')
        
        if date_from and date_to and date_from > date_to:
            raise forms.ValidationError("Start date cannot be after end date.")
        
        return cleaned_data


class AddParticipantsForm(forms.Form):
    """Form for adding participants to a chat room"""
    participants = forms.ModelMultipleChoiceField(
        queryset=User.objects.none(),
        widget=forms.CheckboxSelectMultiple,
        required=True,
        help_text="Select users to add to the chat room"
    )
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        room = kwargs.pop('room', None)
        super().__init__(*args, **kwargs)
        
        if user and room:
            # Get users who are not already in the room
            existing_participants = room.participants.all()
            
            # Set available participants based on user type and room type
            if user.user_type == '1':  # HOD
                # HOD can add anyone not already in room
                available_users = User.objects.exclude(id__in=existing_participants.values_list('id', flat=True))
            elif user.user_type == '2':  # Staff
                # Staff can add HOD, other staff, and students
                available_users = User.objects.filter(
                    user_type__in=['1', '2', '3']
                ).exclude(id__in=existing_participants.values_list('id', flat=True))
            elif user.user_type == '3':  # Student
                # Students can add HOD, staff, and other students
                available_users = User.objects.filter(
                    user_type__in=['1', '2', '3']
                ).exclude(id__in=existing_participants.values_list('id', flat=True))
            elif user.user_type == '4':  # Management
                # Management can add anyone not already in room
                available_users = User.objects.exclude(id__in=existing_participants.values_list('id', flat=True))
            else:
                available_users = User.objects.none()
            
            self.fields['participants'].queryset = available_users.order_by('first_name', 'last_name')


class ClassGroupForm(forms.ModelForm):
    """Form for creating class-based group chats"""
    course = forms.ModelChoiceField(
        queryset=Course.objects.all(),
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'course-select'
        }),
        help_text="Select the course for this class group"
    )
    
    session = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., 2024-25, 2023-24'
        }),
        help_text="Enter the academic session"
    )
    
    include_staff = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        help_text="Include course faculty in the group"
    )
    
    class Meta:
        model = ChatRoom
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter group name'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Enter group description'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['room_type'].initial = 'class'
    
    def clean_session(self):
        session = self.cleaned_data.get('session', '').strip()
        if not session:
            raise forms.ValidationError("Session is required for class groups.")
        return session


class SubjectGroupForm(forms.ModelForm):
    """Form for creating subject-based group chats"""
    subject = forms.ModelChoiceField(
        queryset=Subject.objects.all(),
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'subject-select'
        }),
        help_text="Select the subject for this group"
    )
    
    include_all_students = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        help_text="Include all students enrolled in this subject"
    )
    
    class Meta:
        model = ChatRoom
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter group name'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Enter group description'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['room_type'].initial = 'subject'


class EditMessageForm(forms.ModelForm):
    """Form for editing chat messages"""
    class Meta:
        model = ChatMessage
        fields = ['message']
        widgets = {
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'id': 'edit-message-input'
            }),
        }
    
    def clean_message(self):
        message = self.cleaned_data.get('message', '').strip()
        if not message:
            raise forms.ValidationError("Message cannot be empty.")
        if len(message) > 1000:
            raise forms.ValidationError("Message is too long. Maximum 1000 characters.")
        return message


