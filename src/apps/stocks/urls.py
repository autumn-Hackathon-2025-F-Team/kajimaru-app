from django.urls import path
from . import views

app_name = 'stocks'

urlpatterns = [
    path('', views.list_view, name='list'),
    path('create/', views.create_view, name='create')
]