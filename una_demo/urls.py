"""una_demo URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
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
from django.urls import include, re_path, path

from una_app.views import get_glucose_levels, get_glucose_highlow, export_glucose_levels, populate_dataset

from rest_framework_swagger.views import get_swagger_view

schema_view = get_swagger_view(title='UNA API')

prefixed_urlpatterns = [path(r'levels/', get_glucose_levels),
                        path(r'levels/<int:entry_id>/', get_glucose_levels),
                        path(r'levels/export/<str:format>/', export_glucose_levels),
                        path(r'highlow/', get_glucose_highlow),
                        path(r'populate/', populate_dataset)]

urlpatterns = [
    re_path(r'^$', schema_view),
    re_path(r'admin/', admin.site.urls),
    re_path(r'api/v1/', include(prefixed_urlpatterns))
]
