import os
import sys
import django
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import time, date, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from users.models import User
from salons.models import Salon, Service, SalonPublication, HairstylePublication, Review
from appointments.models import Availability, Appointment, Chat, Message


class Command(BaseCommand):
    help = 'Populate the database with Cameroonian sample data'

    def handle(self, *args, **kwargs):
        self.stdout.write("Clearing existing data...")
        Appointment.objects.all().delete()
        Availability.objects.all().delete()
        Review.objects.all().delete()
        SalonPublication.objects.all().delete()
        HairstylePublication.objects.all().delete()
        Service.objects.all().delete()
        Salon.objects.all().delete()
        User.objects.filter(is_superuser=False).delete()
        self.stdout.write("Data cleared.")

        admin = None
        if not User.objects.filter(username='admin').exists():
            admin = User.objects.create_superuser('admin', 'admin@luxesalon.cm', 'admin123')
            admin.first_name = 'Admin'
            admin.last_name = 'User'
            admin.role = 'admin'
            admin.save()
            self.stdout.write(self.style.SUCCESS('Created superuser: admin / admin123'))
        else:
            admin = User.objects.get(username='admin')

        def get_or_create_user(username, password, email, first_name, last_name, role, phone_number=None, profile_picture=None):
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': email,
                    'first_name': first_name,
                    'last_name': last_name,
                    'role': role,
                    'phone_number': phone_number or '',
                    'profile_picture': profile_picture or '',
                }
            )
            if created:
                user.set_password(password)
                user.save()
                self.stdout.write(f"Created user: {username} ({role})")
            return user

        client1 = get_or_create_user('amira_tchoukeu', 'pass123', 'amira@example.cm', 'Amira', 'Tchoukeu', 'client', '+237 670 000 001')
        client2 = get_or_create_user('diane_mbarga', 'pass123', 'diane@example.cm', 'Diane', 'Mbarga', 'client', '+237 670 000 002')
        client3 = get_or_create_user('fatima_bello', 'pass123', 'fatima@example.cm', 'Fatima', 'Bello', 'client', '+237 670 000 003')

        hd1 = get_or_create_user('grace_ebot', 'pass123', 'grace@beautypalace.cm', 'Grace', 'Ebot', 'hairdresser', '+237 690 000 001', 'https://i.pravatar.cc/150?u=grace')
        hd2 = get_or_create_user('nadia_ndongo', 'pass123', 'nadia@glowbeauty.cm', 'Nadia', 'Ndongo', 'hairdresser', '+237 690 000 002', 'https://i.pravatar.cc/150?u=nadia')
        hd3 = get_or_create_user('solange_fotso', 'pass123', 'solange@afrochic.cm', 'Solange', 'Fotso', 'hairdresser', '+237 690 000 003', 'https://i.pravatar.cc/150?u=solange')
        hd4 = get_or_create_user('rachel_kamga', 'pass123', 'rachel@nailspiercing.cm', 'Rachel', 'Kamga', 'hairdresser', '+237 690 000 004', 'https://i.pravatar.cc/150?u=rachel')
        hd5 = get_or_create_user('michelle_tanya', 'pass123', 'michelle@nailspiercing.cm', 'Michelle', 'Tanya', 'hairdresser', '+237 690 000 005', 'https://i.pravatar.cc/150?u=michelle')

        salon1, _ = Salon.objects.get_or_create(
            name='Beauty Palace Douala',
            defaults={
                'description': 'Salon de beauté premium à Douala. Spécialisé dans les coiffures africaines, les tissages, les perruques et les soins capillaires.',
                'address': 'Rue du Marché, Akwa, Douala',
                'phone_number': '+237 233 100 001',
                'email': 'info@beautypalace.cm',
                'image_url': 'https://images.unsplash.com/photo-1595476108010-b4d1f102b1b1?w=800',
                'video_url': 'https://www.w3schools.com/html/mov_bbb.mp4',
                'latitude': 4.0511,
                'longitude': 9.7679,
                'manager': admin,
            }
        )

        salon2, _ = Salon.objects.get_or_create(
            name='Glow Beauty Lounge',
            defaults={
                'description': 'Lounge de beauté moderne à Yaoundé. Nous offrons des services de coiffure, onglerie, piercing et soins esthétiques dans un cadre relaxant.',
                'address': 'Bastos, Yaoundé',
                'phone_number': '+237 222 100 002',
                'email': 'hello@glowbeauty.cm',
                'image_url': 'https://images.unsplash.com/photo-1562322140-8baeececf3df?w=800',
                'video_url': '',
                'latitude': 3.8480,
                'longitude': 11.5021,
                'manager': admin,
            }
        )

        salon3, _ = Salon.objects.get_or_create(
            name='Afro Chic Buea',
            defaults={
                'description': 'Salon spécialisé dans les coiffures afro modernes, locks, braids et coupes créatives. Le rendez-vous de la femme moderne au Cameroun.',
                'address': 'Molyko, Buea',
                'phone_number': '+237 233 400 003',
                'email': 'contact@afrochic.cm',
                'image_url': 'https://images.unsplash.com/photo-1622287162716-f311361a2ae9?w=800',
                'video_url': '',
                'latitude': 4.1550,
                'longitude': 9.2420,
                'manager': admin,
            }
        )

        salon1.hairdressers.add(hd1, hd3)
        salon2.hairdressers.add(hd2, hd4, hd5)
        salon3.hairdressers.add(hd1, hd2)

        # Hair services
        Service.objects.get_or_create(salon=salon1, name='Tissage Africain', defaults={'description': 'Tissage naturel ou synthétique', 'price': 15000, 'duration': 120, 'category': 'hair'})
        Service.objects.get_or_create(salon=salon1, name='Perruque (Custom)', defaults={'description': 'Perruque sur mesure', 'price': 25000, 'duration': 90, 'category': 'hair'})
        Service.objects.get_or_create(salon=salon1, name='Défrisage', defaults={'description': 'Défrisage professionnel', 'price': 10000, 'duration': 90, 'category': 'hair'})
        Service.objects.get_or_create(salon=salon1, name='Tresses (Box Braids)', defaults={'description': 'Tresses africaines de qualité', 'price': 12000, 'duration': 150, 'category': 'hair'})
        Service.objects.get_or_create(salon=salon1, name='Soin Capillaire (Huile de Karité)', defaults={'description': 'Traitement hydratant au karité camerounais', 'price': 5000, 'duration': 45, 'category': 'skincare'})
        Service.objects.get_or_create(salon=salon1, name='Brushing & Lissage', defaults={'description': 'Brushing professionnel', 'price': 4500, 'duration': 45, 'category': 'hair'})
        Service.objects.get_or_create(salon=salon1, name='Coloration Bio', defaults={'description': 'Coloration sans ammoniaque', 'price': 18000, 'duration': 75, 'category': 'hair'})

        Service.objects.get_or_create(salon=salon2, name='Coupe & Coiffure Homme', defaults={'description': 'Coupe moderne homme', 'price': 3000, 'duration': 30, 'category': 'hair'})
        Service.objects.get_or_create(salon=salon2, name='Locks & Dreadlocks', defaults={'description': 'Création et entretien locks', 'price': 20000, 'duration': 120, 'category': 'hair'})
        Service.objects.get_or_create(salon=salon2, name='Brushing / Lissage', defaults={'description': 'Brushing professionnel', 'price': 4500, 'duration': 45, 'category': 'hair'})
        Service.objects.get_or_create(salon=salon2, name='Makeup Pro', defaults={'description': 'Maquillage événementiel', 'price': 12000, 'duration': 60, 'category': 'makeup'})
        Service.objects.get_or_create(salon=salon2, name='Soin Visage', defaults={'description': 'Soin hydratant africain', 'price': 8000, 'duration': 45, 'category': 'skincare'})

        Service.objects.get_or_create(salon=salon3, name='Nattes (Cornrows)', defaults={'description': 'Nattes artistiques', 'price': 8000, 'duration': 60, 'category': 'hair'})
        Service.objects.get_or_create(salon=salon3, name='Tissage Crochet', defaults={'description': 'Tissage à crochet rapide', 'price': 14000, 'duration': 120, 'category': 'hair'})
        Service.objects.get_or_create(salon=salon3, name='Coupe Afro Créative', defaults={'description': 'Coupe afro personnalisée', 'price': 6000, 'duration': 45, 'category': 'hair'})
        Service.objects.get_or_create(salon=salon3, name='Pose de Clips', defaults={'description': 'Pose de extensions clips', 'price': 10000, 'duration': 60, 'category': 'hair'})
        Service.objects.get_or_create(salon=salon3, name='Henné Naturel', defaults={'description': 'Coloration naturelle au henné', 'price': 7000, 'duration': 45, 'category': 'hair'})

        Service.objects.get_or_create(salon=salon2, name='Manucure', defaults={'description': 'Manucure classique ou gel', 'price': 5000, 'duration': 45, 'category': 'nails'})
        Service.objects.get_or_create(salon=salon2, name='Pédicure', defaults={'description': 'Pédicure relaxante', 'price': 6000, 'duration': 60, 'category': 'nails'})
        Service.objects.get_or_create(salon=salon2, name='Ongles Acryliques', defaults={'description': 'Pose complète acrylique', 'price': 12000, 'duration': 90, 'category': 'nails'})
        Service.objects.get_or_create(salon=salon2, name='Piercing Oreille', defaults={'description': 'Perçage oreille stérile', 'price': 3000, 'duration': 15, 'category': 'piercing'})
        Service.objects.get_or_create(salon=salon2, name='Piercing Nez / Nombril', defaults={'description': 'Perçage avec bijou inclus', 'price': 8000, 'duration': 20, 'category': 'piercing'})
        Service.objects.get_or_create(salon=salon2, name='Tatouage Temporaire', defaults={'description': 'Tatouage temporaire henné', 'price': 5000, 'duration': 30, 'category': 'makeup'})

        # Salon publications (portfolio for salons)
        SalonPublication.objects.get_or_create(salon=salon1, title='Tresses de Noël', defaults={'description': 'Coiffure festive pour les fêtes', 'media_url': 'https://images.unsplash.com/photo-1605497788044-5a32c70786f3?w=800', 'media_type': 'image'})
        SalonPublication.objects.get_or_create(salon=salon1, title='Derrière les coulisses', defaults={'description': 'Notre salon en pleine action', 'media_url': 'https://images.unsplash.com/photo-1595476108010-b4d1f102b1b1?w=800', 'media_type': 'image'})
        SalonPublication.objects.get_or_create(salon=salon1, title='Makeup & Glow', defaults={'description': 'Maquillage professionnel pour soirées', 'media_url': 'https://images.unsplash.com/photo-1522337360788-8b13dee7a37e?w=800', 'media_type': 'image'})

        SalonPublication.objects.get_or_create(salon=salon2, title='Nails Art Douala', defaults={'description': 'Designs ongles incroyables', 'media_url': 'https://images.unsplash.com/photo-1562322140-8baeececf3df?w=800', 'media_type': 'image'})
        SalonPublication.objects.get_or_create(salon=salon2, title='Piercing Party', defaults={'description': 'Session piercing privée', 'media_url': 'https://images.unsplash.com/photo-1594300576998-224a1856f9e5?w=800', 'media_type': 'image'})

        SalonPublication.objects.get_or_create(salon=salon3, title='Locks Session', defaults={'description': 'Transformation locks complète', 'media_url': 'https://images.unsplash.com/photo-1633681926022-84c23e8cb2d6?w=800', 'media_type': 'image'})
        SalonPublication.objects.get_or_create(salon=salon3, title='Afro Cut du Mois', defaults={'description': 'Coupe afro masculine stylée', 'media_url': 'https://images.unsplash.com/photo-1503951914875-452162b0f3f1?w=800', 'media_type': 'image'})

        # Hairstyle publications (posted by hairdressers, linking to their salon)
        HairstylePublication.objects.get_or_create(hairdresser=hd1, title='Box Braids Elegance', defaults={'description': 'Modèle de tresses bohème chic', 'media_url': 'https://images.unsplash.com/photo-1560869713-7d0a29430803?w=800', 'salon': salon1})
        HairstylePublication.objects.get_or_create(hairdresser=hd1, title='Tissage Ghana', defaults={'description': 'Tissage invisible', 'media_url': 'https://images.unsplash.com/photo-1605497788044-5a32c70786f3?w=800', 'salon': salon1})

        HairstylePublication.objects.get_or_create(hairdresser=hd2, title='Locks Modernes', defaults={'description': 'Locks courts et stylés', 'media_url': 'https://images.unsplash.com/photo-1633681926022-84c23e8cb2d6?w=800', 'salon': salon2})
        HairstylePublication.objects.get_or_create(hairdresser=hd2, title='Coupe Mixte Fade', defaults={'description': 'Fade avec design', 'media_url': 'https://images.unsplash.com/photo-1503951914875-452162b0f3f1?w=800', 'salon': salon2})

        HairstylePublication.objects.get_or_create(hairdresser=hd3, title='Nattes Colées', defaults={'description': 'Nattes serrées artistiques', 'media_url': 'https://images.unsplash.com/photo-1560066984-138dadb4c035?w=800', 'salon': salon3})
        HairstylePublication.objects.get_or_create(hairdresser=hd3, title='Fulani Braids', defaults={'description': 'Braids traditionnelles Fulani', 'media_url': 'https://images.unsplash.com/photo-1595476108010-b4d1f102b1b1?w=800', 'salon': salon3})

        HairstylePublication.objects.get_or_create(hairdresser=hd4, title='Nails Art Cameroun', defaults={'description': 'Designs avec les couleurs du Cameroun', 'media_url': 'https://images.unsplash.com/photo-1562322140-8baeececf3df?w=800', 'salon': salon2})
        HairstylePublication.objects.get_or_create(hairdresser=hd5, title='Piercing Look', defaults={'description': 'Combinaison piercing & makeup', 'media_url': 'https://images.unsplash.com/photo-1594300576998-224a1856f9e5?w=800', 'salon': salon2})

        Review.objects.get_or_create(salon=salon1, client=client1, rating=5, defaults={'comment': 'Meilleur salon de tresses à Douala!', 'created_at': timezone.now() - timedelta(days=2)})
        Review.objects.get_or_create(salon=salon1, client=client2, rating=4, defaults={'comment': 'Très professionnel, je recommande.', 'created_at': timezone.now() - timedelta(days=1)})
        Review.objects.get_or_create(salon=salon2, client=client3, rating=5, defaults={'comment': 'Le meilleur salon de Yaoundé pour les ongles et le piercing!', 'created_at': timezone.now() - timedelta(hours=12)})
        Review.objects.get_or_create(salon=salon2, client=client1, rating=5, defaults={'comment': 'Locks parfaits, merci Rachel!', 'created_at': timezone.now() - timedelta(hours=5)})
        Review.objects.get_or_create(salon=salon3, client=client2, rating=4, defaults={'comment': 'Salon propre, résultats au top.', 'created_at': timezone.now() - timedelta(days=3)})
        Review.objects.get_or_create(salon=salon3, client=client3, rating=5, defaults={'comment': 'Nattes incroyables pour mon mariage!', 'created_at': timezone.now() - timedelta(days=1)})

        Availability.objects.get_or_create(hairdresser=hd1, day_of_week=1, start_time=time(8, 0), end_time=time(18, 0))
        Availability.objects.get_or_create(hairdresser=hd1, day_of_week=2, start_time=time(8, 0), end_time=time(18, 0))
        Availability.objects.get_or_create(hairdresser=hd1, day_of_week=3, start_time=time(8, 0), end_time=time(18, 0))
        Availability.objects.get_or_create(hairdresser=hd1, day_of_week=5, start_time=time(9, 0), end_time=time(19, 0))

        Availability.objects.get_or_create(hairdresser=hd2, day_of_week=1, start_time=time(9, 0), end_time=time(19, 0))
        Availability.objects.get_or_create(hairdresser=hd2, day_of_week=3, start_time=time(9, 0), end_time=time(19, 0))
        Availability.objects.get_or_create(hairdresser=hd2, day_of_week=4, start_time=time(9, 0), end_time=time(19, 0))
        Availability.objects.get_or_create(hairdresser=hd2, day_of_week=5, start_time=time(9, 0), end_time=time(19, 0))

        Availability.objects.get_or_create(hairdresser=hd3, day_of_week=2, start_time=time(8, 0), end_time=time(17, 0))
        Availability.objects.get_or_create(hairdresser=hd3, day_of_week=4, start_time=time(8, 0), end_time=time(17, 0))
        Availability.objects.get_or_create(hairdresser=hd3, day_of_week=6, start_time=time(9, 0), end_time=time(16, 0))

        Availability.objects.get_or_create(hairdresser=hd4, day_of_week=1, start_time=time(9, 0), end_time=time(18, 0))
        Availability.objects.get_or_create(hairdresser=hd4, day_of_week=2, start_time=time(9, 0), end_time=time(18, 0))
        Availability.objects.get_or_create(hairdresser=hd4, day_of_week=4, start_time=time(9, 0), end_time=time(18, 0))

        Availability.objects.get_or_create(hairdresser=hd5, day_of_week=1, start_time=time(10, 0), end_time=time(19, 0))
        Availability.objects.get_or_create(hairdresser=hd5, day_of_week=3, start_time=time(10, 0), end_time=time(19, 0))
        Availability.objects.get_or_create(hairdresser=hd5, day_of_week=5, start_time=time(10, 0), end_time=time(19, 0))
        Availability.objects.get_or_create(hairdresser=hd5, day_of_week=6, start_time=time(10, 0), end_time=time(17, 0))

        chat1, _ = Chat.objects.get_or_create(client=client1, hairdresser=hd1, salon=salon1)
        chat2, _ = Chat.objects.get_or_create(client=client2, hairdresser=hd2, salon=salon2)
        chat3, _ = Chat.objects.get_or_create(client=client1, hairdresser=hd3, salon=salon3)
        chat4, _ = Chat.objects.get_or_create(client=client3, hairdresser=hd4, salon=salon2)

        Message.objects.get_or_create(chat=chat1, sender=client1, defaults={'content': 'Bonjour Grace, je voudrais réserver pour des tresses.', 'read': True})
        Message.objects.get_or_create(chat=chat1, sender=hd1, defaults={'content': 'Bonjour Amira! Oui, quand ça vous arrange?', 'read': True})
        Message.objects.get_or_create(chat=chat1, sender=client1, defaults={'content': 'Mardi prochain à 10h svp.', 'read': False})

        Message.objects.get_or_create(chat=chat2, sender=client2, defaults={'content': 'Nadia, peux-tu me refaire les locks?', 'read': True})
        Message.objects.get_or_create(chat=chat2, sender=hd2, defaults={'content': 'Oui Diane, vendredi?', 'read': True})
        Message.objects.get_or_create(chat=chat2, sender=client2, defaults={'content': 'Parfait!', 'read': True})

        Message.objects.get_or_create(chat=chat3, sender=hd3, defaults={'content': 'Fatima, tes nattes étaient magnifiques!', 'read': True})
        Message.objects.get_or_create(chat=chat3, sender=client1, defaults={'content': 'Merci Solange!', 'read': False})

        Message.objects.get_or_create(chat=chat4, sender=client3, defaults={'content': 'Rachel, quel est le prix pour des ongles acryliques?', 'read': True})
        Message.objects.get_or_create(chat=chat4, sender=hd4, defaults={'content': 'Bonjour Fatima, c\'est 12 000 FCFA.', 'read': True})
        Message.objects.get_or_create(chat=chat4, sender=client3, defaults={'content': 'D\'accord, je réserve pour samedi.', 'read': False})

        today = date.today()
        Appointment.objects.get_or_create(
            client=client1,
            hairdresser=hd1,
            salon=salon1,
            service=Service.objects.filter(salon=salon1, name='Tresses (Box Braids)').first(),
            date=today + timedelta(days=3),
            time=time(10, 0),
            defaults={'status': 'confirmed'}
        )
        Appointment.objects.get_or_create(
            client=client2,
            hairdresser=hd2,
            salon=salon2,
            service=Service.objects.filter(salon=salon2, name='Locks & Dreadlocks').first(),
            date=today + timedelta(days=5),
            time=time(14, 0),
            defaults={'status': 'pending'}
        )
        Appointment.objects.get_or_create(
            client=client3,
            hairdresser=hd4,
            salon=salon2,
            service=Service.objects.filter(salon=salon2, name='Ongles Acryliques').first(),
            date=today + timedelta(days=2),
            time=time(11, 0),
            defaults={'status': 'pending'}
        )
        Appointment.objects.get_or_create(
            client=client1,
            hairdresser=hd3,
            salon=salon3,
            service=Service.objects.filter(salon=salon3, name='Nattes (Cornrows)').first(),
            date=today - timedelta(days=2),
            time=time(11, 0),
            defaults={'status': 'completed'}
        )

        self.stdout.write(self.style.SUCCESS('Database population complete.'))
