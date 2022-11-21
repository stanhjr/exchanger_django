"""exchanger_django URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.urls import include
from django.conf.urls.static import static
from django.conf import settings

from bestchange.views import best_change_xml
from webhook.views import WhiteBitVerify, WhiteBitWebHook
from .yasg import url_patterns as doc_urls


urlpatterns = [

    path('api/admin/', admin.site.urls),
    path('api/account/', include('account.urls')),
    path('api/blog/', include('blog.urls')),
    path('api/important_info/', include('important_info.urls')),
    path('api/exchanger/', include('exchanger.urls')),
    path('api/webhook/', WhiteBitWebHook.as_view(), name='web_hook'),
    path('whiteBIT-verification', WhiteBitVerify.as_view(), name='whiteBIT-verification'),
    path('api/bestchange.xml/', best_change_xml)
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += doc_urls
