from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models


class Rol(models.Model):
    id_rol = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=50)

    class Meta:
        db_table = 'roles'
        managed = True

    def __str__(self):
        return self.nombre


class UsuarioManager(BaseUserManager):
    def create_user(self, email, nombre, contrasena=None, **extra_fields):
        if not email:
            raise ValueError('El email es obligatorio')
        email = self.normalize_email(email)
        user = self.model(email=email, nombre=nombre, **extra_fields)
        user.set_password(contrasena)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, nombre, contrasena=None, **extra_fields):
        extra_fields.setdefault('estado', 'activo')
        rol_admin, _ = Rol.objects.get_or_create(nombre='ADMIN')
        extra_fields.setdefault('rol', rol_admin)
        return self.create_user(email, nombre, contrasena, **extra_fields)


class Usuario(AbstractBaseUser, PermissionsMixin):
    id_usuario = models.AutoField(primary_key=True, db_column='id_usuario')
    nombre = models.CharField(max_length=100)
    email = models.EmailField(max_length=100, unique=True)
    password = models.CharField(max_length=100, db_column='contrasena')
    estado = models.CharField(max_length=20, default='activo')
    rol = models.ForeignKey(
        Rol,
        on_delete=models.PROTECT,
        db_column='id_rol',
        null=True,
        blank=True,
    )
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    objects = UsuarioManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nombre']

    class Meta:
        db_table = 'usuarios'
        managed = True

    def __str__(self):
        return f'{self.nombre} ({self.email})'

    @property
    def is_active(self):
        return self.estado.lower() == 'activo'

    def get_rol_nombre(self):
        if self.rol:
            nombre = self.rol.nombre.upper()
            return nombre.replace('ROLE_', '')
        return 'CLIENTE'

    def es_admin(self):
        rol = self.get_rol_nombre()
        return rol in ('ADMIN', 'ADMINISTRADOR')