from django.contrib import admin

from important_info.models import Action
from important_info.models import Feedback
from important_info.models import Faq


admin.site.register(Action)
admin.site.register(Faq)
admin.site.register(Feedback)
