from rest_framework import generics

from important_info.models import Faq
from important_info.models import Feedback
from important_info.serializers import FaqSerializer
from important_info.serializers import FeedbackSerializer


class FaqList(generics.ListAPIView):
    queryset = Faq.objects.all()
    serializer_class = FaqSerializer


class FeedbackList(generics.ListAPIView):
    queryset = Feedback.objects.all()
    serializer_class = FeedbackSerializer
