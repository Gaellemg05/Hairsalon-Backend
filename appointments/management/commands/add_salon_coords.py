import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from salons.models import Salon

# Add coordinates to salons
cities = {
    'Beauty Palace Douala': (4.0511, 9.7679),
    'Glow Beauty Lounge': (3.8480, 11.5021),
    'Afro Chic Buea': (4.1550, 9.2420),
}

for salon_name, (lat, lng) in cities.items():
    try:
        salon = Salon.objects.get(name=salon_name)
        salon.latitude = lat
        salon.longitude = lng
        salon.save()
        print(f"Updated {salon_name}: {lat}, {lng}")
    except Salon.DoesNotExist:
        print(f"Salon not found: {salon_name}")

print("Done updating coordinates.")
