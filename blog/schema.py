from drf_yasg import openapi

post_tags = openapi.Parameter('tags', openapi.IN_QUERY,
                              description="fields for get post from tag",
                              type=openapi.TYPE_STRING)


