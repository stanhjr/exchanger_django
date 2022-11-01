from rest_framework import generics
from rest_framework.views import APIView

from important_info.models import Faq, GetInTouchModel
from important_info.models import Action
from important_info.models import FeedbackMonitoring
from important_info.models import FeedbackSites
from important_info.serializers import FaqSerializer, GetInTouchSerializer
from important_info.serializers import FeedbackSitesSerializer
from important_info.serializers import FeedbackMonitoringSerializer
from important_info.serializers import ActionSerializer


class FaqListView(generics.ListAPIView):
    queryset = Faq.objects.all()
    serializer_class = FaqSerializer


class FeedbackMonitoringListView(generics.ListAPIView):
    queryset = FeedbackMonitoring.objects.all()
    serializer_class = FeedbackMonitoringSerializer


class FeedbackSitesListView(generics.ListAPIView):
    queryset = FeedbackSites.objects.all()
    serializer_class = FeedbackSitesSerializer


class ActionListView(generics.ListAPIView):
    queryset = Action.objects.all()
    serializer_class = ActionSerializer


class GetInTouchView(generics.CreateAPIView):
    queryset = GetInTouchModel.objects.all()
    serializer_class = GetInTouchSerializer


