# D:\2312040-wfp\productcatalog_project\accounts\urls.py
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),

    # Use Django's built-in Login/Logout views
    path('login/', auth_views.LoginView.as_view(
        template_name='accounts/login.html'),
        name='login'
    ),

    path('logout/', views.logout_view, name='logout'),

    # Profile completion
    path('profile/', views.profile_completion, name='profile_completion'),
    path('my-profile/', views.profile_view, name='profile_view'),
]
