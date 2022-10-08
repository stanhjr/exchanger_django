from django.urls import path
from rest_framework.routers import DefaultRouter

from blog.views import PostList
from blog.views import PostDetail


router = DefaultRouter()

urlpatterns = router.urls
urlpatterns += [
    path('blog/', PostList.as_view(), name='post_list'),
    path('blog/<slug:slug>/', PostDetail.as_view(), name='post_detail')
]
