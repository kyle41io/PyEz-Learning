from django.core.management.base import BaseCommand
from django.contrib.sites.models import Site


class Command(BaseCommand):
    help = 'Update Site domain for production'

    def add_arguments(self, parser):
        parser.add_argument('domain', type=str, help='New domain (e.g., pyez-learning.onrender.com)')

    def handle(self, *args, **options):
        domain = options['domain']
        
        try:
            site = Site.objects.get(id=1)
            old_domain = site.domain
            site.domain = domain
            site.name = 'PyEz Learning'
            site.save()
            self.stdout.write(self.style.SUCCESS(f'Successfully updated site domain from "{old_domain}" to "{domain}"'))
        except Site.DoesNotExist:
            site = Site.objects.create(id=1, domain=domain, name='PyEz Learning')
            self.stdout.write(self.style.SUCCESS(f'Successfully created site with domain "{domain}"'))
