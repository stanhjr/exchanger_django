from django.contrib.auth.hashers import make_password
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenRefreshSerializer
from django.utils.translation import gettext_lazy as _
from rest_framework_simplejwt.tokens import RefreshToken

from account.exception_custom import TwoFactorAuthException
from account.models import CustomUser
from celery_tasks.tasks import generate_key, send_verify_code_to_email
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
        fields = ['email', 'username', 'referral_url', 'wallet', 'level', 'sum_refers_eq_usdt', 'is_confirmed',
                  'two_factor_auth']


class CustomTokenRefreshSerializer(TokenRefreshSerializer):
    def validate(self, attrs):
        attrs = super(CustomTokenRefreshSerializer, self).validate(attrs)
        refresh_token = RefreshToken(attrs['refresh'])
        access_token = refresh_token.access_token
        user = CustomUser.objects.get(id=access_token['user_id'])
        attrs.update({'user': GetUserSerializer(instance=user).data})
        return attrs


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):

    def validate(self, attrs):
        username = attrs.get('username')
        user = CustomUser.objects.filter(username=username).first()
        if not user:
            raise AuthenticationFailed(
                self.error_messages['no_active_account'],
                'no_active_account',
            )
        if not user.check_password(attrs.get('password')):
            raise AuthenticationFailed(
                'not valid password or no_active_account',
                'not valid password or no_active_account',
            )
        if user.two_factor_auth:
            code = generate_key()
            user.two_factor_auth_code = code
            user.save()
            send_verify_code_to_email.delay(email_to=user.email,
                                            code=code,
                                            subject="Email Verify Code")
            raise TwoFactorAuthException()

        data = super(CustomTokenObtainPairSerializer, self).validate(attrs)
        data.update({'user': GetUserSerializer(instance=user).data})
        return data


class ResetPasswordWithCodeSerializer(serializers.Serializer):
    model = CustomUser

    """
    Serializer for email change endpoint with code
    """
    reset_password_code = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

    def validate(self, data):
        reset_password_code = data.get('reset_password_code')
        user = CustomUser.objects.filter(reset_password_code=reset_password_code).first()
        if not user:
            raise AuthenticationFailed(
                'not_valid_code',
                'no_active_account',
            )
        user.set_password(data.get("new_password"))
        user.reset_password_code = ''
        user.save()
        return data


class LoginWithTwoAuthCodeSerializer(serializers.Serializer):
    default_error_messages = {
        'not_valid_code': _('not_valid_code'),

    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['two_auth_code'] = serializers.CharField(required=True)

    def validate(self, attrs):
        two_auth_code = attrs.get('two_auth_code')
        user = CustomUser.objects.filter(two_factor_auth_code=two_auth_code).first()
        if not user:
            raise AuthenticationFailed(
                self.default_error_messages['not_valid_code'],
                'no_active_account',
            )

        user.two_factor_auth_code = ''
        user.save()

        refresh = TokenObtainPairSerializer.get_token(user)
        data = {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }
        data.update({'user': GetUserSerializer(instance=user).data})
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


class UserTwoFactorSerializer(serializers.Serializer):
    email = serializers.CharField(required=True)


class ChangePasswordSerializer(serializers.Serializer):
    model = CustomUser

    """
    Serializer for password change endpoint.
    """
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)


class ChangeTwoFactorSerializer(serializers.Serializer):
    model = CustomUser
    """
    Serializer for two_factor_authd change endpoint.
    """
    two_factor_auth = serializers.BooleanField(required=True)


class ChangeEmailSerializer(serializers.Serializer):
    model = CustomUser

    """
    Serializer for email change endpoint.
    """
    old_email = serializers.EmailField(required=True)
    new_email = serializers.EmailField(required=True)


class SignUpConfirmSerializer(serializers.Serializer):

    default_error_messages = {
        'not_valid_code': _('not_valid_code'),

    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['code'] = serializers.CharField(required=True, min_length=15)

    def validate(self, attrs):
        code = attrs.get('code')
        user = CustomUser.objects.filter(verify_code=code).first()
        if not user:
            raise AuthenticationFailed(
                self.default_error_messages['not_valid_code'],
                'no_active_account',
            )

        user.verify_code = ''
        user.save()

        refresh = TokenObtainPairSerializer.get_token(user)
        data = {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }
        data.update({'user': GetUserSerializer(instance=user).data})
        return data


class UserTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transactions
        fields = ['transaction_date', 'status', 'currency_exchange', 'currency_received',
                  'amount_exchange', 'amount_real_received', 'created_at', 'address',
                  'address_from', 'address_to', 'get_deposit', 'complete', 'unique_id']
