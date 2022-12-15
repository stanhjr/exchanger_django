from decimal import Decimal
from datetime import datetime, timedelta

from django.utils import timezone

from drf_yasg.utils import swagger_auto_schema
from rest_framework import permissions, viewsets, status, views
from rest_framework.generics import CreateAPIView, UpdateAPIView

from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from account.models import CustomUser, Payouts
from account import schema

from account.serializers import (
    SignUpSerializer,
    GetUserSerializer,
    CustomTokenObtainPairSerializer,
    UserBonusCalculateSerializer,
    UserAnalyticsSerializer,
    UserReferralOperationsSerializer,
    UserTwoFactorSerializer,
    ChangePasswordSerializer,
    ChangeTwoFactorSerializer,
    ChangeEmailSerializer,
    LoginWithTwoAuthCodeSerializer,
    ResetPasswordWithCodeSerializer,
    CustomTokenRefreshSerializer,
    SignUpConfirmSerializer,
    UserTransactionSerializer, CreatePayoutSerializer,
)

from celery_tasks.tasks import (
    generate_key,
    send_verify_code_to_email,
    send_reset_password_code_to_email
)
from celery_tasks.tasks import send_registration_link_to_email
from exchanger.models import Transactions

from rest_framework_simplejwt.tokens import RefreshToken, AccessToken

from exchanger.pagination import CustomPaginator


class SignUpApi(CreateAPIView):
    permission_classes = [permissions.AllowAny]
    queryset = CustomUser.objects.all()
    serializer_class = SignUpSerializer

    def create(self, request, *args, **kwargs):
        code = generate_key()
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.verify_code = code
            user = CustomUser.objects.create_user(
                email=serializer.validated_data['email'],
                username=serializer.validated_data['username'],
                password=serializer.validated_data['password'],
                verify_code=code,
                inviter_token=serializer.validated_data.get('inviter_token')
            )
            send_registration_link_to_email.delay(email_to=serializer.validated_data.get("email"),
                                                  code=code,
                                                  subject="Email Verify Code")
            refresh_token = RefreshToken.for_user(user)
            access_token = AccessToken.for_user(user)
            response = {"user": GetUserSerializer(instance=user).data}
            response.update(access_token=str(access_token))
            response.update(refresh_token=str(refresh_token))
            return Response(response, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GetTwoFactorCode(CreateAPIView):
    permission_classes = [permissions.AllowAny]
    queryset = CustomUser.objects.all()
    serializer_class = UserTwoFactorSerializer

    def create(self, request, *args, **kwargs):
        code = generate_key()
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            user = CustomUser.objects.filter(email=serializer.validated_data['email']).first()
            if not user:
                return Response({'detail': 'not user'}, status=400)
            user.two_factor_auth_code = code
            user.save()
            send_verify_code_to_email.delay(email_to=serializer.validated_data.get("email"),
                                            code=code,
                                            subject="Email Verify Code")

            return Response({'detail': 'email sending'}, status=status.HTTP_200_OK)
        return Response({'detail': 'not valid email'}, status=404)


class UserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = GetUserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    def list(self, request, *args, **kwargs):
        self.request.user.set_level()
        return self.retrieve(request, *args, **kwargs)


class SignUpConfirm(TokenObtainPairView):
    serializer_class = SignUpConfirmSerializer
    model = CustomUser


class ResetPasswordWithCodeView(UpdateAPIView):
    serializer_class = ResetPasswordWithCodeSerializer
    model = CustomUser

    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            response = {
                'status': 'success',
                'code': status.HTTP_200_OK,
                'message': 'Password updated successfully',
                'data': []
            }

            return Response(response)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class LoginRefreshView(TokenRefreshView):
    serializer_class = CustomTokenRefreshSerializer


class LoginWithTwoAuthCodeView(TokenObtainPairView):
    serializer_class = LoginWithTwoAuthCodeSerializer


class UserBonusPreCalculateView(views.APIView):

    @swagger_auto_schema(manual_parameters=[schema.referral_number, schema.price])
    def get(self, request):
        """
        Takes required query params and returned pre calculate bonus value
        """
        serializer = UserBonusCalculateSerializer(data=self.request.query_params)
        if serializer.is_valid():
            from exchanger.models import ProfitModel, ProfitTotal
            price = serializer.data.get("referral_number") * serializer.data.get("price")
            percent_total = ProfitTotal.objects.filter(total_usdt__lte=price).first()
            profit_model = ProfitModel.objects.filter(price_dollars__lte=price).first()
            if profit_model and percent_total:
                result = price * profit_model.profit_percent_coef * percent_total.profit_percent
                result = Decimal(result)
            else:
                result = Decimal(price * 0)
            return Response({'value': result}, status=200)

        return Response({'detail': 'not params'}, status=404)


class UserRefAnalyticsView(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = UserAnalyticsSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    def list(self, request, *args, **kwargs):
        self.request.user.set_level()
        return self.retrieve(request, *args, **kwargs)


class UserReferralOperationsView(viewsets.ModelViewSet):
    queryset = Transactions.objects.all().select_related('user')
    serializer_class = UserReferralOperationsSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    def get_queryset(self):
        return Transactions.objects.filter(user__inviter_token=self.request.user.pk).all().select_related('user')


class SendChangePasswordCodeView(UpdateAPIView):
    permission_classes = [permissions.AllowAny]
    queryset = CustomUser.objects.all()
    serializer_class = UserTwoFactorSerializer

    def update(self, request, *args, **kwargs):
        code = generate_key()
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = CustomUser.objects.filter(email=serializer.validated_data['email']).first()
            if not user:
                return Response({'detail': 'not_user'}, status=400)
            user.reset_password_code = code
            user.save()
            send_reset_password_code_to_email.delay(email_to=serializer.validated_data.get("email"),
                                                    code=code,
                                                    subject="Email Verify Code")

            return Response({'detail': 'email sending'}, status=status.HTTP_200_OK)
        return Response({'detail': 'not valid email'}, status=404)


class SendVerifyCodeView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = CustomUser.objects.all()

    def post(self, request):
        if self.request.user.is_confirmed is True:
            return Response("message: account is confirmed", status=status.HTTP_200_OK)
        code = generate_key()
        self.request.user.verify_code = code
        self.request.user.save()
        send_registration_link_to_email.delay(email_to=self.request.user.email,
                                              code=code,
                                              subject="Email Verify Code")
        return Response("message: code sending", status=status.HTTP_200_OK)


class ChangePasswordView(UpdateAPIView):
    serializer_class = ChangePasswordSerializer
    model = CustomUser
    permission_classes = (IsAuthenticated,)

    def get_object(self, queryset=None):
        obj = self.request.user
        return obj

    def update(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            if not user.check_password(serializer.data.get("old_password")):
                return Response({"old_password": ["Wrong password."]}, status=status.HTTP_400_BAD_REQUEST)
            user.set_password(serializer.data.get("new_password"))
            user.save()
            response = {
                'status': 'success',
                'code': status.HTTP_200_OK,
                'message': 'Password updated successfully',
                'data': []
            }

            return Response(response)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ChangeTwoFactorView(UpdateAPIView):
    serializer_class = ChangeTwoFactorSerializer
    model = CustomUser
    permission_classes = (IsAuthenticated,)

    def get_object(self, queryset=None):
        obj = self.request.user
        return obj

    def update(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user.two_factor_auth = serializer.data.get("two_factor_auth")
            user.save()
            response = {
                'status': 'success',
                'code': status.HTTP_200_OK,
                'two_factor_auth': user.two_factor_auth,
                'data': []
            }

            return Response(response)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ChangeEmailView(UpdateAPIView):
    serializer_class = ChangeEmailSerializer
    model = CustomUser
    permission_classes = (IsAuthenticated,)

    def get_object(self, queryset=None):
        obj = self.request.user
        return obj

    def update(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            if user.email != serializer.data.get("old_email"):
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            user.email = serializer.data.get("new_email")
            user.reset_info_date_time = timezone.now()
            user.save()
            response = {
                'status': 'success',
                'code': status.HTTP_200_OK,
                'two_factor_auth': user.two_factor_auth,
                'data': []
            }

            return Response(response)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserTransactions(viewsets.ModelViewSet):
    queryset = Transactions.objects.all()
    serializer_class = UserTransactionSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPaginator

    def get_queryset(self):
        return Transactions.objects.filter(user=self.request.user).all()

    def get_object(self):
        return self.request.user

    # def list(self, request, *args, **kwargs):
    #     return self.retrieve(request, *args, **kwargs)
    #
    # def retrieve(self, request, *args, **kwargs):


class PayoutCreateView(CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Payouts.objects.all()
    serializer_class = CreatePayoutSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():

            if Decimal(serializer.validated_data.get('price_usdt')) <= 0:
                return Response({'detail': 'not Zero please'}, status=400)
            if Decimal(serializer.validated_data.get('price_usdt')) > self.request.user.available_for_payment:
                return Response({'detail': 'insufficient funds'}, status=400)
            if Payouts.objects.filter(user=self.request.user, is_confirm=False).count() > 1:
                return Response({'detail': 'you have an open payout'}, status=400)
            if self.request.user.reset_info_date_time > datetime.now() - timedelta(days=1):
                return Response({'detail': f'a day must pass from the moment you reset'
                                           f' your password or email, you reset '
                                           f'{self.request.user.reset_info_date_time}'}, status=400)

            Payouts.objects.create(user=self.request.user,
                                   price_usdt=serializer.validated_data.get('price_usdt'),
                                   )
            return Response({'detail': 'payout created!'}, status=status.HTTP_200_OK)
