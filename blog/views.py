from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from blog.models import Post
from blog.serializers import PostSerializer


class PostList(generics.ListAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
