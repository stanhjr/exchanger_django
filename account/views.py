from decimal import Decimal

from django.shortcuts import redirect
from django.views.generic import RedirectView
from drf_yasg.utils import swagger_auto_schema
from rest_framework import permissions, viewsets, status, views
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView

from account.models import CustomUser
from account import schema

from account.serializers import (
    SignUpSerializer,
    GetUserSerializer,
    CustomTokenObtainPairSerializer,
    UserBonusCalculateSerializer,
    UserAnalyticsSerializer
)

from celery_tasks.tasks import generate_key
from celery_tasks.tasks import send_reset_password_link_to_email
from celery_tasks.tasks import send_registration_link_to_email
from exchanger_django.settings import HOST

from rest_framework_simplejwt.tokens import RefreshToken, AccessToken


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


class UserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = GetUserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    def list(self, request, *args, **kwargs):
        self.request.user.set_level()
        return self.retrieve(request, *args, **kwargs)


class ResetPassword(RedirectView):
    def dispatch(self, request, *args, **kwargs):
        user_email = self.request.GET.get("email")
        if not user_email:
            return redirect('home')
        user = CustomUser.objects.filter(email=user_email).first()

        if user:
            code = generate_key()
            user.reset_password_code = code
            user.save()
            send_reset_password_link_to_email.delay(code=code,
                                                    subject="Reset Password",
                                                    email_to=user_email)
            redirect(HOST)

        return redirect(HOST)


class SignUpConfirm(RedirectView):

    def dispatch(self, request, *args, **kwargs):
        code = self.request.GET.get("code")
        if not code:
            return redirect(HOST)
        user = CustomUser.objects.filter(verify_code=code).first()
        if user:
            user.verify_code = ''
            user.is_confirmed = True
            user.save()
            return redirect(HOST)
        else:
            return redirect(HOST)


class LoginView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


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


class UserAnalyticsView(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = UserAnalyticsSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    def list(self, request, *args, **kwargs):
        self.request.user.set_level()
        return self.retrieve(request, *args, **kwargs)