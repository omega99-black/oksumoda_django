"""
oksumoda/wsgi.py — punto de entrada WSGI para producción.
Equivalente al servidor embebido Tomcat de Spring Boot.
"""

import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'oksumoda.settings')
application = get_wsgi_application()
