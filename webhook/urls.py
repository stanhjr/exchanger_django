from rest_framework.routers import DefaultRouter
from django.urls import path

from webhook.views import WhiteBitWebHook
router = DefaultRouter()

urlpatterns = router.urls
urlpatterns += [
    path('/', WhiteBitWebHook.as_view(), name='web_hook'),

]