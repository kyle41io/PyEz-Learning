"""
Management command to setup Google OAuth credentials
Usage: python manage.py setup_google_oauth_credentials
"""
import os
from django.core.management.base import BaseCommand
from django.contrib.sites.models import Site
from allauth.socialaccount.models import SocialApp
from dotenv import load_dotenv

load_dotenv()


class Command(BaseCommand):
    help = 'Setup Google OAuth credentials for django-allauth'

    def handle(self, *args, **options):
        # Load Google OAuth credentials from .env file
        CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID')
        CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET')
        
        if not CLIENT_ID or not CLIENT_SECRET:
            self.stdout.write(self.style.ERROR('Error: GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET must be set in .env file'))
            return
        
        # Get or create the Site
        site, created = Site.objects.get_or_create(
            id=1,
            defaults={'domain': 'localhost:8000', 'name': 'PyEz Learning'}
        )
        if not created:
            # Update if it exists but has different values
            if site.domain != 'localhost:8000' or site.name != 'PyEz Learning':
                site.domain = 'localhost:8000'
                site.name = 'PyEz Learning'
                site.save()
                self.stdout.write(self.style.SUCCESS(f'Updated site: {site.domain}'))
            else:
                self.stdout.write(self.style.SUCCESS(f'Site already configured: {site.domain}'))
        else:
            self.stdout.write(self.style.SUCCESS(f'Created site: {site.domain}'))
        
        # Count and delete existing Google OAuth apps
        existing_count = SocialApp.objects.filter(provider='google').count()
        if existing_count > 0:
            self.stdout.write(self.style.WARNING(f'Found {existing_count} existing Google OAuth app(s)'))
            deleted = SocialApp.objects.filter(provider='google').delete()
            self.stdout.write(self.style.SUCCESS(f'Deleted {deleted[0]} Google OAuth app(s)'))
        
        # Create Google OAuth app
        google_app = SocialApp.objects.create(
            provider='google',
            name='Google OAuth',
            client_id=CLIENT_ID,
            secret=CLIENT_SECRET,
        )
        
        # Associate with site
        google_app.sites.add(site)
        google_app.save()
        
        # Verify only one exists
        final_count = SocialApp.objects.filter(provider='google').count()
        
        self.stdout.write(self.style.SUCCESS('✓ Google OAuth app created successfully'))
        self.stdout.write(self.style.SUCCESS(f'  Client ID: {CLIENT_ID}'))
        self.stdout.write(self.style.SUCCESS(f'  Provider: google'))
        self.stdout.write(self.style.SUCCESS(f'  Associated with site: {site.domain}'))
        self.stdout.write(self.style.SUCCESS(f'  Total Google OAuth apps in DB: {final_count}'))
        self.stdout.write(self.style.WARNING('\nMake sure these URLs are authorized in Google Cloud Console:'))
        self.stdout.write(self.style.WARNING('  - http://localhost:8000/accounts/google/login/callback/'))
        self.stdout.write(self.style.WARNING('  - http://localhost:8000/en/accounts/google/login/callback/'))
        self.stdout.write(self.style.WARNING('  - http://localhost:8000/vi/accounts/google/login/callback/'))
