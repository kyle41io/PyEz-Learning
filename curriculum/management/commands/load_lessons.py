import os
import re
from django.core.management.base import BaseCommand
from curriculum.models import Lesson


class Command(BaseCommand):
    help = 'Load lessons from PDF files in curriculum/docs'

    def handle(self, *args, **options):
        # Path to the docs folder
        docs_path = 'curriculum/docs'
        
        # Get all PDF files
        pdf_files = [f for f in os.listdir(docs_path) if f.endswith('.pdf')]
        pdf_files.sort()  # Sort alphabetically
        
        created_count = 0
        updated_count = 0
        
        for pdf_file in pdf_files:
            # Extract order and title from filename
            # Format: 'Bài X_Title.pdf'
            match = re.match(r'Bài (\d+)_(.+)\.pdf', pdf_file)
            
            if match:
                order = int(match.group(1))
                title = match.group(2)
                
                # File path relative to media root
                pdf_path = f'lessons/docs/{pdf_file}'
                
                # Create or update lesson
                lesson, created = Lesson.objects.update_or_create(
                    order=order,
                    defaults={
                        'title': title,
                        'points_value': 10,
                        'pdf_file': pdf_path,
                    }
                )
                
                if created:
                    created_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(f'Created lesson {order}: {title}')
                    )
                else:
                    updated_count += 1
                    self.stdout.write(
                        self.style.WARNING(f'Updated lesson {order}: {title}')
                    )
            else:
                self.stdout.write(
                    self.style.ERROR(f'Could not parse filename: {pdf_file}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\nCompleted: {created_count} created, {updated_count} updated'
            )
        )
