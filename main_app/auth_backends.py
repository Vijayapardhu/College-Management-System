"""
Custom Authentication Backend for EduVision
Allows login with either Roll Number OR Email
"""

from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from .models import Student

CustomUser = get_user_model()


class RollNumberOrEmailBackend(ModelBackend):
    """
    Authenticates users using either:
    1. Email address
    2. Roll number (for students)
    
    Usage in login view:
    authenticate(request, username=email_or_roll, password=password)
    """
    
    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None or password is None:
            return None
        
        user = None
        username_lower = username.lower().strip()
        
        try:
            # First, try to find by email
            if '@' in username_lower:
                user = CustomUser.objects.get(email__iexact=username_lower)
            else:
                # If no @, try to find student by roll number
                try:
                    student = Student.objects.select_related('admin').get(
                        roll_number__iexact=username_lower
                    )
                    user = student.admin
                except Student.DoesNotExist:
                    # If not found as roll number, try as username (fallback)
                    try:
                        user = CustomUser.objects.get(username__iexact=username_lower)
                    except CustomUser.DoesNotExist:
                        pass
        
        except CustomUser.DoesNotExist:
            # No user found
            return None
        except CustomUser.MultipleObjectsReturned:
            # Multiple users with same email (shouldn't happen, but handle it)
            return None
        
        # Check password
        if user and user.check_password(password):
            return user
        
        return None
    
    def get_user(self, user_id):
        """Required method to retrieve user by ID"""
        try:
            return CustomUser.objects.get(pk=user_id)
        except CustomUser.DoesNotExist:
            return None







