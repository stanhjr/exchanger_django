import uuid
from decimal import Decimal


from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from django.conf import settings
from exchanger_django.settings import HOST


class CustomUser(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(blank=True, unique=True)
    inviter_token = models.CharField(max_length=150, null=True, blank=True)
    last_action = models.DateTimeField(default=timezone.now)
    is_confirmed = models.BooleanField(default=False)
    cents = models.BigIntegerField(default=0)
    verify_code = models.CharField(default='', max_length=100, null=True, blank=True)
    reset_password_code = models.CharField(default='', max_length=100, null=True, blank=True)

    @property
    def wallet(self):
        return Decimal(self.cents / 100)

    @property
    def referral_url(self):
        return f"{HOST}/{self.id}"

    @classmethod
    def get_inviter(cls, referral_token=None):
        return cls.objects.filter(id=referral_token).first()

    def save(self, *args, **kwargs):
        if not self.username:
            self.username = self.email
        return super().save(*args, **kwargs)


class ReferralRelationship(models.Model):
    inviter = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='inviter',
        verbose_name="inviter",
        on_delete=models.CASCADE,
    )
    invited = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='invited',
        verbose_name="invited",
        on_delete=models.CASCADE,
    )

    def __str__(self) -> str:
        return f"{self.inviter}_{self.invited}"


@receiver(post_save, sender=CustomUser)
def post_save_function(sender, instance, **kwargs):
    try:
        inviter = CustomUser.objects.filter(id=instance.inviter_token).first()
        if inviter:
            referral = ReferralRelationship.objects.create(inviter=inviter,
                                                           invited=instance)
            referral.save()
    except ValidationError as e:
        print(e)

