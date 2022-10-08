from django.utils.decorators import method_decorator
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics

from blog import schema
from blog.models import Post
from blog.serializers import PostSerializer


class PostList(generics.ListAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer

    @method_decorator(swagger_auto_schema(manual_parameters=[schema.post_tags]))
    def get(self, request, *args, **kwargs):
        """

        Takes tag or tags (optional) and returned posts containing these tags

        Tags format example:
        1. yourtag
        2. onetag,twotag

        """
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        hash_tags = self.request.query_params.get("tags")
        if hash_tags:
            tags = hash_tags.split(",")
            return Post.objects.filter(tags__name__in=tags).distinct()
        return Post.objects.all()


class PostDetail(generics.RetrieveAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    lookup_field = 'slug'
