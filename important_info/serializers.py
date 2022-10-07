from rest_framework import serializers

from important_info.models import Faq
from important_info.models import Feedback
from important_info.models import Action


class FaqSerializer(serializers.ModelSerializer):
    class Meta:
        model = Faq
        fields = ['question', 'answer']


class FeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = ['link', 'image_url']


class ActionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = ['link', 'image_url']

