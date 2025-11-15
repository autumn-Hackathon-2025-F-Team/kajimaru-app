from django.urls import path
from . import views
from django.views.generic import TemplateView


urlpatterns = [
    # テスト用index
    path('index/', views.index, name='index'),
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
    path('profiles/<int:pk>/avatar/', views.avatar_edit, name='avatar_edit'),
    path('members/new/', views.member_create, name='member_create'),


    # 管理者メニュー
    path('owner/user/', views.admin_user, name='admin_user'),
    path('owner/user/gate/', views.admin_gate, name='admin_gate'),
    path('owner/user/add/', views.member_create, name='family_member_add'),
    path('owner/user/<int:pk>/edit/', views.member_edit, name='family_list_edit'),
    path('owner/user/<int:pk>/pin-reset/', views.pin_reset, name='pin_reset'),
    path('owner/user/<int:pk>/delete/', views.member_delete, name='family_list_delete'),
    path('owner/user/invite/create/', views.invite_create, name='family_invite_create'),

]