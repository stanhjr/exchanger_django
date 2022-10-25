from drf_yasg import openapi

post_tags = openapi.Parameter('tags', openapi.IN_QUERY,
                              description="fields for get post from tag",
                              type=openapi.TYPE_STRING)

post_search = openapi.Parameter('search string', openapi.IN_QUERY,
                                description="field for search by title or text search",
                                type=openapi.TYPE_STRING)
