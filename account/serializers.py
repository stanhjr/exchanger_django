from django.contrib.auth.hashers import make_password
from rest_framework import serializers
from account.models import CustomUser


class SignUpSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['password', 'email']

    def save(self, **kwargs):
        if len(self.validated_data["password"]) < 8:
            raise serializers.ValidationError({"password": "password must be at least 8 characters long"})
        if CustomUser.objects.filter(email=self.validated_data["email"]).first():
            raise serializers.ValidationError({"email": "this email is busy"})
        self.validated_data["password"] = make_password(self.validated_data["password"])
        return super().save()
