"""ratonGato URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
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
from logic import views
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

handler404 = views.error404

urlpatterns = [
    path('index/', views.index, name='index'),
    path('', views.index, name='landing'),
    path('admin/', admin.site.urls),
    path('raton_gato/', include('logic.urls')),
]

urlpatterns += staticfiles_urlpatterns()
