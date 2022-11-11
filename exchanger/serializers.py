from rest_framework import serializers

from exchanger.models import ExchangeRates
from exchanger.models import Transactions
from exchanger.models import Currency


class CurrencySerializer(serializers.ModelSerializer):
    class Meta:
        model = Currency
        fields = '__all__'


class ExchangeSerializer(serializers.ModelSerializer):
    currency_left = CurrencySerializer()
    currency_right = CurrencySerializer()

    class Meta:
        model = ExchangeRates
        fields = ['id', 'value_left', 'value_right', 'currency_left',
                  'currency_right', 'min_value', 'max_value', 'fiat_to_crypto']


class ExchangeIdSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExchangeRates
        fields = ['id', ]


class TransactionsSerializer(serializers.ModelSerializer):
    pairs_id = serializers.IntegerField(required=True)

    class Meta:
        model = Transactions
        fields = ['pairs_id', 'amount_exchange', 'email', 'address']
        extra_kwargs = {'address': {'required': True}, 'email': {'required': True}}

    def validate(self, data):
        data = super().validate(data)
        address = data.get('address')
        if len(address.split()) > 1:
            raise serializers.ValidationError("remove spaces in payment address")
        if len(address) != 16 or not address.isdigit():
            raise serializers.ValidationError("credit card number must be 16 digits")
        return data


class TransactionsFiatToCryptoSerializer(TransactionsSerializer):

    def validate(self, data):

        address = data.get('address')
        if len(address.split()) > 1:
            raise serializers.ValidationError("remove spaces in payment address")
        if len(address) < 16:
            raise serializers.ValidationError("payment address length cannot be less than 16")
        return data


class TransactionsSerializerResponse(serializers.ModelSerializer):
    currency_received = serializers.StringRelatedField()
    currency_exchange = serializers.StringRelatedField()

    class Meta:
        model = Transactions
        fields = ['amount_exchange', 'currency_exchange',
                  'amount_received', 'currency_received',
                  'created_at', 'user', 'deposit_address', 'unique_id', 'email']


class TransactionsSerializerFiatResponse(serializers.ModelSerializer):
    currency_received = serializers.StringRelatedField()
    currency_exchange = serializers.StringRelatedField()

    class Meta:
        model = Transactions
        fields = ['amount_exchange', 'currency_exchange',
                  'amount_received', 'currency_received',
                  'created_at', 'user', 'deposit_address', 'unique_id', 'email']


class CalculateSerializer(serializers.Serializer):
    pairs_id = serializers.IntegerField(required=True)
    price = serializers.FloatField(required=True)


