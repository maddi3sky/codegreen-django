"""
Management command to import inline JS data files into the database.

Usage:
    python manage.py load_ndvi
"""
import re
import sys
from pathlib import Path
from django.core.management.base import BaseCommand
from django.db import transaction
from map.models import Site, DataPoint

SITES_CONFIG = [
    {
        'id': 'wilmington',
        'name': '🇺🇸 Wilmington, NC',
        'title': 'Code Green — Wilmington Green Space Tracker',
        'subtitle': 'YSA Global STEM Ambassadors · NASA/USGS Satellite Data · Wilmington, NC · 2019–2026',
        'js_file': 'ndvi_all_years_inline.js',
        'var_name': 'RAW_DATA',
    },
    {
        'id': 'chisinau',
        'name': '🇲🇩 Chisinau, Moldova',
        'title': 'Code Green MD — Chisinau Green Space Tracker',
        'subtitle': 'YSA Global STEM Ambassadors · NASA/USGS Satellite Data · Moldova · 2019–2026',
        'js_file': 'ndvi_chisinau_inline.js',
        'var_name': 'RAW_DATA_CHISINAU',
    },
    {
        'id': 'lozova',
        'name': '🇲🇩 Lozova, Strășeni',
        'title': 'Code Green MD — Lozova Green Space Tracker',
        'subtitle': 'YSA Global STEM Ambassadors · NASA/USGS Satellite Data · Strășeni Raion, Moldova · 2019–2026',
        'js_file': 'ndvi_lozova_inline.js',
        'var_name': 'RAW_DATA_LOZOVA',
    },
]

# Look for JS files in Django's STATICFILES_DIRS, then BASE_DIR/static
from django.conf import settings as _settings
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent

def _find_js(filename):
    candidates = [BASE_DIR / 'static' / filename]
    if hasattr(_settings, 'STATICFILES_DIRS'):
        for d in _settings.STATICFILES_DIRS:
            candidates.append(Path(d) / filename)
    for p in candidates:
        if p.exists():
            return p
    return None


def parse_js_file(path, var_name):
    """Extract {year: [{lat, lng, ndvi}]} from an inline JS data file."""
    content = path.read_text()
    result = {}
    pattern = re.compile(rf'{re.escape(var_name)}\[(\d{{4}})\]\s*=\s*\[(.*?)\];', re.DOTALL)
    for m in pattern.finditer(content):
        year = int(m.group(1))
        pts_raw = re.findall(r'"ndvi":\s*([\d.]+),\s*"lat":\s*([\d.]+),\s*"lng":\s*([-\d.]+)', m.group(2))
        if not pts_raw:
            pts_raw = re.findall(r'"lat":\s*([\d.]+),\s*"lng":\s*([-\d.]+),\s*"ndvi":\s*([\d.]+)', m.group(2))
            pts_raw = [(c, a, b) for a, b, c in pts_raw]
        result[year] = [{'ndvi': float(n), 'lat': float(la), 'lng': float(ln)} for n, la, ln in pts_raw]
    return result


class Command(BaseCommand):
    help = 'Import NDVI inline JS data files into the database'

    def add_arguments(self, parser):
        parser.add_argument('--site', type=str, help='Only load a specific site id')
        parser.add_argument('--clear', action='store_true', help='Clear existing data before loading')

    def handle(self, *args, **options):
        target = options.get('site')
        configs = [c for c in SITES_CONFIG if not target or c['id'] == target]

        for cfg in configs:
            js_path = _find_js(cfg['js_file'])
            if not js_path:
                self.stdout.write(self.style.WARNING(f"  Skipping {cfg['id']} — {cfg['js_file']} not found in static dirs"))
                continue

            self.stdout.write(f"Loading {cfg['id']} from {js_path.name}...")
            site, _ = Site.objects.get_or_create(
                id=cfg['id'],
                defaults={'name': cfg['name'], 'title': cfg['title'], 'subtitle': cfg['subtitle']}
            )

            if options['clear']:
                deleted, _ = DataPoint.objects.filter(site=site).delete()
                self.stdout.write(f"  Cleared {deleted} existing points")

            data = parse_js_file(js_path, cfg['var_name'])
            total = 0
            with transaction.atomic():
                for year, pts in data.items():
                    # Skip years already loaded (unless --clear was used)
                    if not options['clear'] and DataPoint.objects.filter(site=site, year=year).exists():
                        self.stdout.write(f"  {year}: already loaded, skipping")
                        continue
                    objs = [DataPoint(site=site, year=year, lat=p['lat'], lng=p['lng'], ndvi=p['ndvi']) for p in pts]
                    DataPoint.objects.bulk_create(objs, batch_size=500)
                    total += len(objs)
                    self.stdout.write(f"  {year}: {len(objs)} points")

            self.stdout.write(self.style.SUCCESS(f"  {cfg['id']} done — {total} points total\n"))
