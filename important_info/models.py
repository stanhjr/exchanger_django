from django.db import models

from exchanger_django.settings import HOST


class Faq(models.Model):
    question = models.CharField(max_length=90)
    answer = models.TextField(max_length=1000)

    class Meta:
        verbose_name = 'Faq settings'
        verbose_name_plural = 'Faq settings'
        ordering = ['question', ]


class Feedback(models.Model):
    name = models.CharField(max_length=200)
    logo_image = models.ImageField(null=True, upload_to="logo_images/")
    link = models.CharField(max_length=200)

    @property
    def image_url(self):
        if self.logo_image:
            return f"{HOST}{self.logo_image.url}"

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Feedback'
        verbose_name_plural = 'Feedback'


class Action(models.Model):
    title = models.CharField(max_length=200)
    text = models.TextField()
    image = models.ImageField(null=True, upload_to="actions_images/")

    @property
    def image_url(self):
        if self.image:
            return f"{HOST}{self.image.url}"

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Action'
        verbose_name_plural = 'Action'
