from drf_yasg import openapi

pairs_id = openapi.Parameter('pairs_id', openapi.IN_QUERY,
                             description="required field for get currency pairs exchanger",
                             type=openapi.TYPE_INTEGER)

price = openapi.Parameter('price', openapi.IN_QUERY,
                          description="required field for get exchange calculate",
                          type=openapi.TYPE_NUMBER)

