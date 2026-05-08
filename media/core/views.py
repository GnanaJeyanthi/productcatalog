# D:\2312040-wfp\productcatalog_project\core\views.py
from django.shortcuts import render

def about_us(request):
    return render(request, 'core/about_us.html')
