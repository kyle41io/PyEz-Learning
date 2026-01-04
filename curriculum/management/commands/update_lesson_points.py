from django.core.management.base import BaseCommand
from curriculum.models import Lesson

class Command(BaseCommand):
    help = 'Update all lessons to have 20 points'

    def handle(self, *args, **kwargs):
        lessons = Lesson.objects.all()
        count = 0
        
        for lesson in lessons:
            lesson.points_value = 20
            lesson.save()
            count += 1
            self.stdout.write(f'  Updated Lesson {lesson.order}: {lesson.title} -> 20 stars')
        
        self.stdout.write(self.style.SUCCESS(f'\n✓ Updated {count} lessons to 20 stars each'))
