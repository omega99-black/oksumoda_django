"""
apps/usuarios/backends.py

Equivalente a UsuarioService.loadUserByUsername() de Spring Security.
Django requiere un Authentication Backend personalizado cuando se
autentica por email en lugar de username.
"""

from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

User = get_user_model()


class EmailBackend(ModelBackend):
    """
    Autentica usando email + contraseña.
    Equivalente al flujo: loadUserByUsername(email) → BCrypt.matches()
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        # 'username' aquí es en realidad el email (campo del form de login)
        email = username or kwargs.get('email')
        if not email:
            return None

        try:
            user = User.objects.select_related('rol').get(email=email)
        except User.DoesNotExist:
            # Equivalente a UsernameNotFoundException
            return None

        # check_password es el equivalente a BCryptPasswordEncoder.matches()
        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None

    def user_can_authenticate(self, user):
        # Equivalente a isEnabled() + isAccountNonLocked() en UserDetails
        return user.is_active
