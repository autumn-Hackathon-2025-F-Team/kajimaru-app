from django.urls import path
from . import views

app_name = 'shopping'

urlpatterns = [
    path('shopping/', views.list_view, name='list'),
    path('shopping/add/', views.add, name='add'),
    path('shopping/toggle/<int:pk>/', views.toggle, name='toggle'),
    path('shopping/detail/<int:pk>/', views.detail, name='detail'),
    path('shopping/delete/<int:pk>/', views.delete, name='delete'),
]