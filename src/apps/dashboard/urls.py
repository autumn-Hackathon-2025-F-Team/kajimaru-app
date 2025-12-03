from django.urls import path
from .view import DashboardView, ToggleTaskDoneView
from .view import request_substitute, accept_substitute, toggle_busy

app_name = "dashboard"

urlpatterns = [
    path('', DashboardView.as_view(), name="dashboard"),
    path("tasks/<int:pk>/toggle/", ToggleTaskDoneView.as_view(), name="task_toggle"),
    path("tasks/<int:task_id>/request_substitute/", request_substitute, name="request_substitute"),
    path("tasks/<int:task_id>/accept_substitute/", accept_substitute, name="accept_substitute"),
    path("toggle-busy/", toggle_busy, name="toggle_busy"),
]