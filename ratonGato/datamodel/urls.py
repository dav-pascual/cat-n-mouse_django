from datamodel import views
from django.urls import path

app_name = 'datamodel'

urlpatterns = [
    path('', views.index, name='index')
]
