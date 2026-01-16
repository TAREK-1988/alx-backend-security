from django.core.management.base import BaseCommand, CommandError
from ip_tracking.models import BlockedIP


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("ip_address", type=str)

    def handle(self, *args, **options):
        ip_address = options["ip_address"].strip()
        if not ip_address:
            raise CommandError("ip_address is required")

        obj, created = BlockedIP.objects.get_or_create(ip_address=ip_address)
        if created:
            self.stdout.write(self.style.SUCCESS(f"Blocked {obj.ip_address}"))
        else:
            self.stdout.write(self.style.WARNING(f"Already blocked {obj.ip_address}"))

