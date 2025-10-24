from django.urls import path
from . import views
from django.views.generic import TemplateView

urlpatterns = [
    # 管理者サインアップ/ログイン
    path('signup/', views.signup, name='signup'),
    path('login/', views.admin_login, name='admin_login'),

    # 参加コード検証
    path('join/verify/', views.join_verify, name='join_verify'),
    path('welcome/', TemplateView.as_view(template_name='user/code_input.html'), name='welcome'),
    path('invite/create/', views.invite_create, name='invite_create'),

    # プロフィール関連
    path('profiles/', views.profiles_list, name='profiles_list'),
    path('profiles/<int:pk>/enter/', views.profile_enter, name='profile_enter'),
    path('members/new/', views.member_create, name='member_create'),
    path('members/<int:pk>/edit/', views.member_edit, name='member_edit'),
    path('members/<int:pk>/delete/', views.member_delete, name='member_delete'),

    # ダッシュボード
    path('dashboard/', TemplateView.as_view(template_name='user/dashboard.html'), name='dashboard'),
]