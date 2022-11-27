from django.db import models
from django.utils import timezone as tz
from django.utils.translation import gettext as _
from parler.models import TranslatedFields, TranslatableModel
from slugify import slugify
from parler.utils.context import switch_language


class Tag(TranslatableModel):
    translations = TranslatedFields(name=models.CharField(max_length=255), )

    class Meta:
        verbose_name_plural = 'Категории (тэги)'

    def __str__(self):
        return self.name


class Post(TranslatableModel):
    translations = TranslatedFields(
        title=models.CharField(_("Title"), max_length=200, unique=True),
        text=models.TextField(_("Content"), blank=True)
    )
    created = models.DateTimeField(auto_now_add=True, verbose_name='Создано')
    slug = models.SlugField(unique=True, max_length=100, blank=True)
    tags = models.ManyToManyField(Tag, related_name='posts', verbose_name='Категория (тэг)')
    minutes_for_reading = models.IntegerField(default=1, verbose_name='Минут для чтения')
    image = models.ImageField(upload_to='posts_images/%Y/%m/%d/', null=True, max_length=255)
    recommendation = models.ManyToManyField('self', related_name='post_recommendation', null=True, blank=True, verbose_name='Рекомендации')

    class Meta:
        verbose_name_plural = 'Посты'
        ordering = ['created']

    @property
    def next_slug(self):
        next_ogj = Post.objects.filter(pk__gt=self.pk).order_by('pk').first()
        if next_ogj:
            return next_ogj.slug

    @property
    def previous_slug(self):
        next_ogj = Post.objects.filter(pk__lt=self.pk).order_by('pk').first()
        if next_ogj:
            return next_ogj.slug

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs) -> None:
        if Post.objects.filter(pk=self.pk):
            self.updated_at = tz.now()
        with switch_language(self, 'en'):
            self.slug = slugify(self.title)
        return super().save(*args, **kwargs)
