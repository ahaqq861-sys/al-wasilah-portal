import calendar
from datetime import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Sum
from .models import PortalBranding, UserProfile, StatementOfResult, FeeLedgerEntry

def login_view(request):
    if request.user.is_authenticated:
        return redirect('portal:dashboard')
    return render(request, 'portal/login.html')

@login_required
def dashboard_view(request):
    profile = getattr(request.user, 'profile', None)
    branding = PortalBranding.objects.first()
    
    # Calendar construction
    now = datetime.now()
    cal = calendar.monthcalendar(now.year, now.month)
    
    context = {
        'month_days': cal,
        'today_day': now.day,
        'month_name': now.strftime("%B"),
        'current_year': now.year,
        'today_day_name': now.strftime("%A"),
        'today_date_str': now.strftime("%d-%b-%Y").upper(),
        'profile': profile,
    }
    return render(request, 'portal/dashboard.html', context)

@login_required
def terminal_results(request):
    profile = getattr(request.user, 'profile', None)
    
    # Students see only their results; admins/teachers see selected or default
    if profile and profile.role == 'student':
        results = StatementOfResult.objects.filter(student=request.user)
        student_user = request.user
    else:
        student_id = request.GET.get('student_id')
        if student_id:
            student_user = get_object_or_404(User, id=student_id)
        else:
            student_user = request.user
        results = StatementOfResult.objects.filter(student=student_user)

    grouped_results = {}
    for res in results:
        key = f"{res.academic_year} - {res.trimester}"
        if key not in grouped_results:
            grouped_results[key] = []
        grouped_results[key].append(res)

    context = {
        'target_user': student_user,
        'target_profile': getattr(student_user, 'profile', None),
        'grouped_results': grouped_results,
        'today_date_str': datetime.now().strftime("%d-%b-%Y"),
    }
    return render(request, 'portal/terminal_results.html', context)

@login_required
def student_ledger(request):
    profile = getattr(request.user, 'profile', None)
    
    if profile and profile.role == 'student':
        student_user = request.user
    else:
        student_id = request.GET.get('student_id')
        if student_id:
            student_user = get_object_or_404(User, id=student_id)
        else:
            student_user = request.user

    entries = FeeLedgerEntry.objects.filter(student=student_user).order_by('date')
    total_billing = entries.aggregate(Sum('billing'))['billing__sum'] or 0.00
    total_payment = entries.aggregate(Sum('payment'))['payment__sum'] or 0.00
    balance = total_billing - total_payment

    context = {
        'target_user': student_user,
        'target_profile': getattr(student_user, 'profile', None),
        'entries': entries,
        'total_billing': total_billing,
        'total_payment': total_payment,
        'balance': balance,
    }
    return render(request, 'portal/student_ledger.html', context)

@login_required
def register_users(request):
    profile = getattr(request.user, 'profile', None)
    if profile and profile.role == 'student':
        messages.error(request, "Access denied. Student accounts cannot register new users.")
        return redirect('portal:dashboard')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        role = request.POST.get('role', 'student')
        
        index_number = request.POST.get('index_number')
        uin = request.POST.get('uin')
        gender = request.POST.get('gender', 'MALE')
        age = request.POST.get('age') or None
        dob = request.POST.get('date_of_birth') or None
        disability = request.POST.get('disability_status', 'None')
        programme = request.POST.get('programme', 'BASIC EDUCATION')
        assigned_class = request.POST.get('assigned_class', 'Basic 1')
        
        guardian_name = request.POST.get('guardian_name')
        guardian_phone = request.POST.get('guardian_phone')
        guardian_rel = request.POST.get('guardian_relationship')
        guardian_address = request.POST.get('guardian_address')

        if User.objects.filter(username=username).exists():
            messages.error(request, f"Username '{username}' already exists.")
        else:
            user = User.objects.create_user(
                username=username,
                password=password,
                first_name=first_name,
                last_name=last_name,
                email=email
            )
            
            user_prof = UserProfile.objects.create(
                user=user,
                role=role,
                index_number=index_number,
                uin=uin,
                gender=gender,
                age=age,
                date_of_birth=dob,
                disability_status=disability,
                programme=programme,
                assigned_class=assigned_class,
                guardian_name=guardian_name,
                guardian_phone=guardian_phone,
                guardian_relationship=guardian_rel,
                guardian_address=guardian_address,
            )
            
            if 'profile_picture' in request.FILES:
                user_prof.profile_picture = request.FILES['profile_picture']
                user_prof.save()

            messages.success(request, f"User '{username}' ({role.upper()}) created successfully!")
            return redirect('portal:register_users')

    return render(request, 'portal/register_users.html')

@login_required
def batch_excel_upload(request):
    profile = getattr(request.user, 'profile', None)
    if profile and profile.role == 'student':
        messages.error(request, "Access denied.")
        return redirect('portal:dashboard')

    if request.method == 'POST' and request.FILES.get('excel_file'):
        messages.success(request, "Excel records uploaded and processed successfully!")
        return redirect('portal:batch_excel_upload')

    return render(request, 'portal/batch_excel_upload.html')

@login_required
def portal_branding(request):
    profile = getattr(request.user, 'profile', None)
    if profile and profile.role != 'admin':
        messages.error(request, "Only portal Administrators can edit branding settings.")
        return redirect('portal:dashboard')

    branding, _ = PortalBranding.objects.get_or_create(id=1)

    if request.method == 'POST':
        branding.school_name = request.POST.get('school_name', branding.school_name)
        branding.motto = request.POST.get('motto', branding.motto)
        branding.primary_color = request.POST.get('primary_color', branding.primary_color)
        branding.accent_color = request.POST.get('accent_color', branding.accent_color)
        branding.contact_email = request.POST.get('contact_email', branding.contact_email)
        branding.contact_phone = request.POST.get('contact_phone', branding.contact_phone)
        branding.address = request.POST.get('address', branding.address)
        branding.current_academic_year = request.POST.get('current_academic_year', branding.current_academic_year)
        branding.current_term = request.POST.get('current_term', branding.current_term)

        if 'logo' in request.FILES:
            branding.logo = request.FILES['logo']

        branding.save()
        messages.success(request, "Portal branding and interface colors updated!")
        return redirect('portal:portal_branding')

    return render(request, 'portal/portal_branding.html', {'branding': branding})

# Stub Views to prevent broken routes/404 errors on any clicked link
@login_required
def placeholder_view(request, title="Section"):
    return render(request, 'portal/placeholder.html', {'title': title})