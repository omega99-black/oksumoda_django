# Oksumoda — Django

Conversión del proyecto Spring Boot → Django 4.2

---

## Mapa de equivalencias Java → Python

| Spring Boot / Java                          | Django / Python                                      |
|---------------------------------------------|------------------------------------------------------|
| `@SpringBootApplication`                    | `manage.py` + `settings.py`                          |
| `application.properties`                    | `.env` + `settings.py`                               |
| `@Entity` + JPA/Hibernate                   | `models.py` con `managed = False` (misma BD)         |
| `JpaRepository`                             | ORM de Django (`Model.objects.*`)                    |
| `@Service`                                  | Funciones en `services.py` o métodos del modelo      |
| `@Controller` + `@RequestMapping`           | `views.py` + `urls.py`                               |
| `Model.addAttribute()`                      | Diccionario `context` en `render()`                  |
| `FreeMarkerConfigurer` + `.ftl`             | Templates de Django (`.html`)                        |
| `UserDetails` + `UserDetailsService`        | `AbstractBaseUser` + `EmailBackend`                  |
| `BCryptPasswordEncoder`                     | `user.set_password()` / `make_password()`            |
| `SecurityConfig.hasAnyRole()`               | Decoradores `@admin_requerido` / `@rol_requerido()`  |
| `CustomAccessDeniedHandler` → `/403`        | Decorador redirige a `/403/`                         |
| `@SessionScope` en `CarritoService`         | `request.session` (dict en BD de sesiones)           |
| `ITextRenderer` (Flying Saucer PDF)         | `ReportLab`                                          |
| `HttpServletResponse` para PDF              | `HttpResponse(content_type='application/pdf')`       |
| `@ResponseBody` + `ResponseEntity`          | `JsonResponse()`                                     |
| `stream().filter()` en Services             | QuerySet `.filter()` del ORM                         |
| `BigDecimal`                                | `Decimal` de Python                                  |

---

## Instalación

```bash
# 1. Clonar / descomprimir el proyecto
cd oksumoda_django

# 2. Crear entorno virtual
python -m venv venv
source venv/bin/activate        # Linux/Mac
venv\Scripts\activate           # Windows

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar variables de entorno
cp .env.example .env
# Editar .env con tus credenciales de MySQL

# 5. Configurar backend de autenticación en settings.py
#    (ya incluido):
#    AUTHENTICATION_BACKENDS = ['apps.usuarios.backends.EmailBackend']

# 6. Aplicar migraciones (solo crea tablas de sesión y admin de Django)
#    Las tablas existentes (productos, usuarios, etc.) NO se tocan
#    porque tienen managed = False
python manage.py migrate

# 7. Ejecutar servidor
python manage.py runserver
#    Equivalente a: mvn spring-boot:run
#    → http://localhost:8000
```

---

## Estructura del proyecto

```
oksumoda_django/
├── manage.py                        # Equivalente a la clase main de Spring Boot
├── requirements.txt
├── .env.example
│
├── oksumoda/                        # Configuración global
│   ├── settings.py                  # application.properties + SecurityConfig + FreeMarkerConfig
│   └── urls.py                      # Rutas globales
│
└── apps/
    ├── usuarios/                    # Usuario.java + UserDetails + AuthController
    │   ├── models.py                # Usuario, Rol
    │   ├── backends.py              # loadUserByUsername()
    │   ├── decorators.py            # hasAnyRole()
    │   ├── views.py                 # AuthController
    │   ├── forms.py
    │   └── urls.py
    │
    ├── productos/                   # Producto.java + IndexController
    │   ├── models.py                # Producto + ProductoService.filtrar()
    │   ├── views.py                 # IndexController (/, /hombres, etc.)
    │   └── urls.py
    │
    ├── categorias/                  # Categoria.java + CategoriaService
    │   └── models.py
    │
    ├── clientes/                    # Cliente.java + ClienteService
    │   └── models.py
    │
    ├── carrito/                     # CarritoService (@SessionScope) + CarritoController
    │   ├── services.py              # Lógica del carrito en session
    │   ├── context_processors.py   # cantidadItems automático en todos los templates
    │   ├── views.py                 # CarritoController (AJAX + checkout)
    │   └── urls.py
    │
    ├── admin_panel/                 # AdminController
    │   ├── views.py                 # dashboard + CRUD completo
    │   └── urls.py
    │
    └── reportes/                    # PdfGenerator + reporteXxx()
        ├── views.py                 # Genera PDF con ReportLab
        └── urls.py
```

---

## Notas importantes

- **`managed = False`** en todos los modelos: Django no altera las tablas existentes.
- **Autenticación por email**: agrega en `settings.py`:
  ```python
  AUTHENTICATION_BACKENDS = ['apps.usuarios.backends.EmailBackend']
  ```
- **CSRF en carrito**: Django protege con CSRF por defecto. El JS del carrito debe
  incluir el token:
  ```javascript
  headers: { 'X-CSRFToken': document.cookie.match(/csrftoken=([^;]+)/)?.[1] }
  ```
- **Contraseñas**: Django usa PBKDF2 por defecto. Las contraseñas BCrypt existentes
  en la BD no serán reconocidas directamente. Para migrar, añade en `settings.py`:
  ```python
  PASSWORD_HASHERS = [
      'django.contrib.auth.hashers.BCryptSHA256PasswordHasher',
      'django.contrib.auth.hashers.PBKDF2PasswordHasher',
  ]
  # pip install bcrypt
  ```
