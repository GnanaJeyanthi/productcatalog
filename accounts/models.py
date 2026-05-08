# D:\2312040-wfp\productcatalog_project\accounts\models.py
from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    address = models.TextField()
    district = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    country = models.CharField(max_length=100, default='India')
    is_college_student = models.BooleanField(default=False)
    profile_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"

    def is_college_email(self):
        """Check if the email domain is from a college"""
        from django.conf import settings
        college_domains = getattr(settings, 'COLLEGE_EMAIL_DOMAINS', [])
        email_domain = self.email.split('@')[-1].lower()
        return email_domain in college_domains
