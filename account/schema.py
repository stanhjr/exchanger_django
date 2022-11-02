from drf_yasg import openapi

referral_number = openapi.Parameter('referral_number', openapi.IN_QUERY,
                                    description="required field for get bonus calculate referral number",
                                    type=openapi.TYPE_INTEGER)

price = openapi.Parameter('price', openapi.IN_QUERY,
                          description="required field for get bonus calculate",
                          type=openapi.TYPE_NUMBER)

email = openapi.Parameter('email', openapi.IN_QUERY,
                          description="required field for get bonus calculate",
                          type=openapi.TYPE_STRING)
