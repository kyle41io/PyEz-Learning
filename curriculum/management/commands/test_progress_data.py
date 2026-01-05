from django.core.management.base import BaseCommand
from django.utils import timezone
from curriculum.models import Lesson, Progress, Chapter
from users.models import User


class Command(BaseCommand):
    help = 'Create test progress data for debugging'

    def handle(self, *args, **options):
        # Get or create a test student
        student = User.objects.filter(role='student').first()
        
        if not student:
            self.stdout.write(self.style.ERROR('No student found in database!'))
            return
        
        self.stdout.write(f'Using student: {student.username} (ID: {student.id})')
        
        # Get all lessons
        lessons = Lesson.objects.all().order_by('order')
        
        if not lessons:
            self.stdout.write(self.style.ERROR('No lessons found in database!'))
            return
        
        self.stdout.write(f'Found {lessons.count()} lessons')
        
        # Mark first 2 lessons as completed with timestamps
        for i, lesson in enumerate(lessons[:2]):
            progress, created = Progress.objects.get_or_create(
                student=student,
                lesson=lesson
            )
            
            # Unlock the lesson
            progress.is_unlocked = True
            
            # Check if lesson has quiz
            if lesson.quiz and len(lesson.quiz) > 0:
                progress.quiz_passed = True
                progress.quiz_passed_at = timezone.now()
                self.stdout.write(f'  ✓ Lesson {lesson.order}: Quiz marked as passed')
            
            # Check if lesson has coding test
            if lesson.coding and len(lesson.coding) > 0:
                progress.code_test_passed = True
                progress.code_test_passed_at = timezone.now()
                self.stdout.write(f'  ✓ Lesson {lesson.order}: Coding test marked as passed')
            
            # Mark as completed if both tests are passed
            has_quiz = lesson.quiz and len(lesson.quiz) > 0
            has_coding = lesson.coding and len(lesson.coding) > 0
            
            if has_quiz and has_coding:
                if progress.quiz_passed and progress.code_test_passed:
                    progress.is_completed = True
                    progress.completed_at = timezone.now()
            elif has_quiz and not has_coding:
                if progress.quiz_passed:
                    progress.is_completed = True
                    progress.completed_at = timezone.now()
            elif not has_quiz and has_coding:
                if progress.code_test_passed:
                    progress.is_completed = True
                    progress.completed_at = timezone.now()
            
            progress.save()
            
            if progress.is_completed:
                self.stdout.write(self.style.SUCCESS(f'  ✓ Lesson {lesson.order} "{lesson.title}" marked as COMPLETED'))
            else:
                self.stdout.write(f'  • Lesson {lesson.order} "{lesson.title}" in progress')
        
        # Update student's overall progress
        student.update_progress()
        
        self.stdout.write(self.style.SUCCESS(f'\n✓ Test data created successfully!'))
        self.stdout.write(f'Student progress: {student.progress_percent}%')
        self.stdout.write(f'Student stars: {student.star_points}')
        
        # Show progress data
        self.stdout.write('\n--- Progress Records ---')
        progress_records = Progress.objects.filter(student=student).order_by('lesson__order')
        for prog in progress_records:
            self.stdout.write(f'Lesson {prog.lesson.order}: completed={prog.is_completed}, '
                            f'quiz_passed={prog.quiz_passed}, quiz_passed_at={prog.quiz_passed_at}, '
                            f'code_passed={prog.code_test_passed}, code_passed_at={prog.code_test_passed_at}, '
                            f'completed_at={prog.completed_at}')
