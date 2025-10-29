from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db.models import Q


class EmailBackend(ModelBackend):
    def authenticate(self, username=None, password=None, **kwargs):
        UserModel = get_user_model()
        user = None
        
        if not username:
            return None
        
        username = str(username).strip()
        
        # Try to find user by email OR username (unique ID)
        try:
            user = UserModel.objects.get(
                Q(email__iexact=username) | Q(username__iexact=username)
            )
        except UserModel.DoesNotExist:
            # If not found by email/username, try roll number (for students)
            try:
                from .models import Student
                student = Student.objects.select_related('admin').get(
                    roll_number__iexact=username
                )
                user = student.admin
            except Student.DoesNotExist:
                # If not found as roll number, try employee ID (for staff)
                try:
                    from .models import Staff
                    staff = Staff.objects.select_related('admin').get(
                        employee_id__iexact=username
                    )
                    user = staff.admin
                except Staff.DoesNotExist:
                    # Try management employee ID
                    try:
                        from .models import Management
                        management = Management.objects.select_related('admin').get(
                            employee_id__iexact=username
                        )
                        user = management.admin
                    except:
                        return None
        except UserModel.MultipleObjectsReturned:
            # If multiple users, try email first
            try:
                user = UserModel.objects.get(email__iexact=username)
            except UserModel.DoesNotExist:
                try:
                    user = UserModel.objects.get(username__iexact=username)
                except UserModel.DoesNotExist:
                    return None
        
        # Check password
        if user and user.check_password(password):
            return user
        
        return None
