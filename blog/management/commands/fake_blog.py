import random

from faker import Faker

from django.core.management.base import BaseCommand
from blog.models import Tag, Post

faker = Faker()


class Command(BaseCommand):
    help = "genetating fake data"

    def handle(self, *args, **options):
        self.stdout.write("Creating fake data")
        Tag.objects.create(name='book')
        Tag.objects.create(name='alice')
        Tag.objects.create(name='frontend')
        tags = Tag.objects.all()
        for _ in range(50):
            post = Post()
            post.set_current_language('en')
            post.title = faker.text()[:10]
            post.text = faker.text()
            post.minutes_for_reading = faker.random_int(1, 10)
            post.save()
            post.tags.add(random.choice(tags))
            post.save()
