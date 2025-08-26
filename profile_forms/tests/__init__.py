from django.core.management import call_command
from django.db import transaction


def seed_health_catalogs():
    """
    Seed the health catalogs with common chronic diseases, medicines, and allergies.
    """
    with transaction.atomic():
        call_command("seed_health_catalogs")
        print("Health catalogs seeded successfully.")
