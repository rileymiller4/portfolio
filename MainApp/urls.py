from django.contrib.auth import views as auth_views
from django.urls import path
from . import views

app_name = 'skillswap'

urlpatterns = [
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),

    path('skill/create/', views.skill_create, name='skill_create'),
    path('skill/<int:pk>/', views.skill_detail, name='skill_detail'),
    path('skill/<int:pk>/edit/', views.skill_update, name='skill_update'),
    path('skill/<int:pk>/delete/', views.skill_delete, name='skill_delete'),

    path('skill/<int:pk>/review/', views.add_review, name='add_review'),
    path('skill/<int:pk>/book/', views.create_booking, name='create_booking'),
    path('booking/<int:pk>/approve/', views.approve_booking, name='approve_booking'),
    path('booking/<int:pk>/deny/', views.deny_booking, name='deny_booking'),
    path('booking/<int:pk>/complete/', views.complete_booking, name='complete_booking'),
    path('user/<int:pk>/review/', views.review_user, name='review_user'),

    path('register/', views.register, name='register'),
    path('login/', views.SkillSwapLoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='skillswap:home'), name='logout'),
]