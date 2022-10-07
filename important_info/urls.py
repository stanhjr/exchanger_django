from django.urls import path
from rest_framework.routers import DefaultRouter

from important_info.views import FaqList
from important_info.views import FeedbackList


router = DefaultRouter()

urlpatterns = router.urls
urlpatterns += [
    path('faq/', FaqList.as_view(), name='faq_list'),
    path('feedback/', FeedbackList.as_view(), name='feedback_list'),
]
