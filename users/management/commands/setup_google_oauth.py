"""
Management command to set up Google OAuth credentials in the database.
Usage: python manage.py setup_google_oauth <client_id> <client_secret>
"""

from django.core.management.base import BaseCommand
from django.contrib.sites.models import Site
from allauth.socialaccount.models import SocialApp


class Command(BaseCommand):
    help = 'Set up Google OAuth credentials in the database'

    def add_arguments(self, parser):
        parser.add_argument('client_id', type=str, help='Google OAuth Client ID')
        parser.add_argument('client_secret', type=str, help='Google OAuth Client Secret')

    def handle(self, *args, **options):
        client_id = options['client_id']
        client_secret = options['client_secret']
        
        if not client_id or not client_secret:
            self.stdout.write(
                self.style.ERROR('Error: Both client_id and client_secret are required')
            )
            return
        
        try:
            # Get or create the site
            site = Site.objects.get_current()
            
            # Get or create Google OAuth app
            app, created = SocialApp.objects.get_or_create(
                provider='google',
                defaults={
                    'name': 'Google OAuth',
                    'client_id': client_id,
                    'secret': client_secret,
                }
            )
            
            if not created:
                # Update existing app
                app.client_id = client_id
                app.secret = client_secret
                app.save()
                self.stdout.write(
                    self.style.SUCCESS('Updated existing Google OAuth credentials')
                )
            else:
                self.stdout.write(
                    self.style.SUCCESS('Created new Google OAuth credentials')
                )
            
            # Ensure the app is linked to the current site
            if site not in app.sites.all():
                app.sites.add(site)
            
            self.stdout.write(
                self.style.SUCCESS('✅ Google OAuth has been successfully configured!')
            )
            self.stdout.write(f'Site: {site.domain}')
            self.stdout.write(f'Client ID: {client_id[:20]}...')
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error setting up Google OAuth: {str(e)}')
            )
