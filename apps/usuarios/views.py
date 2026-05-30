"""
apps/usuarios/views.py
"""

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.http import require_http_methods
from django.contrib.auth.hashers import make_password

from .models import Rol, Usuario


# ── Login ──────────────────────────────────────────────────────────────────
@require_http_methods(["GET", "POST"])
def login_view(request):
    if request.user.is_authenticated:
        return redirect('/')

    error = None
    if request.method == 'POST':
        email    = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')

        user = authenticate(request, username=email, password=password)

        if user is not None:
            login(request, user)
            print(f"✅ LOGIN EXITOSO — {user.email} | Rol: {user.get_rol_nombre()}")
            return redirect('/')
        else:
            print(f"❌ LOGIN FALLIDO — email: {email}")
            error = 'Correo o contraseña incorrectos.'

    return render(request, 'login.html', {'error': error})


# ── Logout ─────────────────────────────────────────────────────────────────
def logout_view(request):
    logout(request)
    return redirect('/login/?logout')


# ── Registro ───────────────────────────────────────────────────────────────
@require_http_methods(["GET", "POST"])
def registro_view(request):
    error = None

    if request.method == 'POST':
        nombre     = request.POST.get('nombre', '').strip()
        email      = request.POST.get('email', '').strip()
        contrasena = request.POST.get('contrasena', '').strip()

        # Validaciones básicas
        if not nombre or not email or not contrasena:
            error = 'Todos los campos son obligatorios.'
        elif Usuario.objects.filter(email=email).exists():
            error = 'Ya existe una cuenta con ese correo electrónico.'
        else:
            try:
                # Buscar rol CLIENTE (ID 2)
                try:
                    rol_cliente = Rol.objects.get(id_rol=2)
                except Rol.DoesNotExist:
                    rol_cliente = Rol.objects.get(nombre__iexact='CLIENTE')

                # Crear usuario
                usuario = Usuario(
                    nombre=nombre,
                    email=email,
                    estado='activo',
                    rol=rol_cliente,
                )
                usuario.set_password(contrasena)
                usuario.save()

                # ── Crear Cliente vinculado al usuario ──────────────────
                try:
                    from apps.clientes.models import Cliente
                    if not Cliente.objects.filter(email=email).exists():
                        Cliente.objects.create(
                            nombre=nombre,
                            email=email,
                            contrasena=usuario.password,  # ya hasheada
                            estado='activo',
                        )
                        print(f"✅ Cliente creado automáticamente: {email}")
                except Exception as e:
                    print(f"⚠️ Usuario creado pero error al crear Cliente: {e}")
                # ────────────────────────────────────────────────────────

                print(f"✅ Nuevo usuario registrado: {email}")
                return redirect('/login/?success')

            except Exception as e:
                print(f"❌ Error al registrar usuario: {e}")
                error = f'Error al crear la cuenta: {str(e)}'

    return render(request, 'registro.html', {'error': error})