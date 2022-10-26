from parler_rest.fields import TranslatedFieldsField
from rest_framework import serializers

from blog.mixins import TranslatedSerializerMixin
from blog.models import Post
from blog.models import Tag


class TagSerializer(TranslatedSerializerMixin, serializers.ModelSerializer):
    translations = TranslatedFieldsField(shared_model=Tag)

    class Meta:
        model = Tag
        fields = ['translations', ]


class PostSerializer(TranslatedSerializerMixin, serializers.ModelSerializer):
    tags = TagSerializer(many=True)
    translations = TranslatedFieldsField(shared_model=Post)

    class Meta:
        model = Post
        fields = ['slug', 'translations', 'created', 'tags', 'minutes_for_reading', 'image']
