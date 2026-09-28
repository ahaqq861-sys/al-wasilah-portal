from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from datetime import datetime
from .models import PortalBranding, StudentProfile, FeeLedger

def get_branding():
    branding, _ = PortalBranding.objects.get_or_create(id=1)
    return branding

def login_view(request):
    if request.user.is_authenticated:
        return redirect('portal:dashboard')

    if request.method == 'POST':
        username_input = request.POST.get('username')
        password_input = request.POST.get('password')
        user = authenticate(request, username=username_input, password=password_input)

        if user is not None:
            login(request, user)
            return redirect('portal:dashboard')
        else:
            messages.error(request, "Invalid Index Number/Username or Password.")

    context = {
        'branding': get_branding(),
    }
    return render(request, 'portal/login.html', context)

@login_required
def dashboard_view(request):
    profile, _ = StudentProfile.objects.get_or_create(user=request.user)
    context = {
        'branding': get_branding(),
        'profile': profile,
        'today_day_name': datetime.now().strftime('%A'),
        'today_date_str': datetime.now().strftime('%d-%b-%Y'),
        'total_students': StudentProfile.objects.filter(role='student').count(),
        'total_teachers': StudentProfile.objects.filter(role='teacher').count(),
    }
    return render(request, 'portal/dashboard.html', context)

@login_required
def results_view(request):
    profile, _ = StudentProfile.objects.get_or_create(user=request.user)
    context = {
        'branding': get_branding(),
        'profile': profile,
        'results': [],
    }
    return render(request, 'portal/student_results.html', context)

@login_required
def fees_view(request):
    profile, _ = StudentProfile.objects.get_or_create(user=request.user)
    entries = FeeLedger.objects.filter(student=request.user).order_by('-date_recorded')
    context = {
        'branding': get_branding(),
        'profile': profile,
        'entries': entries,
    }
    return render(request, 'portal/student_fees.html', context)

@login_required
def registration_view(request):
    profile, _ = StudentProfile.objects.get_or_create(user=request.user)
    
    if profile.role not in ['admin', 'teacher']:
        messages.error(request, "Permission denied: Only administrators can register users.")
        return redirect('portal:dashboard')

    if request.method == 'POST':
        username = request.POST.get('username')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        role = request.POST.get('role', 'student')
        assigned_class = request.POST.get('assigned_class', 'Primary 1')
        index_number = request.POST.get('index_number', f"AWS/{datetime.now().year}/{User.objects.count()+1:03d}")
        
        if User.objects.filter(username=username).exists():
            messages.error(request, f"User with username/index '{username}' already exists.")
        else:
            new_user = User.objects.create_user(
                username=username,
                first_name=first_name,
                last_name=last_name,
                password='ChangeMe123!'
            )
            new_profile, _ = StudentProfile.objects.get_or_create(user=new_user)
            new_profile.role = role
            new_profile.assigned_class = assigned_class
            new_profile.index_number = index_number
            
            if 'passport_picture' in request.FILES:
                new_profile.passport_picture = request.FILES['passport_picture']
                
            new_profile.save()
            messages.success(request, f"Account successfully created for {first_name} {last_name} ({username}).")
            return redirect('portal:registration')

    registered_users = StudentProfile.objects.select_related('user').all().order_by('-id')
    context = {
        'branding': get_branding(),
        'profile': profile,
        'registered_users': registered_users,
    }
    return render(request, 'portal/registration.html', context)

@login_required
def branding_view(request):
    profile, _ = StudentProfile.objects.get_or_create(user=request.user)
    branding = get_branding()

    if request.method == 'POST':
        branding.school_name = request.POST.get('school_name', branding.school_name)
        branding.tagline_subtext = request.POST.get('tagline_subtext', branding.tagline_subtext)
        branding.primary_color = request.POST.get('primary_color', branding.primary_color)
        branding.contact_email = request.POST.get('contact_email', branding.contact_email)
        branding.contact_phone = request.POST.get('contact_phone', branding.contact_phone)
        branding.address = request.POST.get('address', branding.address)
        branding.footer_text = request.POST.get('footer_text', branding.footer_text)

        if 'logo' in request.FILES:
            branding.logo = request.FILES['logo']

        branding.save()
        messages.success(request, "Portal branding settings updated successfully!")
        return redirect('portal:branding')

    context = {
        'branding': branding,
        'profile': profile,
    }
    return render(request, 'portal/branding.html', context)

@login_required
def placeholder_view(request, feature):
    messages.info(request, f"The '{feature}' feature is currently under active development.")
    return redirect('portal:dashboard')

def logout_view(request):
    logout(request)
    return redirect('portal:login')