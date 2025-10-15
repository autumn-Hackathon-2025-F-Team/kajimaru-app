from django.urls import path
from . import views

urlpatterns = [
    path("welcome", views.welcome, name="welcome"),
    path("join/verify", views.join_verify, name="join_verify"),
    path("signup", views.signup, name="signup"),
    path("profiles", views.profiles, name="profiles"),
    path("profiles/<int:pk>/enter", views.profile_enter, name="profile_enter"),
    path("profiles/exit", views.profile_exit, name="profile_exit"),
    path("dashboard", views.dashboard, name="dashboard"),
]