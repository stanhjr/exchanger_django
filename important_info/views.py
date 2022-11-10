from rest_framework import generics

from important_info.models import (
    Faq,
    GetInTouchModel,
    Action,
    FeedbackMonitoring,
    FeedbackSites
)

from important_info.serializers import (
    FaqSerializer,
    GetInTouchSerializer,
    FeedbackSitesSerializer,
    FeedbackMonitoringSerializer,
    ActionSerializer
)


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
