from django.core.management.base import BaseCommand
from users.models import User


class Command(BaseCommand):
    help = 'Fix role field for existing superuser/staff accounts'

    def handle(self, *args, **options):
        # Update all superusers and staff to have admin role
        updated_count = 0
        
        superusers = User.objects.filter(is_superuser=True, is_staff=True)
        for user in superusers:
            if user.role != 'admin':
                user.role = 'admin'
                user.save()
                updated_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Updated {user.username} to admin role')
                )
        
        self.stdout.write(
            self.style.SUCCESS(f'\nTotal users updated: {updated_count}')
        )
