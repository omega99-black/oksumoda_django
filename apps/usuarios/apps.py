from django.apps import AppConfig


class UsuariosConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.usuarios'
    verbose_name = 'Usuarios'

    def ready(self):
        try:
            from apps.usuarios.models import Usuario, Rol
            rol_admin, _ = Rol.objects.get_or_create(nombre='ADMIN')
            if not Usuario.objects.filter(email='admin@oksu.com').exists():
                u = Usuario()
                u.nombre = 'Admin'
                u.email = 'admin@oksu.com'
                u.set_password('admin123')
                u.estado = 'activo'
                u.is_staff = True
                u.is_superuser = True
                u.rol = rol_admin
                u.save()
                print("✅ Usuario admin creado automáticamente")
        except Exception:
            pass