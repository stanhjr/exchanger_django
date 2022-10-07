import uuid
from decimal import Decimal

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from datetime import datetime

from exchanger_django.settings import HOST


class CustomUser(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(blank=True, unique=True)
    last_action = models.DateTimeField(default=datetime.now())
    is_confirmed = models.BooleanField(default=False)
    cents = models.BigIntegerField(default=0)

    @property
    def wallet(self):
        return Decimal(self.cents / 100)

    @property
    def referral_url(self):
        return f"{HOST}?referral={self.id}"

    @classmethod
    def get_inviter(cls, referral_token=None):
        return cls.objects.filter(id=referral_token).first()


class ReferralRelationship(models.Model):
    # who invite
    inviter = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='inviter',
        verbose_name="inviter",
        on_delete=models.CASCADE,
    )
    # who connected
    invited = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='invited',
        verbose_name="invited",
        on_delete=models.CASCADE,
    )
    # referral code
    refer_token = models.ForeignKey(
        "ReferralCode",
        verbose_name="referral_code",
        on_delete=models.CASCADE,
    )

    def __str__(self) -> str:
        return f"{self.inviter}_{self.invited}"


class ReferralCode(models.Model):
    token = models.CharField(unique=True, max_length=150)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, verbose_name="code_master", on_delete=models.CASCADE
    )

    def __str__(self) -> str:
        return f"{self.user}_{self.token}"
