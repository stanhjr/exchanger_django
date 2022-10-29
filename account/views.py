from django.shortcuts import redirect
from django.views.generic import RedirectView
from rest_framework import permissions, viewsets, status
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from account.models import CustomUser
from account.serializers import SignUpSerializer, GetUserSerializer

from celery_tasks.tasks import generate_key
from celery_tasks.tasks import send_reset_password_link_to_email
from celery_tasks.tasks import send_registration_link_to_email
from exchanger_django.settings import HOST


class SignUpApi(CreateAPIView):
    permission_classes = [permissions.AllowAny]
    queryset = CustomUser.objects.all()
    serializer_class = SignUpSerializer

    # def perform_create(self, serializer):
    #     code = generate_key()
    #     serializer.verify_code = code
    #     send_registration_link_to_email.delay(email_to=serializer.validated_data.get("email"),
    #                                           code=code,
    #                                           subject="Email Verify Code")
    #     serializer = serializer.save()
    #     serializer.verify_code = code
    #     return serializer.save()

    def create(self, request, *args, **kwargs):
        code = generate_key()
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.verify_code = code
            user = CustomUser.objects.create_user(
                email=serializer.validated_data['email'],
                username=serializer.validated_data['email'],
                password=serializer.validated_data['password'],
                login=serializer.validated_data['login'],
            )
            send_registration_link_to_email.delay(email_to=serializer.validated_data.get("email"),
                                                  code=code,
                                                  subject="Email Verify Code")
            return Response(GetUserSerializer(instance=user).data, status=status.HTTP_201_CREATED)
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
