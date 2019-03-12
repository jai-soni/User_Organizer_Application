"""
WSGI config for WebProject project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/2.1/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

if (os.environ['PROFILE']=="dev"):
	os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'WebProject.settings_dev')
elif (os.environ['PROFILE']=="default"):
	os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'WebProject.setting_default')
else:
	os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'WebProject.setting_test')

application = get_wsgi_application()
