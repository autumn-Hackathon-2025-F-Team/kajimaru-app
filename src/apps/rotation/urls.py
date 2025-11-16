from django.urls import path
from .view import (
    task_list_view, task_list_create, task_list_edit, task_list_delete,
    maintenance_list_view, maintenance_create, maintenance_edit, maintenance_delete
)

app_name = "rotation"

#週ローテ
urlpatterns = [
    path("tasks/", task_list_view, name="task_list"),
    path("tasks/create/", task_list_create, name="task_list_create"),
    path("tasks/edit/", task_list_edit, name="task_list_edit"),
    path("tasks/delete/", task_list_delete, name="task_list_delete"),
]

#メンテナンス
urlpatterns += [
    path("maintenance/", maintenance_list_view, name="maintenance_list"),
    path("maintenance/create/", maintenance_create, name="maintenance_create"),
    path("maintenance/edit/", maintenance_edit, name="maintenance_edit"),
    path("maintenance/delete/", maintenance_delete, name="maintenance_delete"),
]