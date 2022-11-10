from django.conf import settings
from django.db import models
from parler.models import TranslatedFields, TranslatableModel


class Faq(TranslatableModel):
    translations = TranslatedFields(
        question=models.CharField(max_length=90),
        answer=models.TextField(max_length=1000)
    )

    class Meta:
        verbose_name = 'Faq settings'
        verbose_name_plural = 'Faq settings'


class FeedbackMonitoring(TranslatableModel):
    translations = TranslatedFields(
        name=models.CharField(max_length=200),
    )

    logo_image = models.ImageField(null=True, upload_to="logo_images/")
    link = models.CharField(max_length=200)

    @property
    def image_url(self):
        if self.logo_image:
            return f"{settings.HOST}{self.logo_image.url}"

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'FeedbackMonitoring'
        verbose_name_plural = 'FeedbackMonitoring'


class FeedbackSites(TranslatableModel):
    translations = TranslatedFields(
        name=models.CharField(max_length=200),
    )

    logo_image = models.ImageField(null=True, upload_to="logo_images/")
    link = models.CharField(max_length=200)

    @property
    def image_url(self):
        if self.logo_image:
            return f"{settings.HOST}{self.logo_image.url}"

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'FeedbackSites'
        verbose_name_plural = 'FeedbackSites'


class Action(TranslatableModel):
    translations = TranslatedFields(
        title=models.CharField(max_length=200),
        text=models.TextField()
    )
    created_at = models.DateField(auto_now_add=True)
    new = models.BooleanField(default=True)

    image = models.ImageField(null=True, upload_to="actions_images/")

    @property
    def image_url(self):
        if self.image:
            return f"{settings.HOST}{self.image.url}"

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Action'
        verbose_name_plural = 'Action'


class GetInTouchModel(models.Model):
    email = models.EmailField()
    title = models.CharField(max_length=100)
    text = models.TextField(max_length=1024)
    telegram = models.CharField(max_length=100)
    created_at = models.DateField(auto_now_add=True)
    viewed = models.BooleanField(default=False)

    def __str__(self):
        return self.email

    class Meta:
        verbose_name = 'GetInTouch'
        verbose_name_plural = 'GetInTouch'
        ordering = ['-created_at', 'viewed']
