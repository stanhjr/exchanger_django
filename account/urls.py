from django.urls import path
from rest_framework.routers import DefaultRouter

from rest_framework_simplejwt.views import TokenRefreshView

from account.views import SignUpApi, UserReferralOperationsView
from account.views import UserRefAnalyticsView
from account.views import UserViewSet
from account.views import ResetPassword
from account.views import SignUpConfirm
from account.views import LoginView
from account.views import UserBonusPreCalculateView

router = DefaultRouter()

urlpatterns = router.urls
urlpatterns += [
    path('sign_up/', SignUpApi.as_view(), name='sign_up'),
    path('login/',  LoginView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('user_info/', UserViewSet.as_view({'get': 'list'}), name='user_info'),
    path('account-activate/', SignUpConfirm.as_view(), name='account-activate'),
    path('reset-password/', ResetPassword.as_view(), name='reset-password'),
    path('get-bonus-calculate/', UserBonusPreCalculateView.as_view(), name='get-bonus_calculate'),
    path('referral-statistics/', UserRefAnalyticsView.as_view({'get': 'list'}), name='referral-statistics'),
    path('referral-operations-list/', UserReferralOperationsView.as_view({'get': 'list'}), name='referral-statistics'),
]
