from django.core.management.base import BaseCommand
from finances.exchange import fetch_exchange_rates, rates_stale


class Command(BaseCommand):
    help = 'Actualiza las cotizaciones de moneda desde la API (open.er-api.com)'

    def add_arguments(self, parser):
        parser.add_argument('--force', action='store_true', help='Fuerza la actualización ignorando el TTL')

    def handle(self, *args, **options):
        if not options['force'] and not rates_stale():
            self.stdout.write(self.style.WARNING('Cotizaciones al día, no se llamó a la API'))
            return
        ok, msg = fetch_exchange_rates(force=options['force'])
        if ok:
            self.stdout.write(self.style.SUCCESS(msg))
        else:
            self.stdout.write(self.style.ERROR(msg))
