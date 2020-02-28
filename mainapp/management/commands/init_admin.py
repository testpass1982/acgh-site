from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.conf import settings
import json
import os

with open(os.path.join(settings.BASE_DIR, 'secret.json'), 'r') as secret_file:
    secret = json.load(secret_file)
    ADMIN, PASSWORD, EMAIL = secret['site_admin'], secret['site_admin_password'], secret['site_admin_email']

class Command(BaseCommand):
    def handle(self, *args, **options):
        if User.objects.count() == 0:
            admin = User.objects.create_superuser(
                username=ADMIN,
                password=PASSWORD,
                email=EMAIL)
            admin.is_active = True
            admin.is_admin = True
            admin.save()
            print('Admin created')
        else:
            print('Superuser already created')
