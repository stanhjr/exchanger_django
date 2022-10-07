from rest_framework import permissions, viewsets, status, serializers
from rest_framework.decorators import action
from rest_framework.generics import CreateAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser

from account.models import CustomUser
from account.serializers import SignUpSerializer


class SignUpApi(CreateAPIView):
    permission_classes = [permissions.AllowAny]
    queryset = CustomUser.objects.all()
    serializer_class = SignUpSerializer

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        return Response({'message': 'Sign up access',
                         'username': response.data.get('username')},
                        status=status.HTTP_201_CREATED)

