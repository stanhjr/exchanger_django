from rest_framework import generics

from important_info.models import Faq
from important_info.models import Action
from important_info.models import Feedback
from important_info.serializers import FaqSerializer
from important_info.serializers import FeedbackSerializer
from important_info.serializers import ActionSerializer


class FaqList(generics.ListAPIView):
    queryset = Faq.objects.all()
    serializer_class = FaqSerializer


class FeedbackList(generics.ListAPIView):
    queryset = Feedback.objects.all()
    serializer_class = FeedbackSerializer


class ActionList(generics.ListAPIView):
    queryset = Action.objects.all()
    serializer_class = ActionSerializer
