from django.contrib.auth.hashers import make_password
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from account.models import CustomUser
from exchanger.models import Transactions


class SignUpSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['password', 'email', 'inviter_token', 'username']

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
        fields = ['email', 'username', 'referral_url', 'wallet', 'level', 'sum_refers_eq_usdt', 'is_confirmed']


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super(CustomTokenObtainPairSerializer, self).validate(attrs)
        data.update({'user': GetUserSerializer(instance=self.user).data})
        return data


class UserBonusCalculateSerializer(serializers.Serializer):
    referral_number = serializers.IntegerField(required=True)
    price = serializers.IntegerField(required=True)


class UserAnalyticsSerializer(serializers.ModelSerializer):
    available_for_payment = serializers.CharField(source='wallet')

    class Meta:
        model = CustomUser
        fields = ['counts_of_referral', 'available_for_payment',
                  'paid_from_referral', 'total_sum_from_referral', 'referral_url']


class UserReferralOperationsSerializer(serializers.ModelSerializer):

    class Meta:
        model = Transactions
        fields = ['transaction_date', 'user_email', 'inviter_earned_by_transaction']
