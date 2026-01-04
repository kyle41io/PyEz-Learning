from django.core.management.base import BaseCommand
from users.models import User
from curriculum.models import Lesson, Progress


class Command(BaseCommand):
    help = 'Update progress_percent field for all students based on completed lessons'

    def handle(self, *args, **options):
        students = User.objects.filter(role='student')
        total_lessons = Lesson.objects.count()
        
        if total_lessons == 0:
            self.stdout.write(self.style.WARNING('No lessons found in the database.'))
            return
        
        updated_count = 0
        for student in students:
            completed_lessons = Progress.objects.filter(
                student=student, 
                is_completed=True
            ).count()
            
            progress_percent = int((completed_lessons / total_lessons) * 100)
            
            # Only update if changed
            if student.progress_percent != progress_percent:
                student.progress_percent = progress_percent
                student.save(update_fields=['progress_percent'])
                updated_count += 1
                
                self.stdout.write(
                    f'Updated {student.username}: {completed_lessons}/{total_lessons} lessons = {progress_percent}%'
                )
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully updated {updated_count} students out of {students.count()}')
        )
