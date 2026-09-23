from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from .models import SchoolBranding

def login_view(request):
    branding = SchoolBranding.objects.first()
    
    # If already logged in, go straight to dashboard
    if request.user.is_authenticated:
        return redirect('portal:dashboard')
    
    if request.method == 'POST':
        u = request.POST.get('username')
        p = request.POST.get('password')
        user = authenticate(request, username=u, password=p)
        
        if user is not None:
            login(request, user)
            return redirect('portal:dashboard')  # Ensures proper redirect after login
        else:
            return render(request, 'login.html', {'branding': branding, 'error': 'Invalid Username or Password'})
            
    return render(request, 'login.html', {'branding': branding})