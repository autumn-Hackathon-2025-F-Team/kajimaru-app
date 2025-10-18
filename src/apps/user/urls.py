from django.urls import path
from . import views
from django.views.generic import TemplateView

urlpatterns = [
    # 管理者サインアップ/ログイン
    path('signup/', views.signup, name='signup'),
    path('login/', views.admin_login, name='admin_login'),

    # 参加コード検証
    path('join_verify/', views.join_verify, name='join_verify'),

    # プロフィール関連
    path('profiles/<int:pk>/', views.profiles, name='profiles'),

    #まだ未実装
    path('welcome/', TemplateView.as_view(template_name='user/welcome.html'), name='welcome'),
    path('dashboard/', TemplateView.as_view(template_name='user/dashboard.html'), name='dashboard'),
]