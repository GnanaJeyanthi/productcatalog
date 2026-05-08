from django.shortcuts import redirect
from django.urls import reverse

class ProfileCompletionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Check if user is authenticated and profile is not completed or doesn't exist
        if (request.user.is_authenticated and
            (not hasattr(request.user, 'profile') or
             not request.user.profile.profile_completed) and
            request.path not in [reverse('profile_completion'), reverse('logout'), '/admin/']):
            return redirect('profile_completion')

        response = self.get_response(request)
        return response
