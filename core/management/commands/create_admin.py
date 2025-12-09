import os
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

class Command(BaseCommand):
    help = 'Creates a superuser if one does not exist'

    def handle(self, *args, **options):
        User = get_user_model()
        # --- مقادیر زیر را با اطلاعات دلخواه خودتان جایگزین کنید ---
        ADMIN_USERNAME = 'ieajohsila'
        ADMIN_EMAIL = 'alishojaei73@gmail.com'
        ADMIN_PASSWORD = 'i7gnUCgV!' # <-- یک رمز عبور قوی انتخاب کنید

        if not User.objects.filter(username=ADMIN_USERNAME).exists():
            self.stdout.write(self.style.SUCCESS(f"Creating account for {ADMIN_USERNAME}"))
            User.objects.create_superuser(ADMIN_USERNAME, ADMIN_EMAIL, ADMIN_PASSWORD)
        else:
            self.stdout.write(self.style.WARNING(f"Admin user '{ADMIN_USERNAME}' already exists. Skipping."))
