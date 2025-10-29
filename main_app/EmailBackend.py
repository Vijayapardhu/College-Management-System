from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db.models import Q


class EmailBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        UserModel = get_user_model()
        user = None
        
        if not username:
            return None
        
        username = str(username).strip()
        
        print(f"[EmailBackend] Authenticating: {username}")
        
        # Try to find user by email OR username (unique ID)
        try:
            user = UserModel.objects.get(
                Q(email__iexact=username) | Q(username__iexact=username)
            )
            print(f"[EmailBackend] Found user by email/username: {user.email}")
        except UserModel.DoesNotExist:
            # If not found by email/username, try roll number (for students)
            try:
                from .models import Student
                student = Student.objects.select_related('admin').get(
                    roll_number__iexact=username
                )
                user = student.admin
                print(f"[EmailBackend] Found user by roll_number: {user.email}")
            except Student.DoesNotExist:
                # If not found as roll number, try employee ID (for staff)
                try:
                    from .models import Staff
                    staff = Staff.objects.select_related('admin').get(
                        employee_id__iexact=username
                    )
                    user = staff.admin
                    print(f"[EmailBackend] Found user by employee_id: {user.email}")
                except Staff.DoesNotExist:
                    # Try management employee ID
                    try:
                        from .models import Management
                        management = Management.objects.select_related('admin').get(
                            employee_id__iexact=username
                        )
                        user = management.admin
                        print(f"[EmailBackend] Found user by management employee_id: {user.email}")
                    except:
                        print(f"[EmailBackend] User not found: {username}")
                        return None
        except UserModel.MultipleObjectsReturned:
            # If multiple users, try email first
            try:
                user = UserModel.objects.get(email__iexact=username)
                print(f"[EmailBackend] Found user by email (multiple): {user.email}")
            except UserModel.DoesNotExist:
                try:
                    user = UserModel.objects.get(username__iexact=username)
                    print(f"[EmailBackend] Found user by username (multiple): {user.email}")
                except UserModel.DoesNotExist:
                    print(f"[EmailBackend] User not found (multiple): {username}")
                    return None
        
        # Check password
        if user:
            print(f"[EmailBackend] Checking password for: {user.email}")
            if user.check_password(password):
                print(f"[EmailBackend] Password valid for: {user.email}")
                return user
            else:
                print(f"[EmailBackend] Password invalid for: {user.email}")
        
        return None
