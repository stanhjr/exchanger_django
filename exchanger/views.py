from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics
from rest_framework import views
from rest_framework.response import Response
from exchanger import schema

from exchanger.models import ExchangeRates
from exchanger.serializers import ExchangeSerializer, CalculateSerializer


class ExchangeList(generics.ListAPIView):
    pagination_class = None
    queryset = ExchangeRates.objects.all()
    serializer_class = ExchangeSerializer


class ExchangeCalculate(views.APIView):

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
            return Response({'value': pairs_model.get_calculate(serializer.data.get("price"))}, status=200)

        return Response({'detail': 'not params'}, status=404)
