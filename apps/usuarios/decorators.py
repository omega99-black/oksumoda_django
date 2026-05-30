"""
apps/usuarios/decorators.py  — VERSION CORREGIDA
─────────────────────────────────────────────────
Cambio principal:
  • cliente_o_admin_requerido  →  AHORA solo permite CLIENTES.
    Los admins son redirigidos al dashboard con un mensaje de error.
  • admin_requerido             →  sin cambios.
"""

from functools import wraps
from django.shortcuts import redirect
from django.http import HttpResponseForbidden


# ─────────────────────────────────────────────
# Decorador: solo admins
# ─────────────────────────────────────────────
def admin_requerido(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('/login/')
        if not request.user.es_admin():
            return redirect('/')
        return view_func(request, *args, **kwargs)
    return wrapper


# ─────────────────────────────────────────────
# Decorador: SOLO clientes  ← CORRECCIÓN PRINCIPAL
# (antes se llamaba cliente_o_admin_requerido y
#  permitía que los admins también compraran)
# ─────────────────────────────────────────────
def cliente_o_admin_requerido(view_func):
    """
    Permite el acceso ÚNICAMENTE a usuarios autenticados con rol CLIENTE.
    Los administradores son redirigidos al dashboard admin con mensaje.
    Los no autenticados van al login.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('/login/')
        # Bloquear admin: redirigir al dashboard con parámetro de aviso
        if request.user.es_admin():
            return redirect('/admin/dashboard/?error=no_compras')
        return view_func(request, *args, **kwargs)
    return wrapper


# ─────────────────────────────────────────────
# Decorador: cualquier usuario autenticado
# ─────────────────────────────────────────────
def login_requerido(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('/login/')
        return view_func(request, *args, **kwargs)
    return wrapper