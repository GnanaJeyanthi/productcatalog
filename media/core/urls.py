# D:\2312040-wfp\productcatalog_project\core\urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('about-us/', views.about_us, name='about_us'),
]
