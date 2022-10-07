from rest_framework import permissions, viewsets, status
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response

from account.models import CustomUser
from account.serializers import SignUpSerializer, GetUserSerializer


class SignUpApi(CreateAPIView):
    permission_classes = [permissions.AllowAny]
    queryset = CustomUser.objects.all()
    serializer_class = SignUpSerializer

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        return Response({'message': 'Sign up access',
                         'email': response.data.get('email')},
                        status=status.HTTP_201_CREATED)


class UserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = GetUserSerializer

    def get_object(self):
        return self.request.user

    def list(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)
