from django.contrib import admin
from parler.admin import TranslatableAdmin

from blog.models import Post
from blog.models import Tag


class TagAdmin(TranslatableAdmin):
    fieldsets = (
        (None, {
            'fields': ('name',),
        }),
    )


class PostAdmin(TranslatableAdmin):
    list_display = ('title', 'text')
    fieldsets = (
        (None, {
            'fields': ('title', 'text', 'slug', 'tags', 'minutes_for_reading', 'image'),
        }),
    )


admin.site.register(Tag, TagAdmin)
admin.site.register(Post, PostAdmin)
