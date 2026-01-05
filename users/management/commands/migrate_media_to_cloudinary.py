"""
Management command to migrate existing media files to Cloudinary
Usage: python manage.py migrate_media_to_cloudinary
"""
import os
from django.core.management.base import BaseCommand
from django.conf import settings
import cloudinary.uploader
from users.models import User
from curriculum.models import Lesson


class Command(BaseCommand):
    help = 'Migrate existing media files to Cloudinary'

    def handle(self, *args, **options):
        media_root = settings.MEDIA_ROOT
        uploaded_count = 0
        error_count = 0

        self.stdout.write(self.style.SUCCESS('Starting media migration to Cloudinary...'))

        # Migrate profile pictures
        self.stdout.write('\n=== Migrating Profile Pictures ===')
        profiles_dir = os.path.join(media_root, 'profiles')
        
        if os.path.exists(profiles_dir):
            for filename in os.listdir(profiles_dir):
                if filename.startswith('.'):
                    continue
                    
                file_path = os.path.join(profiles_dir, filename)
                if os.path.isfile(file_path):
                    try:
                        # Upload to Cloudinary
                        result = cloudinary.uploader.upload(
                            file_path,
                            folder='profiles',
                            public_id=os.path.splitext(filename)[0],
                            resource_type='auto',
                            overwrite=True
                        )
                        
                        # Update user records if filename matches pattern
                        # Store the Cloudinary path (not full URL) for CloudinaryStorage to handle
                        cloudinary_path = result['public_id'] + '.' + result['format']
                        relative_path = f"profiles/{filename}"
                        
                        users = User.objects.filter(profile_picture=relative_path)
                        if users.exists():
                            for user in users:
                                user.profile_picture = cloudinary_path
                                user.save()
                                self.stdout.write(
                                    self.style.SUCCESS(
                                        f'✓ Updated user {user.username}: {filename}'
                                    )
                                )
                        else:
                            self.stdout.write(
                                self.style.SUCCESS(f'✓ Uploaded: {filename}')
                            )
                        
                        uploaded_count += 1
                        
                    except Exception as e:
                        self.stdout.write(
                            self.style.ERROR(f'✗ Failed to upload {filename}: {str(e)}')
                        )
                        error_count += 1

        # Migrate lesson PDFs
        self.stdout.write('\n=== Migrating Lesson PDFs ===')
        lessons_docs_dir = os.path.join(media_root, 'lessons', 'docs')
        
        if os.path.exists(lessons_docs_dir):
            for filename in os.listdir(lessons_docs_dir):
                if filename.startswith('.'):
                    continue
                    
                file_path = os.path.join(lessons_docs_dir, filename)
                if os.path.isfile(file_path):
                    try:
                        # Upload to Cloudinary as raw file (for PDFs)
                        result = cloudinary.uploader.upload(
                            file_path,
                            folder='lessons/docs',
                            public_id=os.path.splitext(filename)[0],
                            resource_type='raw',  # Use 'raw' for PDFs
                            overwrite=True
                        )
                        
                        # Update lesson records if filename matches
                        # Store the Cloudinary path (not full URL) for CloudinaryStorage to handle
                        cloudinary_path = result['public_id'] + '.' + result['format']
                        relative_path = f"lessons/docs/{filename}"
                        
                        lessons = Lesson.objects.filter(pdf_file=relative_path)
                        if lessons.exists():
                            for lesson in lessons:
                                lesson.pdf_file = cloudinary_path
                                lesson.save()
                                self.stdout.write(
                                    self.style.SUCCESS(
                                        f'✓ Updated lesson {lesson.title}: {filename}'
                                    )
                                )
                        else:
                            self.stdout.write(
                                self.style.SUCCESS(f'✓ Uploaded: {filename}')
                            )
                        
                        uploaded_count += 1
                        
                    except Exception as e:
                        self.stdout.write(
                            self.style.ERROR(f'✗ Failed to upload {filename}: {str(e)}')
                        )
                        error_count += 1

        # Migrate game files if any
        self.stdout.write('\n=== Migrating Game Files ===')
        games_dir = os.path.join(media_root, 'games')
        
        if os.path.exists(games_dir):
            for filename in os.listdir(games_dir):
                if filename.startswith('.'):
                    continue
                    
                file_path = os.path.join(games_dir, filename)
                if os.path.isfile(file_path):
                    try:
                        # Upload to Cloudinary
                        result = cloudinary.uploader.upload(
                            file_path,
                            folder='games',
                            public_id=os.path.splitext(filename)[0],
                            resource_type='auto',
                            overwrite=True
                        )
                        
                        self.stdout.write(
                            self.style.SUCCESS(f'✓ Uploaded: {filename}')
                        )
                        uploaded_count += 1
                        
                    except Exception as e:
                        self.stdout.write(
                            self.style.ERROR(f'✗ Failed to upload {filename}: {str(e)}')
                        )
                        error_count += 1

        # Summary
        self.stdout.write('\n' + '='*50)
        self.stdout.write(
            self.style.SUCCESS(
                f'Migration complete: {uploaded_count} files uploaded, {error_count} errors'
            )
        )
        
        if error_count == 0:
            self.stdout.write(
                self.style.SUCCESS(
                    '\n✓ All media files successfully migrated to Cloudinary!'
                )
            )
        else:
            self.stdout.write(
                self.style.WARNING(
                    f'\n⚠ Migration completed with {error_count} errors. Check logs above.'
                )
            )
