from django.urls import path
from rest_framework.routers import DefaultRouter

from blog.views import PostList
from blog.views import PostListSearch
from blog.views import PostDetail
from blog.views import TagList


router = DefaultRouter()

urlpatterns = router.urls
urlpatterns += [
    path('tags/', TagList.as_view(), name='tag_list'),
    path('posts_by_tags/', PostList.as_view(), name='post_list_by_tags'),
    path('posts_search/', PostListSearch.as_view(), name='post_list'),
    path('<slug:slug>/', PostDetail.as_view(), name='post_detail'),
]
