# D:\2312040-wfp\productcatalog_project\accounts\views.py
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import ProfileForm
from .models import Profile

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user) # Log the user in immediately
            # Create initial profile with profile_completed=False
            Profile.objects.create(user=user, profile_completed=False)
            return redirect('profile_completion') # Redirect to profile completion
    else:
        form = UserCreationForm()
    return render(request, 'accounts/register.html', {'form': form})

def logout_view(request):
    if request.method == 'POST':
        logout(request)
        return redirect('product_list')
    return render(request, 'accounts/logout.html')

@login_required
def profile_view(request):
    """View for displaying and editing user profile"""
    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        profile = None

    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=profile)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = request.user

            # Check if email is from college domain
            if profile.is_college_email():
                profile.is_college_student = True
                messages.success(request, 'College email detected! You are eligible for student discounts.')
            else:
                profile.is_college_student = False

            profile.profile_completed = True
            profile.save()

            messages.success(request, 'Profile updated successfully!')
            return redirect('profile_view')
    else:
        # Pre-fill form with user data if profile exists
        initial_data = {}
        if profile:
            initial_data = {
                'name': profile.name,
                'email': profile.email,
                'phone': profile.phone,
                'address': profile.address,
                'district': profile.district,
                'state': profile.state,
                'country': profile.country,
            }
        else:
            # Pre-fill with Django user data
            initial_data = {
                'name': request.user.get_full_name() or request.user.username,
                'email': request.user.email,
                'country': 'India',
            }
        form = ProfileForm(initial=initial_data)

    context = {
        'form': form,
        'profile': profile,
        'is_college_student': profile.is_college_student if profile else False,
    }
    return render(request, 'accounts/profile.html', context)

@login_required
def profile_completion(request):
    """View for completing user profile and checking college status"""
    try:
        profile = request.user.profile
        profile_completed = profile.profile_completed
    except Profile.DoesNotExist:
        profile = None
        profile_completed = False

    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=profile)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = request.user

            # Check if email is from college domain
            if profile.is_college_email():
                profile.is_college_student = True
                messages.success(request, 'College email detected! You are eligible for student discounts.')
            else:
                profile.is_college_student = False

            profile.profile_completed = True
            profile.save()

            messages.success(request, 'Profile completed successfully!')
            return redirect('profile_view')
    else:
        # Pre-fill form with user data if profile exists
        initial_data = {}
        if profile:
            initial_data = {
                'name': profile.name,
                'email': profile.email,
                'phone': profile.phone,
                'address': profile.address,
                'district': profile.district,
                'state': profile.state,
                'country': profile.country,
            }
        else:
            # Pre-fill with Django user data
            initial_data = {
                'name': request.user.get_full_name() or request.user.username,
                'email': request.user.email,
                'country': 'India',
            }
        form = ProfileForm(initial=initial_data)

    context = {
        'form': form,
        'profile_completed': profile_completed,
        'is_college_student': profile.is_college_student if profile else False,
    }
    return render(request, 'accounts/profile_completion.html', context)

# Note: We don't need to create views for login
# We will use Django's built-in LoginView in urls.py
