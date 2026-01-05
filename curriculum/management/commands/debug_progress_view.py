from django.core.management.base import BaseCommand
from curriculum.models import Lesson, Progress, Chapter
from users.models import User


class Command(BaseCommand):
    help = 'Debug progress view data'

    def handle(self, *args, **options):
        student = User.objects.filter(role='student').first()
        
        if not student:
            self.stdout.write(self.style.ERROR('No student found!'))
            return
        
        self.stdout.write(f'Debugging for student: {student.username}')
        self.stdout.write(f'Student progress: {student.progress_percent}%\n')
        
        # Check chapters
        chapters = Chapter.objects.prefetch_related('lessons').order_by('order')
        self.stdout.write(f'Total chapters: {chapters.count()}')
        
        lessons_progress = []
        
        # Check if chapters exist
        if chapters.exists():
            # Group lessons by chapter
            for chapter in chapters:
                self.stdout.write(f'\n--- Chapter {chapter.order}: {chapter.title} ---')
                chapter_lessons = []
                
                for lesson in chapter.lessons.all().order_by('order'):
                    progress = Progress.objects.filter(student=student, lesson=lesson).first()
                    
                    self.stdout.write(f'  Lesson {lesson.order}: {lesson.title}')
                    if progress:
                        self.stdout.write(f'    Progress exists: completed={progress.is_completed}')
                        self.stdout.write(f'    Quiz: passed={progress.quiz_passed}, at={progress.quiz_passed_at}')
                        self.stdout.write(f'    Code: passed={progress.code_test_passed}, at={progress.code_test_passed_at}')
                        self.stdout.write(f'    Completed at: {progress.completed_at}')
                    else:
                        self.stdout.write(f'    No progress record')
                    
                    # Check lesson content
                    has_quiz = lesson.quiz and len(lesson.quiz) > 0
                    has_coding = lesson.coding and len(lesson.coding) > 0
                    self.stdout.write(f'    Has quiz: {has_quiz}, Has coding: {has_coding}')
                    
                    lesson_data = {
                        'lesson': lesson,
                        'progress': progress,
                        'is_completed': progress.is_completed if progress else False,
                        'quiz_passed': progress.quiz_passed if progress else False,
                        'quiz_passed_at': progress.quiz_passed_at if progress else None,
                        'code_test_passed': progress.code_test_passed if progress else False,
                        'code_test_passed_at': progress.code_test_passed_at if progress else None,
                        'completed_at': progress.completed_at if progress else None,
                    }
                    chapter_lessons.append(lesson_data)
                
                if chapter_lessons:
                    lessons_progress.append({
                        'chapter': chapter,
                        'lessons': chapter_lessons
                    })
                    self.stdout.write(f'  ✓ Chapter added with {len(chapter_lessons)} lessons')
                else:
                    self.stdout.write(f'  ✗ Chapter skipped (no lessons)')
        else:
            # If no chapters exist, show all lessons without chapter grouping
            self.stdout.write('\n--- No chapters found, showing all lessons ---')
            all_lessons = Lesson.objects.all().order_by('order')
            
            if all_lessons.exists():
                chapter_lessons = []
                for lesson in all_lessons:
                    progress = Progress.objects.filter(student=student, lesson=lesson).first()
                    
                    self.stdout.write(f'  Lesson {lesson.order}: {lesson.title}')
                    if progress:
                        self.stdout.write(f'    Progress exists: completed={progress.is_completed}')
                        self.stdout.write(f'    Quiz: passed={progress.quiz_passed}, at={progress.quiz_passed_at}')
                        self.stdout.write(f'    Code: passed={progress.code_test_passed}, at={progress.code_test_passed_at}')
                        self.stdout.write(f'    Completed at: {progress.completed_at}')
                    else:
                        self.stdout.write(f'    No progress record')
                    
                    # Check lesson content
                    has_quiz = lesson.quiz and len(lesson.quiz) > 0
                    has_coding = lesson.coding and len(lesson.coding) > 0
                    self.stdout.write(f'    Has quiz: {has_quiz}, Has coding: {has_coding}')
                    
                    lesson_data = {
                        'lesson': lesson,
                        'progress': progress,
                        'is_completed': progress.is_completed if progress else False,
                        'quiz_passed': progress.quiz_passed if progress else False,
                        'quiz_passed_at': progress.quiz_passed_at if progress else None,
                        'code_test_passed': progress.code_test_passed if progress else False,
                        'code_test_passed_at': progress.code_test_passed_at if progress else None,
                        'completed_at': progress.completed_at if progress else None,
                    }
                    chapter_lessons.append(lesson_data)
                
                # Create a default "All Lessons" chapter
                lessons_progress.append({
                    'chapter': {'title': 'All Lessons', 'order': 1},
                    'lessons': chapter_lessons
                })
                self.stdout.write(f'  ✓ Added "All Lessons" group with {len(chapter_lessons)} lessons')
            else:
                self.stdout.write(f'  ✗ No lessons found in database')
        
        self.stdout.write(f'\n\nTotal chapters in lessons_progress: {len(lessons_progress)}')
        
        # Show what will be passed to template
        self.stdout.write('\n--- Data for Template ---')
        for chapter_data in lessons_progress:
            chapter = chapter_data["chapter"]
            chapter_title = chapter.title if hasattr(chapter, 'title') else chapter.get('title', 'Unknown')
            self.stdout.write(f'Chapter: {chapter_title}')
            for lesson_data in chapter_data['lessons']:
                self.stdout.write(f'  - Lesson {lesson_data["lesson"].order}: completed={lesson_data["is_completed"]}, '
                                f'quiz_passed={lesson_data["quiz_passed"]}, code_passed={lesson_data["code_test_passed"]}')
