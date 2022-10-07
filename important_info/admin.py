from django.contrib import admin

from important_info.models import Faq
from important_info.models import Feedback

admin.site.register(Faq)
admin.site.register(Feedback)
