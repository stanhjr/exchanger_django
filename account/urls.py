from django.urls import path
from rest_framework.routers import DefaultRouter

from account.views import (
    SignUpApi,
    UserReferralOperationsView,
    SendChangePasswordCodeView,
    LoginWithTwoAuthCodeView,
    ChangePasswordView,
    ChangeTwoFactorView,
    ChangeEmailView,
    ResetPasswordWithCodeView, LoginRefreshView, UserTransactions
)
from account.views import UserRefAnalyticsView
from account.views import UserViewSet
from account.views import SignUpConfirm
from account.views import LoginView
from account.views import UserBonusPreCalculateView

router = DefaultRouter()

urlpatterns = router.urls
urlpatterns += [
    path('sign_up/', SignUpApi.as_view(), name='sign_up'),
    path('login/',  LoginView.as_view(), name='token_obtain_pair'),
    path('login-with-two-auth-code/',  LoginWithTwoAuthCodeView.as_view(), name='login_with_two_auth_code'),
    path('token/refresh/', LoginRefreshView.as_view(), name='token_refresh'),
    path('user_info/', UserViewSet.as_view({'get': 'list'}), name='user_info'),
    path('account-activate/', SignUpConfirm.as_view(), name='account-activate'),
    path('get-bonus-calculate/', UserBonusPreCalculateView.as_view(), name='get-bonus_calculate'),
    path('referral-statistics/', UserRefAnalyticsView.as_view({'get': 'list'}), name='referral-statistics'),
    path('referral-operations-list/', UserReferralOperationsView.as_view({'get': 'list'}), name='referral-statistics'),
    path('send-change-password-code/', SendChangePasswordCodeView.as_view(), name='send_change_password_code'),
    path('reset-password-with-code/', ResetPasswordWithCodeView.as_view(), name='login_with_reset_password_code'),
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),
    path('change-two-factor-auth/', ChangeTwoFactorView.as_view(), name='change-two-factor-auth'),
    path('change-email/', ChangeEmailView.as_view(), name='change-two-factor-auth'),
    path('user-transactions/', UserTransactions.as_view({'get': 'list'}), name='user-transactions'),
    path('user-transactions/<uuid:unique_id>/', UserTransactions.as_view({'get': 'retrieve'}), name='user-transactions-uuid'),
]
