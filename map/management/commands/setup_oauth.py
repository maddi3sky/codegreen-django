import os
from django.core.management.base import BaseCommand
from django.contrib.sites.models import Site
from allauth.socialaccount.models import SocialApp


class Command(BaseCommand):
    help = 'Configure Google OAuth Social Application from environment variables'

    def handle(self, *args, **options):
        client_id = os.environ.get('GOOGLE_CLIENT_ID', '')
        secret = os.environ.get('GOOGLE_CLIENT_SECRET', '')
        domain = os.environ.get('SITE_DOMAIN', '127.0.0.1:8000')
        name = os.environ.get('SITE_NAME', 'Code Green')

        if not client_id or not secret:
            self.stdout.write(self.style.WARNING('GOOGLE_CLIENT_ID/SECRET not set — skipping OAuth setup'))
            return

        site, _ = Site.objects.update_or_create(
            id=1, defaults={'domain': domain, 'name': name}
        )

        app, created = SocialApp.objects.get_or_create(
            provider='google',
            defaults={'name': 'Google', 'client_id': client_id, 'secret': secret}
        )
        if not created:
            app.client_id = client_id
            app.secret = secret
            app.save()

        if not app.sites.filter(id=site.id).exists():
            app.sites.add(site)

        self.stdout.write(self.style.SUCCESS(f'Google OAuth configured for {domain}'))
