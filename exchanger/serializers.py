from rest_framework import serializers

from exchanger.models import ExchangeRates


class ExchangeSerializer(serializers.ModelSerializer):
    currency_left = serializers.StringRelatedField()
    currency_right = serializers.StringRelatedField()

    class Meta:
        model = ExchangeRates
        fields = ['id', 'value_left', 'value_right', 'currency_left', 'currency_right']


class CalculateSerializer(serializers.Serializer):
    pairs_id = serializers.IntegerField(required=True)
    price = serializers.FloatField(required=True)
