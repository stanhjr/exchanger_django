from django.db import models
from django.utils import timezone as tz
from slugify import slugify


class Tag(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Post(models.Model):
    title = models.CharField(max_length=200)
    text = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    slug = models.SlugField(unique=True, max_length=100, blank=True)
    tags = models.ManyToManyField(Tag, related_name='posts')

    class Meta:
        ordering = ['created']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs) -> None:
        if Post.objects.filter(pk=self.pk):
            self.updated_at = tz.now()
        self.slug = slugify(self.title)
        return super().save(*args, **kwargs)
