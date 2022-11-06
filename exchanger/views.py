from django.conf import settings
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, status
from rest_framework import views
from rest_framework.response import Response
from rest_framework.views import APIView

from exchanger import schema

from exchanger.models import ExchangeRates
from exchanger.models import Transactions
from exchanger.models import Currency

from exchanger.serializers import CalculateSerializer, WhiteBitSerializer
from exchanger.serializers import TransactionsSerializerResponse
from exchanger.serializers import ExchangeSerializer
from exchanger.serializers import TransactionsSerializer
from exchanger.serializers import CurrencySerializer


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
            pairs_model = ExchangeRates.objects.filter(id=serializer.data.get("pairs_id")).first()
            if not pairs_model:
                return Response({'detail': 'not found pairs'}, status=404)
            if not pairs_model.get_price_validation(price_left=serializer.data.get("price")):
                return Response({"message": "value is greater or less than allowed values"}, status=400)
            return Response({'value': pairs_model.get_info_calculate(serializer.data.get("price"))}, status=200)

        return Response({'detail': 'not params'}, status=404)


class TransactionsView(generics.CreateAPIView):
    queryset = ExchangeRates.objects.all()
    serializer_class = TransactionsSerializer

    def create(self, request, *args, **kwargs):

        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            exchanger_pair = ExchangeRates.objects.filter(id=serializer.data.get("pairs_id"))
            if not exchanger_pair:
                return Response({'detail': 'not found pairs'}, status=404)
            if self.request.user.is_anonymous:
                user = None
            else:
                user = self.request.user

            transaction = Transactions(user=user,
                                       amount_exchange=serializer.data.get("amount_exchange"),
                                       )
            transaction.save(pairs_id=serializer.data.get("pairs_id"))
            response_serializer = TransactionsSerializerResponse(transaction)
            return Response({'message': 'transaction create', **response_serializer.data},
                            status=status.HTTP_201_CREATED)
        return Response({'detail': 'not valid data'}, status=404)


class WhiteBitWebHook(APIView):

    def post(self, request, format=None):
        if request.META['X-TXC-APIKEY'] != settings.WHITEBIT_API_KEY:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        serializer = WhiteBitSerializer(data=request.data)

        if serializer.is_valid():

            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)