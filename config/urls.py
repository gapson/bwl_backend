"""bwl URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
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
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.conf.urls import url, re_path
from django.conf.urls.i18n import i18n_patterns
from rest_framework_simplejwt import views
from django.views.generic import TemplateView
from djoser import urls
from djoser.urls import jwt
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from rest_framework import permissions
from rest_framework_simplejwt.authentication import JWTAuthentication
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.contrib.auth import get_user_model
from rest_framework.routers import DefaultRouter

from content.views import LoginView, UserViewSet
import content

#from rest_framework.schemas import get_schema_view
#urlpatterns = [
    #re_path(r"^auth/login/?", views.TokenObtainPairView.as_view(), name="jwt-create"),
    #re_path(r"^jwt/refresh/?", views.TokenRefreshView.as_view(), name="jwt-refresh"),
    #re_path(r"^jwt/verify/?", views.TokenVerifyView.as_view(), name="jwt-verify"),
#]

schema_view = get_schema_view(
   openapi.Info(
      title="BWL API Documentation",
      default_version='v1',
      description="BWL API Documentation",
      contact=openapi.Contact(email="gabrielngankam@gmail.com")
   ),
   public=True,
   permission_classes=(permissions.BasePermission,),
)

router = DefaultRouter()

urlpatterns = [
    #url(r'^jet/', include('jet.urls', 'jet')),  # Django JET URLS
    path('admin/', admin.site.urls),
    #url(r'^auth/', include('djoser.urls.jwt')),
    re_path(r"^auth/login/?", LoginView.as_view(), name="login"),
    re_path(r"^auth/create_token/?", views.TokenObtainPairView.as_view(), name="jwt-create"),
    re_path(r"^auth/refresh-token/?", views.TokenRefreshView.as_view(), name="jwt-refresh"),
    #re_path(r"^auth/user/password/reset/confirm/(?P<uid>[\w-]+)/(?P<token>[\w-]+)", LoginView.as_view(), name="password_reset_confirm"),
    url(r'^api/v1/docs(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    url(r'^api/v1/docs/$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    url(r'^api/v1/doc/$', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    #path('api-auth/', include('rest_framework.urls'))
    #url(r'^auth/', include('djoser.urls')),
    url(r'^api/v1/', include('content.urls')),
]
urlpatterns += [url(r'^i18n/', include('django.conf.urls.i18n')),]
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

router.register("auth/users", UserViewSet)

User = get_user_model()
urlpatterns += router.urls

