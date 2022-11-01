from parler_rest.fields import TranslatedFieldsField
from rest_framework import serializers

from blog.mixins import TranslatedSerializerMixin
from important_info.models import Faq
from important_info.models import FeedbackMonitoring
from important_info.models import FeedbackSites
from important_info.models import Action


class FaqSerializer(TranslatedSerializerMixin, serializers.ModelSerializer):
    translations = TranslatedFieldsField(shared_model=Faq)

    class Meta:
        model = Faq
        fields = ['translations', ]


class FeedbackSitesSerializer(TranslatedSerializerMixin, serializers.ModelSerializer):
    translations = TranslatedFieldsField(shared_model=FeedbackSites)

    class Meta:
        model = FeedbackMonitoring
        fields = ['translations', 'link', 'logo_image']


class FeedbackMonitoringSerializer(TranslatedSerializerMixin, serializers.ModelSerializer):
    translations = TranslatedFieldsField(shared_model=FeedbackMonitoring)

    class Meta:
        model = FeedbackMonitoring
        fields = ['translations', 'link', 'logo_image']


class ActionSerializer(TranslatedSerializerMixin, serializers.ModelSerializer):
    translations = TranslatedFieldsField(shared_model=Action)

    class Meta:
        model = Action
        fields = ['translations', 'image', 'created_at', 'new']
