
from django.core.management.base import BaseCommand
from potholes.models import Pothole

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        Pothole.objects.create(latitude=17.385, longitude=78.486, severity="High")
        self.stdout.write(self.style.SUCCESS("Seeded sample potholes"))
