from django.contrib import admin
from parler.admin import TranslatableAdmin

from important_info.models import Action
from important_info.models import FeedbackMonitoring
from important_info.models import FeedbackSites
from important_info.models import Faq
from important_info.models import GetInTouchModel


class ActionAdmin(TranslatableAdmin):
    list_display = ('title', 'text')
    fieldsets = (
        (None, {
            'fields': ('title', 'text', 'image'),
        }),
    )


class FeedbackAdmin(TranslatableAdmin):
    list_display = ('name',)
    fieldsets = (
        (None, {
            'fields': ('name', 'logo_image', 'link'),
        }),
    )


class FaqAdmin(TranslatableAdmin):
    list_display = ('question',)
    fieldsets = (
        (None, {
            'fields': ('question', 'answer',),
        }),
    )


class GetInTouchAdmin(admin.ModelAdmin):
    list_display = ('email', 'viewed', 'created_at')
    list_filter = ('created_at', 'viewed')


admin.site.register(Action, ActionAdmin)
admin.site.register(Faq, FaqAdmin)
admin.site.register(FeedbackMonitoring, FeedbackAdmin)
admin.site.register(FeedbackSites, FeedbackAdmin)
admin.site.register(GetInTouchModel, GetInTouchAdmin)
