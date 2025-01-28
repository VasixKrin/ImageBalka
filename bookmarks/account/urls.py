from django.contrib.auth import views as auth_views
from django.urls import path, include
from . import views


urlpatterns = [
    path('', include('django.contrib.auth.urls')),
    path('', views.dashboard, name='dashboard'),
    path('register/', views.register, name='register'),
    path('edit/', views.edit, name='edit'),
    path('users/', views.user_list, name='users_list'),
    path('users/follow/', views.user_follow, name='user_follow'),
    path('user/<username>/', views.user_detail, name='user_detail')
]
