from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User

class EmailBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            # Busca al usuario por el email (que es lo que el usuario escribe)
            user = User.objects.get(email=username)
        except User.DoesNotExist:
            return None
        
        # Verifica la contraseña si el usuario existe
        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None