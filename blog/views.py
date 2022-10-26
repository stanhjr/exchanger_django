from functools import reduce
from operator import or_

from django.db.models import Q
from django.utils.decorators import method_decorator
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics

from blog import schema
from blog.models import Post
from blog.models import Tag
from blog.serializers import PostSerializer
from blog.serializers import TagSerializer


class TagList(generics.ListAPIView):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class PostList(generics.ListAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer

    @method_decorator(swagger_auto_schema(manual_parameters=[schema.post_tags]))
    def get(self, request, *args, **kwargs):
        """
        Returned posts list

        Takes tag or tags (optional) and returned posts containing these tags

        Tags format example:
        1. some_tag
        2. some_tag,some_tag2

        """
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        hash_tags = self.request.query_params.get("tags")
        if hash_tags:
            tags = hash_tags.split(",")
            q_object = reduce(or_, (Q(tags__translations__name__icontains=tag) for tag in tags))
            return Post.objects.filter(q_object).distinct()
        return Post.objects.all()


class PostListSearch(generics.ListAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer

    @method_decorator(swagger_auto_schema(manual_parameters=[schema.post_search]))
    def get(self, request, *args, **kwargs):
        """
        Returned posts list

        Takes search query and returned posts containing these query
        """
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        search = self.request.query_params.get("search")
        if search:
            return Post.objects.filter(translations__icontains=search).distinct()
        return Post.objects.all()


class PostDetail(generics.RetrieveAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    lookup_field = 'slug'
