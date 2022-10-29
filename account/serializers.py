from django.contrib.auth.hashers import make_password
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from account.models import CustomUser


class SignUpSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['password', 'email', 'inviter_token', 'login']

    def save(self, **kwargs):
        if len(self.validated_data["password"]) < 8:
            raise serializers.ValidationError({"password": "password must be at least 8 characters long"})
        if CustomUser.objects.filter(email=self.validated_data["email"]).first():
            raise serializers.ValidationError({"email": "this email is busy"})
        if CustomUser.objects.filter(login=self.validated_data["login"]).first():
            raise serializers.ValidationError({"login": "this login is busy"})
        self.validated_data["password"] = make_password(self.validated_data["password"])

        return super().save()


class GetUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['email', 'login', 'referral_url', 'wallet', 'level', 'sum_refers_eq_usdt']


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super(CustomTokenObtainPairSerializer, self).validate(attrs)
        data.update({'login': self.user.login})
        data.update({'email': self.user.email})
        data.update({'referral_url': self.user.referral_url})
        data.update({'wallet': self.user.wallet})
        data.update({'level': self.user.level})
        data.update({'sum_refers_eq_usdt': self.user.sum_refers_eq_usdt})
        return data
