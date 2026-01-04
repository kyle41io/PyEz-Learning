from django.core.management.base import BaseCommand
from curriculum.models import Lesson


class Command(BaseCommand):
    help = 'Assign game HTML files to appropriate lessons'

    def handle(self, *args, **options):
        game_assignments = {
            6: 'Game1.html',   # Lesson 6 - Beginner questions game
            10: 'Game2.html',  # Lesson 10 - Bridge game with True/False questions
            13: 'Game1.html',  # Lesson 13 - Advanced questions game (same game, different questions)
            16: 'Game3.html',  # Lesson 16 - Final comprehensive challenge
        }

        updated_count = 0
        created_count = 0
        
        for lesson_order, game_name in game_assignments.items():
            try:
                lesson = Lesson.objects.get(order=lesson_order)
                lesson.game = game_name
                lesson.save()
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f'✓ Assigned {game_name} to Lesson {lesson_order}: {lesson.title}'
                    )
                )
                updated_count += 1
                
            except Lesson.DoesNotExist:
                self.stdout.write(
                    self.style.WARNING(
                        f'⚠ Lesson {lesson_order} not found. Skipping...'
                    )
                )
                
        self.stdout.write(
            self.style.SUCCESS(
                f'\n✓ Game assignment complete! Updated {updated_count} lessons.'
            )
        )
        
        # Show summary
        self.stdout.write('\nGame Assignment Summary:')
        self.stdout.write('=' * 60)
        self.stdout.write('Lesson 6  → Game1.html (Beginner Python Questions)')
        self.stdout.write('Lesson 10 → Game2.html (PyBridge: Syntax Survivor)')
        self.stdout.write('Lesson 13 → Game1.html (Advanced Python Questions)')
        self.stdout.write('Lesson 16 → Game3.html (Final Challenge: Code Master)')
        self.stdout.write('=' * 60)
