from django.urls import path
from . import views

app_name = 'maintenance'

urlpatterns = [
    path('', views.list_view, name='list'),
    path('create/', views.create_item, name='create'),
    path('delete/', views.delete_item, name='delete'),
]
