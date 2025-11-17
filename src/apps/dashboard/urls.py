from django.urls import path
from .view import DashboardView

urlpatterns = [
    path('', DashboardView.as_view(), name="dashboard")
]