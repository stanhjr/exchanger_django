from django.urls import path
from rest_framework.routers import DefaultRouter

from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.views import TokenRefreshView

from account.views import SignUpApi

router = DefaultRouter()
# router.register(r'posts', PostViewSet, basename='posts')

urlpatterns = router.urls
urlpatterns += [
    path('sign_up/', SignUpApi.as_view(), name='sign_up'),
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
