from django.core.management.base import BaseCommand
from django.core.management import call_command
from curriculum.models import Lesson


class Command(BaseCommand):
    help = 'Initialize database with backup data if empty'

    def handle(self, *args, **options):
        # Check if lessons exist
        lesson_count = Lesson.objects.count()
        
        if lesson_count == 0:
            self.stdout.write(self.style.WARNING('Database is empty. Loading data from backup...'))
            try:
                call_command('loaddata', 'data_backup.json')
                self.stdout.write(self.style.SUCCESS('✓ Successfully loaded data from backup'))
                
                # Verify
                new_count = Lesson.objects.count()
                self.stdout.write(self.style.SUCCESS(f'  Loaded {new_count} lessons'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'✗ Error loading data: {str(e)}'))
        else:
            self.stdout.write(self.style.SUCCESS(f'✓ Database already has {lesson_count} lessons. Skipping data load.'))
