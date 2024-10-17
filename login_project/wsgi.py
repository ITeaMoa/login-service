"""
WSGI config for login project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/wsgi/
"""
# login_project/wsgi.py

import os
from django.core.wsgi import get_wsgi_application

# Set the correct settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'login_project.settings')

application = get_wsgi_application()
