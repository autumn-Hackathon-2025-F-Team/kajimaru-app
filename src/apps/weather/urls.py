from django.urls import path
from . import views

app_name = 'weather'

urlpatterns = [
    path('recommendations/', views.weather_recommendations, name='recommendations'),
]