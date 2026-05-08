# D:\2312040-wfp\productcatalog_project\productcatalog\urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings # <-- Import
from django.conf.urls.static import static # <-- Import

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('store.urls')), # <-- Add this line
    path('accounts/', include('accounts.urls')), # Adds 'accounts/login', etc.
    # path('admin/', include('store.admin.admin_site.urls')),  # Custom admin site

]

# Add this for serving media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
