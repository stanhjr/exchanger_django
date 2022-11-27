from django.conf import settings
from django.db import models
from parler.models import TranslatedFields, TranslatableModel


class Faq(TranslatableModel):
    translations = TranslatedFields(
        question=models.CharField(max_length=90),
        answer=models.TextField(max_length=1000)
    )

    class Meta:
        verbose_name = 'FAQ настройки'
        verbose_name_plural = 'FAQ настройки'


class FeedbackMonitoring(TranslatableModel):
    translations = TranslatedFields(
        name=models.CharField(max_length=200),
    )

    logo_image = models.ImageField(null=True, upload_to="logo_images/", verbose_name='Логотип')
    link = models.CharField(max_length=200, verbose_name='Ссылка')

    @property
    def image_url(self):
        if self.logo_image:
            return f"{settings.HOST}{self.logo_image.url}"

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Отзывы Monitoring'
        verbose_name_plural = 'Отзывы FeedbackMonitoring'


class FeedbackSites(TranslatableModel):
    translations = TranslatedFields(
        name=models.CharField(max_length=200),
    )

    logo_image = models.ImageField(null=True, upload_to="logo_images/", verbose_name='Логотип')
    link = models.CharField(max_length=200, verbose_name='Ссылка')

    @property
    def image_url(self):
        if self.logo_image:
            return f"{settings.HOST}{self.logo_image.url}"

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Отзывы сайтов'
        verbose_name_plural = 'Отзывы сайтов'


class Action(TranslatableModel):
    translations = TranslatedFields(
        title=models.CharField(max_length=200),
        text=models.TextField()
    )
    created_at = models.DateField(auto_now_add=True, verbose_name='Создано')
    new = models.BooleanField(default=True)

    image = models.ImageField(null=True, upload_to="actions_images/")

    @property
    def image_url(self):
        if self.image:
            return f"{settings.HOST}{self.image.url}"

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Акции'
        verbose_name_plural = 'Акции'


class GetInTouchModel(models.Model):
    email = models.EmailField()
    title = models.CharField(max_length=100)
    text = models.TextField(max_length=1024)
    telegram = models.CharField(max_length=100)
    created_at = models.DateField(auto_now_add=True, verbose_name='Создано')
    viewed = models.BooleanField(default=False, verbose_name='Просмотрено')

    def __str__(self):
        return self.email

    class Meta:
        verbose_name = 'Связаться с нами (уведомления от юзеров)'
        verbose_name_plural = 'Связаться с нами (уведомления от юзеров)'
        ordering = ['-created_at', 'viewed']
