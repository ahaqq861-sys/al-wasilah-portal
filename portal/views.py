from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import SchoolBranding, UserProfile

def login_view(request):
    branding = SchoolBranding.objects.first()
    if request.method == 'POST':
        # Handle authentication logic here
        pass
    return render(request, 'login.html', {'branding': branding})

@login_required
def dashboard_view(request):
    branding = SchoolBranding.objects.first()
    profile = getattr(request.user, 'profile', None)
    context = {
        'branding': branding,
        'profile': profile,
    }
    return render(request, 'dashboard.html', context)

def logout_view(request):
    logout(request)
    return redirect('login')