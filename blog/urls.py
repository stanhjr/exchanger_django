from django.urls import path
from rest_framework.routers import DefaultRouter

from blog.views import PostList
from blog.views import PostDetail


router = DefaultRouter()

urlpatterns = router.urls
urlpatterns += [
    path('', PostList.as_view(), name='post_list'),
    path('<slug:slug>/', PostDetail.as_view(), name='post_detail')
]
