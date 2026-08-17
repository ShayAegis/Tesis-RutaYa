from django.contrib.auth.backends import BaseBackend
from .models import Usuario

class EmailBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):

        if username is None or password is None:
            return None
        
        try:
            user = Usuario.objects.get(email=username)
        except Usuario.DoesNotExist:
            return None

        if user.check_password(password):
            return user

        return None

    def get_user(self, user_id):
        try:
            return Usuario.objects.get(pk=user_id)
        except Usuario.DoesNotExist:
            return None