#!/usr/bin/env python
"""
manage.py — equivalente al punto de entrada de Spring Boot (main class).
Uso:
  python manage.py runserver          # Equivalente a mvn spring-boot:run
  python manage.py migrate            # Equivalente a Hibernate auto-ddl
  python manage.py createsuperuser    # Crear administrador
"""

import os
import sys


def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'oksumoda.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "No se pudo importar Django. Asegúrate de tenerlo instalado "
            "y de haber activado el entorno virtual."
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
