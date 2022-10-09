from rest_framework import serializers

from exchanger.models import ExchangeRates
from exchanger.models import Transactions


class ExchangeSerializer(serializers.ModelSerializer):
    currency_left = serializers.StringRelatedField()
    currency_right = serializers.StringRelatedField()

    class Meta:
        model = ExchangeRates
        fields = ['id', 'value_left', 'value_right', 'currency_left', 'currency_right']


class ExchangeIdSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExchangeRates
        fields = ['id', ]


class TransactionsSerializer(serializers.ModelSerializer):
    pairs_id = serializers.IntegerField(required=True)

    class Meta:
        model = Transactions
        fields = ['pairs_id', 'amount_exchange']


class TransactionsSerializerResponse(serializers.ModelSerializer):
    currency_received = serializers.StringRelatedField()
    currency_exchange = serializers.StringRelatedField()

    class Meta:
        model = Transactions
        fields = ['amount_exchange', 'currency_exchange', 'amount_received', 'currency_received', 'created_at', 'user']


class CalculateSerializer(serializers.Serializer):
    pairs_id = serializers.IntegerField(required=True)
    price = serializers.FloatField(required=True)
