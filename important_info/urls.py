from django.urls import path
from rest_framework.routers import DefaultRouter

from important_info.views import ActionList
from important_info.views import FeedbackList
from important_info.views import FaqList


router = DefaultRouter()

urlpatterns = router.urls
urlpatterns += [
    path('faq/', FaqList.as_view(), name='faq_list'),
    path('feedback/', FeedbackList.as_view(), name='feedback_list'),
    path('actions/', ActionList.as_view(), name='actions_list'),
]
