from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db.models import Q


class EmailBackend(ModelBackend):
    def authenticate(self, username=None, password=None, **kwargs):
        UserModel = get_user_model()
        user = None
        
        # Try to find user by email OR username (unique ID)
        try:
            user = UserModel.objects.get(
                Q(email=username) | Q(username=username)
            )
        except UserModel.DoesNotExist:
            return None
        except UserModel.MultipleObjectsReturned:
            # If multiple users, try email first
            try:
                user = UserModel.objects.get(email=username)
            except UserModel.DoesNotExist:
                try:
                    user = UserModel.objects.get(username=username)
                except UserModel.DoesNotExist:
                    return None
        
        # Check password
        if user and user.check_password(password):
            return user
        
        return None
