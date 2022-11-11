from decimal import Decimal

from django.core.exceptions import ValidationError
from drf_yasg.utils import swagger_auto_schema

from rest_framework import generics, status
from rest_framework import views
from rest_framework.response import Response

from exchanger import schema

from exchanger.models import ExchangeRates
from exchanger.models import Transactions
from exchanger.models import Currency
from exchanger.redis_api import redis_cache

from exchanger.serializers import (
    CalculateSerializer,
    TransactionsSerializerFiatResponse,
    TransactionsFiatToCryptoSerializer,
    TransactionsSerializerResponse,
    ExchangeSerializer,
    TransactionsSerializer,
    CurrencySerializer,
)

from exchanger.whitebit_api import WhiteBitApi


class CurrencyListView(generics.ListAPIView):
    pagination_class = None
    queryset = Currency.objects.all()
    serializer_class = CurrencySerializer


class ExchangeListView(generics.ListAPIView):
    pagination_class = None
    queryset = ExchangeRates.objects.all()
    serializer_class = ExchangeSerializer


class ExchangeCalculateView(views.APIView):

    @swagger_auto_schema(manual_parameters=[schema.pairs_id, schema.price])
    def get(self, request):
        """
        Takes required query params and returned pre calculate value
        """
        serializer = CalculateSerializer(data=self.request.query_params)
        if serializer.is_valid():
            redis_cache.cache_exchange_rates()
            pairs_model = ExchangeRates.objects.filter(id=serializer.data.get("pairs_id")).first()
            if not pairs_model:
                return Response({'detail': 'not found pairs'}, status=404)
            if not pairs_model.get_price_validation(price_exchange=serializer.data.get("price")):
                return Response({"message": "value is greater or less than allowed values"}, status=400)
            return Response({'value': pairs_model.get_info_calculate(serializer.data.get("price"))}, status=200)

        return Response({'detail': 'not params'}, status=404)


class TransactionsCryptoToFiatView(generics.CreateAPIView):
    queryset = ExchangeRates.objects.all()
    serializer_class = TransactionsSerializer

    def create(self, request, *args, **kwargs):

        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            redis_cache.cache_exchange_rates()
            exchanger_pair = ExchangeRates.objects.filter(id=serializer.data.get("pairs_id")).first()
            amount_exchange = Decimal(serializer.data.get("amount_exchange"))
            if not exchanger_pair:
                return Response({'detail': 'not found pairs'}, status=404)
            if exchanger_pair.fiat_to_crypto:
                return Response({'detail': 'this pairs id dont exchange fiat to crypto'}, status=400)

            if amount_exchange > exchanger_pair.max_value:
                return Response({'detail': 'amount_exchange more than allowed values'}, status=400)
            if amount_exchange < exchanger_pair.min_value:
                return Response({'detail': 'amount_exchange less than allowed values'}, status=400)
            if self.request.user.is_anonymous:
                user = None
            else:
                user = self.request.user

            transaction = Transactions(user=user,
                                       amount_exchange=serializer.data.get("amount_exchange"),
                                       email=serializer.data.get("email"),
                                       address=serializer.data.get("address"),
                                       )

            white_bit_api = WhiteBitApi()
            try:
                deposit_address = white_bit_api.get_deposit_address(
                    currency_ticker=exchanger_pair.currency_left.name_from_white_bit,
                    amount_price=transaction.amount_exchange,
                    network=exchanger_pair.currency_left.network)
            except Exception as e:
                print(e)
                return Response({'detail': 'WhiteBitApi failed'}, status=500)
            transaction.deposit_address = deposit_address
            try:
                transaction.save(pairs_id=serializer.data.get("pairs_id"))
            except ValidationError:
                return Response({'detail': 'validation error'}, status=500)

            response_serializer = TransactionsSerializerResponse(transaction)
            return Response({'message': 'transaction create', **response_serializer.data},
                            status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=400)


class TransactionsFiatToCryptoView(generics.CreateAPIView):
    queryset = ExchangeRates.objects.all()
    serializer_class = TransactionsFiatToCryptoSerializer

    def create(self, request, *args, **kwargs):

        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            redis_cache.cache_exchange_rates()
            exchanger_pair = ExchangeRates.objects.filter(id=serializer.data.get("pairs_id")).first()
            amount_exchange = Decimal(serializer.data.get("amount_exchange"))
            if not exchanger_pair:
                return Response({'detail': 'not found pairs'}, status=404)
            if not exchanger_pair.fiat_to_crypto:
                return Response({'detail': 'this pairs id dont exchange crypto to fiat'}, status=400)

            if amount_exchange > exchanger_pair.max_value:
                return Response({'detail': 'amount_exchange more than allowed values'}, status=400)
            if amount_exchange < exchanger_pair.min_value:
                return Response({'detail': 'amount_exchange less than allowed values'}, status=400)
            if self.request.user.is_anonymous:
                user = None
            else:
                user = self.request.user

            transaction = Transactions(user=user,
                                       amount_exchange=serializer.data.get("amount_exchange"),
                                       email=serializer.data.get("email"),
                                       address=serializer.data.get("address"),
                                       )

            try:
                transaction.save(pairs_id=serializer.data.get("pairs_id"))
            except ValidationError as e:
                return Response({'detail': 'validation error'}, status=500)

            white_bit_api = WhiteBitApi()
            try:
                transaction.deposit_address = white_bit_api.get_fiat_form(
                    transaction_unique_id=str(transaction.fiat_unique_id),
                    amount_price=str(transaction.amount_exchange),

                )
            except Exception as e:
                print(e)
                return Response({'detail': 'WhiteBitApi failed'}, status=500)

            try:
                transaction.save(pairs_id=serializer.data.get("pairs_id"))
            except ValidationError:
                return Response({'detail': 'validation error'}, status=500)

            response_serializer = TransactionsSerializerFiatResponse(transaction)
            return Response({'message': 'transaction create', **response_serializer.data},
                            status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=400)
