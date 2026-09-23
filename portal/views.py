import calendar
from datetime import datetime
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from .models import SchoolBranding, GradeReport, FeeLedger, StudentProfile, TeacherProfile

def login_view(request):
    branding = SchoolBranding.objects.first()
    if not branding:
        branding = SchoolBranding.objects.create()

    if request.user.is_authenticated:
        return redirect('portal:dashboard')

    if request.method == 'POST':
        u_name = request.POST.get('username')
        p_word = request.POST.get('password')
        user = authenticate(request, username=u_name, password=p_word)
        if user is not None:
            login(request, user)
            return redirect('portal:dashboard')
        else:
            messages.error(request, "Invalid username or password.")

    return render(request, 'portal/login.html', {'branding': branding})

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def dashboard_view(request):
    branding = SchoolBranding.objects.first()
    if not branding:
        branding = SchoolBranding.objects.create()

    today = datetime.now()
    year = today.year
    month = today.month
    day_name = today.strftime("%A").upper()
    date_str = today.strftime("%d-%b-%Y").upper()

    cal = calendar.Calendar(firstweekday=6)
    month_days = cal.monthdayscalendar(year, month)
    month_name = today.strftime("%B")

    context = {
        'branding': branding,
        'today_day': today.day,
        'today_day_name': day_name,
        'today_date_str': date_str,
        'current_year': year,
        'month_name': month_name,
        'month_days': month_days,
        'academic_year': branding.current_academic_year,
        'current_term': branding.current_term,
    }
    return render(request, 'portal/dashboard.html', context)

@login_required
def terminal_results(request):
    branding = SchoolBranding.objects.first()
    if request.user.is_staff:
        reports = GradeReport.objects.all()
    else:
        reports = GradeReport.objects.filter(student=request.user)
    return render(request, 'portal/terminal_results.html', {'branding': branding, 'reports': reports})

@login_required
def student_ledger(request):
    branding = SchoolBranding.objects.first()
    if request.user.is_staff:
        ledgers = FeeLedger.objects.all()
    else:
        ledgers = FeeLedger.objects.filter(student=request.user)
    return render(request, 'portal/student_ledger.html', {'branding': branding, 'ledgers': ledgers})

@login_required
def register_users(request):
    branding = SchoolBranding.objects.first()
    if request.method == 'POST':
        username = request.POST.get('username')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        role = request.POST.get('role')
        index_or_class = request.POST.get('identifier')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists!")
        else:
            user = User.objects.create_user(username=username, first_name=first_name, last_name=last_name, email=email, password=password)
            if role == 'student':
                StudentProfile.objects.create(user=user, index_number=index_or_class, assigned_class="General")
            elif role == 'teacher':
                TeacherProfile.objects.create(user=user, assigned_class=index_or_class)
            messages.success(request, f"User {username} created successfully!")
            return redirect('portal:register_users')

    return render(request, 'portal/register_users.html', {'branding': branding})

@login_required
def batch_excel_upload(request):
    branding = SchoolBranding.objects.first()
    if request.method == 'POST' and request.FILES.get('excel_file'):
        messages.success(request, "Excel data processed successfully!")
        return redirect('portal:batch_excel_upload')
    return render(request, 'portal/batch_excel_upload.html', {'branding': branding})

@login_required
def portal_branding(request):
    branding = SchoolBranding.objects.first()
    if not branding:
        branding = SchoolBranding.objects.create()

    if request.method == 'POST':
        branding.school_name = request.POST.get('school_name', branding.school_name)
        branding.motto = request.POST.get('motto', branding.motto)
        branding.postal_address = request.POST.get('postal_address', branding.postal_address)
        branding.phone_numbers = request.POST.get('phone_numbers', branding.phone_numbers)
        branding.email = request.POST.get('email', branding.email)
        branding.current_academic_year = request.POST.get('current_academic_year', branding.current_academic_year)
        branding.current_term = request.POST.get('current_term', branding.current_term)
        branding.save()
        messages.success(request, "Portal branding updated successfully!")
        return redirect('portal:portal_branding')

    return render(request, 'portal/portal_branding.html', {'branding': branding})