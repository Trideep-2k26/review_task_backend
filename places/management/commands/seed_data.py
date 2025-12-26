import random
from django.core.management.base import BaseCommand
from faker import Faker
from users.models import User
from places.models import Place, Review


class Command(BaseCommand):
    help = 'Seeds the database with fake data'

    def add_arguments(self, parser):
        parser.add_argument('--users', type=int, default=20, help='Number of users to create')
        parser.add_argument('--places', type=int, default=30, help='Number of places to create')
        parser.add_argument('--reviews', type=int, default=100, help='Number of reviews to create')

    def handle(self, *args, **options):
        fake = Faker()
        num_users = options['users']
        num_places = options['places']
        num_reviews = options['reviews']

        self.stdout.write('Seeding database...')

        users = []
        for i in range(num_users):
            phone = f'+1{fake.msisdn()[3:13]}'
            user, created = User.objects.get_or_create(
                phone_number=phone,
                defaults={'name': fake.name()}
            )
            if created:
                users.append(user)
        self.stdout.write(f'Created {len(users)} users')

        place_types = ['Restaurant', 'Clinic', 'Shop', 'Cafe', 'Hospital', 'Gym', 'Salon', 'Hotel']
        places = []
        for i in range(num_places):
            place_type = random.choice(place_types)
            name = f"{fake.company()} {place_type}"
            address = fake.address().replace('\n', ', ')
            place, created = Place.objects.get_or_create(
                name=name,
                address=address
            )
            if created:
                places.append(place)
        self.stdout.write(f'Created {len(places)} places')

        if not users:
            users = list(User.objects.all()[:num_users])
        if not places:
            places = list(Place.objects.all()[:num_places])

        reviews_created = 0
        attempts = 0
        max_attempts = num_reviews * 3

        while reviews_created < num_reviews and attempts < max_attempts:
            attempts += 1
            user = random.choice(users)
            place = random.choice(places)

            if Review.objects.filter(user=user, place=place).exists():
                continue

            Review.objects.create(
                user=user,
                place=place,
                rating=random.randint(1, 5),
                text=fake.paragraph(nb_sentences=random.randint(2, 5))
            )
            reviews_created += 1

        self.stdout.write(f'Created {reviews_created} reviews')
        self.stdout.write(self.style.SUCCESS('Database seeding completed successfully'))
