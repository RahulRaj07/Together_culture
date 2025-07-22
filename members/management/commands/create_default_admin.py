from django.core.management.base import BaseCommand
from members.models import Member
from django.conf import settings

class Command(BaseCommand):
    help = 'Creates the default admin user only if it does not exist'

    def handle(self, *args, **kwargs):
        if not Member.objects.filter(is_admin=True).exists():
            Member.objects.create_superuser(
                username='admin',
                email='admin@example.com',
                password='admin123',
                is_admin=True,
                is_approved=True
            )
            self.stdout.write(self.style.SUCCESS('Default admin created.'))
        else:
            self.stdout.write(self.style.WARNING('Admin already exists.'))
