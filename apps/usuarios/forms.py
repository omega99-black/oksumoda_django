"""
apps/usuarios/forms.py
Formularios para registro y edición de usuarios.
"""

from django import forms
from .models import Usuario, Rol


class RegistroForm(forms.ModelForm):
    contrasena = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Contraseña'}),
        label='Contraseña',
        min_length=6,
    )

    class Meta:
        model = Usuario
        fields = ['nombre', 'email']
        widgets = {
            'nombre': forms.TextInput(attrs={'placeholder': 'Nombre completo'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Correo electrónico'}),
        }


class UsuarioAdminForm(forms.ModelForm):
    """Formulario para crear/editar usuarios desde el panel admin."""
    contrasena = forms.CharField(
        widget=forms.PasswordInput(),
        label='Contraseña (dejar vacío para mantener)',
        required=False,
    )

    class Meta:
        model = Usuario
        fields = ['nombre', 'email', 'estado', 'rol']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['rol'].queryset = Rol.objects.all()
        self.fields['rol'].label_from_instance = lambda obj: obj.nombre
