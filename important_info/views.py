from rest_framework import generics

from important_info.models import Faq
from important_info.models import Action
from important_info.models import FeedbackMonitoring
from important_info.models import FeedbackSites
from important_info.serializers import FaqSerializer
from important_info.serializers import FeedbackSitesSerializer
from important_info.serializers import FeedbackMonitoringSerializer
from important_info.serializers import ActionSerializer


class FaqList(generics.ListAPIView):
    queryset = Faq.objects.all()
    serializer_class = FaqSerializer


class FeedbackMonitoringList(generics.ListAPIView):
    queryset = FeedbackMonitoring.objects.all()
    serializer_class = FeedbackMonitoringSerializer


class FeedbackSitesList(generics.ListAPIView):
    queryset = FeedbackSites.objects.all()
    serializer_class = FeedbackSitesSerializer


class ActionList(generics.ListAPIView):
    queryset = Action.objects.all()
    serializer_class = ActionSerializer
