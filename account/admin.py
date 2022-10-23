from django.contrib import admin

from account.models import CustomUser
from account.models import ReferralRelationship

admin.site.register(CustomUser)
admin.site.register(ReferralRelationship)


