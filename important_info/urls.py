from django.urls import path
from rest_framework.routers import DefaultRouter

from important_info.views import ActionListView
from important_info.views import FeedbackSitesListView
from important_info.views import FeedbackMonitoringListView
from important_info.views import FaqListView
from important_info.views import GetInTouchView


router = DefaultRouter()

urlpatterns = router.urls
urlpatterns += [
    path('faq/', FaqListView.as_view(), name='faq_list'),
    path('feedback-monitoring/', FeedbackMonitoringListView.as_view(), name='feedback_monitoring_list'),
    path('feedback-sites/', FeedbackSitesListView.as_view(), name='feedback_sites_list'),
    path('actions/', ActionListView.as_view(), name='actions_list'),
    path('get-in-touch/', GetInTouchView.as_view(), name='get_in_touch_me')
]
