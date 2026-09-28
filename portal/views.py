import secrets
import string
from datetime import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.db.models import Sum
from .models import PortalBranding, StudentProfile, FeeLedger, AcademicResult

def generate_random_password(length=8):
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))

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
            messages.error(request, "Invalid Login Credentials.")

    context = {'branding': get_branding()}
    return render(request, 'portal/login.html', context)

@login_required
def dashboard_view(request):
    profile, _ = StudentProfile.objects.get_or_create(user=request.user)
    
    # Auto-assign admin role to superusers if not already assigned
    if request.user.is_superuser and profile.role != 'admin':
        profile.role = 'admin'
        profile.can_brand_portal = True
        profile.save()

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
def registration_view(request):
    profile, _ = StudentProfile.objects.get_or_create(user=request.user)
    if profile.role not in ['admin', 'teacher'] and not request.user.is_superuser:
        messages.error(request, "Access restricted to Administrators.")
        return redirect('portal:dashboard')

    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        role = request.POST.get('role', 'student')
        assigned_class = request.POST.get('assigned_class', 'Primary 1')
        
        user_count = User.objects.count() + 1
        username = request.POST.get('username') or f"AWS/{datetime.now().year}/{user_count:03d}"
        generated_password = generate_random_password()

        if User.objects.filter(username=username).exists():
            messages.error(request, f"User with ID '{username}' already exists.")
        else:
            new_user = User.objects.create_user(
                username=username,
                first_name=first_name,
                last_name=last_name,
                password=generated_password
            )
            new_profile, _ = StudentProfile.objects.get_or_create(user=new_user)
            new_profile.role = role
            new_profile.assigned_class = assigned_class
            new_profile.index_number = username
            new_profile.generated_password = generated_password
            
            if 'passport_picture' in request.FILES:
                new_profile.passport_picture = request.FILES['passport_picture']
            new_profile.save()

            messages.success(request, f"Account created! ID: {username} | Password: {generated_password}")
            return redirect('portal:registration')

    context = {
        'branding': get_branding(),
        'profile': profile,
        'registered_users': StudentProfile.objects.select_related('user').all().order_by('-id'),
    }
    return render(request, 'portal/registration.html', context)

@login_required
def user_logins_view(request):
    profile, _ = StudentProfile.objects.get_or_create(user=request.user)
    if profile.role not in ['admin', 'teacher'] and not request.user.is_superuser:
        messages.error(request, "Access restricted.")
        return redirect('portal:dashboard')

    context = {
        'branding': get_branding(),
        'profile': profile,
        'profiles': StudentProfile.objects.select_related('user').all().order_by('role', 'user__username'),
    }
    return render(request, 'portal/user_logins.html', context)

@login_required
def results_view(request):
    profile, _ = StudentProfile.objects.get_or_create(user=request.user)
    results = AcademicResult.objects.filter(student=request.user)
    
    class_students = StudentProfile.objects.filter(assigned_class=profile.assigned_class, role='student')
    student_totals = []
    
    for s_prof in class_students:
        tot_score = AcademicResult.objects.filter(student=s_prof.user).aggregate(Sum('total_score'))['total_score__sum'] or 0
        student_totals.append((s_prof.user.id, tot_score))
        
    student_totals.sort(key=lambda x: x[1], reverse=True)
    
    overall_position = "N/A"
    total_in_class = len(student_totals)
    
    for rank, (user_id, score) in enumerate(student_totals, 1):
        if user_id == request.user.id:
            ordinal = lambda n: "%d%s" % (n, "tsnkrh"[n%10==1 and n%100!=11::4] if n%10<4 and not 11<=n%100<=13 else "th")
            overall_position = f"{ordinal(rank)} / {total_in_class}"
            break

    context = {
        'branding': get_branding(),
        'profile': profile,
        'results': results,
        'overall_position': overall_position,
    }
    return render(request, 'portal/student_results.html', context)

@login_required
def manage_results_view(request):
    profile, _ = StudentProfile.objects.get_or_create(user=request.user)
    if profile.role not in ['admin', 'teacher'] and not request.user.is_superuser:
        messages.error(request, "Permission denied.")
        return redirect('portal:dashboard')

    if request.method == 'POST':
        student_id = request.POST.get('student_id')
        subject_name = request.POST.get('subject_name')
        class_score = request.POST.get('class_score', 0)
        exam_score = request.POST.get('exam_score', 0)
        academic_term = request.POST.get('academic_term', 'Term 1')
        position_in_subject = request.POST.get('position_in_subject', '')

        student_user = get_object_or_404(User, id=student_id)
        AcademicResult.objects.create(
            student=student_user,
            subject_name=subject_name,
            class_score=class_score,
            exam_score=exam_score,
            position_in_subject=position_in_subject,
            academic_term=academic_term
        )
        messages.success(request, f"Result added for {student_user.get_full_name() or student_user.username}")
        return redirect('portal:manage_results')

    students = StudentProfile.objects.filter(role='student').select_related('user')
    all_results = AcademicResult.objects.select_related('student').all().order_by('-id')
    context = {
        'branding': get_branding(),
        'profile': profile,
        'students': students,
        'all_results': all_results,
    }
    return render(request, 'portal/manage_results.html', context)

@login_required
def edit_result_view(request, result_id):
    profile, _ = StudentProfile.objects.get_or_create(user=request.user)
    result = get_object_or_404(AcademicResult, id=result_id)

    if request.method == 'POST':
        result.subject_name = request.POST.get('subject_name', result.subject_name)
        result.class_score = request.POST.get('class_score', result.class_score)
        result.exam_score = request.POST.get('exam_score', result.exam_score)
        result.position_in_subject = request.POST.get('position_in_subject', result.position_in_subject)
        result.academic_term = request.POST.get('academic_term', result.academic_term)
        result.save()
        messages.success(request, "Academic result entry updated successfully.")
        return redirect('portal:manage_results')

    context = {
        'branding': get_branding(),
        'profile': profile,
        'result': result,
    }
    return render(request, 'portal/edit_result.html', context)

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
def manage_fees_view(request):
    profile, _ = StudentProfile.objects.get_or_create(user=request.user)
    if profile.role not in ['admin', 'teacher'] and not request.user.is_superuser:
        messages.error(request, "Permission denied.")
        return redirect('portal:dashboard')

    if request.method == 'POST':
        student_id = request.POST.get('student_id')
        title = request.POST.get('title')
        amount_due = request.POST.get('amount_due', 0.00)
        amount_paid = request.POST.get('amount_paid', 0.00)
        academic_year = request.POST.get('academic_year', '2026/2027')

        student_user = get_object_or_404(User, id=student_id)
        FeeLedger.objects.create(
            student=student_user,
            title=title,
            amount_due=amount_due,
            amount_paid=amount_paid,
            academic_year=academic_year
        )
        messages.success(request, f"Fee ledger entry recorded for {student_user.get_full_name() or student_user.username}")
        return redirect('portal:manage_fees')

    students = StudentProfile.objects.filter(role='student').select_related('user')
    all_entries = FeeLedger.objects.select_related('student').all().order_by('-id')
    context = {
        'branding': get_branding(),
        'profile': profile,
        'students': students,
        'all_entries': all_entries,
    }
    return render(request, 'portal/manage_fees.html', context)

@login_required
def edit_fee_view(request, entry_id):
    profile, _ = StudentProfile.objects.get_or_create(user=request.user)
    fee_entry = get_object_or_404(FeeLedger, id=entry_id)

    if request.method == 'POST':
        fee_entry.title = request.POST.get('title', fee_entry.title)
        fee_entry.amount_due = request.POST.get('amount_due', fee_entry.amount_due)
        fee_entry.amount_paid = request.POST.get('amount_paid', fee_entry.amount_paid)
        fee_entry.academic_year = request.POST.get('academic_year', fee_entry.academic_year)
        fee_entry.save()
        messages.success(request, "Fee record updated.")
        return redirect('portal:manage_fees')

    context = {
        'branding': get_branding(),
        'profile': profile,
        'entry': fee_entry,
    }
    return render(request, 'portal/edit_fee.html', context)

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
    messages.info(request, f"The '{feature}' feature is under active development.")
    return redirect('portal:dashboard')

def logout_view(request):
    logout(request)
    return redirect('login')