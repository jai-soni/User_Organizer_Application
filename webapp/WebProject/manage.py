#!/usr/bin/env python
import os
import sys

if __name__ == '__main__':
	if (!os.environ['PROFILE']):
		os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'WebProject.settings_test')
	elif (os.environ['PROFILE']=="default"):
		os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'WebProject.setting_default')
	else:
		os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'WebProject.setting_test')
	try:
		from django.core.management import execute_from_command_line
	except ImportError as exc:
		raise ImportError(
			"Couldn't import Django. Are you sure it's installed and "
			"available on your PYTHONPATH environment variable? Did you "
			"forget to activate a virtual environment?"
		) from exc
	execute_from_command_line(sys.argv)