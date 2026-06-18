import os
from django.core.management.base import BaseCommand
from django.contrib.sites.models import Site
from allauth.socialaccount.models import SocialApp


class Command(BaseCommand):
    help = 'Configure Google OAuth Social Application from environment variables'

    def handle(self, *args, **options):
        client_id = os.environ.get('GOOGLE_CLIENT_ID', '').strip()
        secret = os.environ.get('GOOGLE_CLIENT_SECRET', '').strip()
        domain = os.environ.get('SITE_DOMAIN', '127.0.0.1:8000').strip()
        name = os.environ.get('SITE_NAME', 'Code Green')

        if not client_id or not secret:
            self.stdout.write(self.style.WARNING('GOOGLE_CLIENT_ID/SECRET not set — skipping OAuth setup'))
            return

        site, _ = Site.objects.update_or_create(
            id=1, defaults={'domain': domain, 'name': name}
        )

        # Delete all existing Google apps to avoid MultipleObjectsReturned
        SocialApp.objects.filter(provider='google').delete()

        app = SocialApp.objects.create(
            provider='google',
            name='Google',
            client_id=client_id,
            secret=secret,
        )
        app.sites.add(site)

        self.stdout.write(self.style.SUCCESS(f'Google OAuth configured for {domain}'))
