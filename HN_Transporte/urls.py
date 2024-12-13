"""
URL configuration for femmes_grosses_RDV project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from django.urls import path, include
from rest_framework import permissions
from rest_framework.schemas import get_schema_view as rest_frameworkGet_schema_view
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.conf import settings
from django.conf.urls.static import static


schema_view = get_schema_view(
    openapi.Info(
        title="APIs Documentation",
        default_version='v1',
        description="Documentation des APIs",
        terms_of_service="#",
       
        license=openapi.License(name="License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)


urlpatterns = [
    path('admin/', admin.site.urls),
     path('api/', include('HN_Transporte_api.urls')),
    path('rest_auth_api-schema/', rest_frameworkGet_schema_view(
        title='API Schema',
        description='Guide for the REST API',
        permission_classes=(permissions.AllowAny,),
    ), name='api_schema'),
   
    path('auth/', include('dj_rest_auth.urls')),
    path('auth/registration/', include('dj_rest_auth.registration.urls'))
   
]