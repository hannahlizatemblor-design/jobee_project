from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from jobee_app.models import AdminProfile

class Command(BaseCommand):
    help = 'Reset admin password'

    def add_arguments(self, parser):
        parser.add_argument('admin_id', type=str, help='Admin ID to reset password for')
        parser.add_argument('new_password', type=str, help='New password')

    def handle(self, *args, **options):
        admin_id = options['admin_id']
        new_password = options['new_password']

        try:
            admin_profile = AdminProfile.objects.get(admin_id=admin_id)
            user = admin_profile.user
            user.set_password(new_password)
            user.save()

            self.stdout.write(
                self.style.SUCCESS(f'Successfully reset password for admin {admin_id} ({admin_profile.username})')
            )
        except AdminProfile.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'Admin with ID {admin_id} not found')
            )