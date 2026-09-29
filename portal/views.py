from datetime import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib import messages
from django.db.models import Sum
from .models import PortalBranding, StudentProfile, FeeLedger, AcademicResult, Announcement, TimetableEntry

def get_branding():
    # Force query to ensure cached/fresh record is returned instantly
    branding, created = PortalBranding.objects.get_or_create(id=1)
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
            profile, _ = StudentProfile.objects.get_or_create(user=user)
            if profile.must_change_password:
                messages.warning(request, "Please change your default password to proceed.")
                return redirect('portal:change_password')
            return redirect('portal:dashboard')
        else:
            messages.error(request, "Invalid Login Credentials. Default password is 123456.")

    context = {'branding': get_branding()}
    return render(request, 'portal/login.html', context)

def password_recovery_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        try:
            target_user = User.objects.get(username=username)
            target_profile, _ = StudentProfile.objects.get_or_create(user=target_user)
            target_user.set_password('123456')
            target_user.save()
            target_profile.must_change_password = True
            target_profile.save()
            messages.success(request, f"Password for account '{username}' has been reset to default: 123456.")
            return redirect('login')
        except User.DoesNotExist:
            messages.error(request, "Account username not found in the system.")
    
    context = {'branding': get_branding()}
    return render(request, 'portal/password_recovery.html', context)

@login_required
def change_password_view(request):
    profile, _ = StudentProfile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        if new_password and new_password == confirm_password:
            request.user.set_password(new_password)
            request.user.save()
            profile.must_change_password = False
            profile.save()
            update_session_auth_hash(request, request.user)
            messages.success(request, "Password updated successfully!")
            return redirect('portal:dashboard')
        else:
            messages.error(request, "Passwords do not match.")

    context = {'branding': get_branding(), 'profile': profile}
    return render(request, 'portal/change_password.html', context)

@login_required
def dashboard_view(request):
    profile, _ = StudentProfile.objects.get_or_create(user=request.user)
    
    if profile.must_change_password:
        return redirect('portal:change_password')

    if request.user.is_superuser and profile.role != 'admin':
        profile.role = 'admin'
        profile.can_brand_portal = True
        profile.save()

    announcements = Announcement.objects.all().order_by('-date_posted')[:5]
    today_name = datetime.now().strftime('%A')
    today_schedule = TimetableEntry.objects.filter(day_of_week=today_name, class_name=profile.assigned_class)

    if profile.role == 'admin':
        stat_1_title = "TOTAL STUDENTS"
        stat_1_val = StudentProfile.objects.filter(role='student').count()
        stat_2_title = "TOTAL TEACHERS"
        stat_2_val = StudentProfile.objects.filter(role='teacher').count()
    elif profile.role == 'teacher':
        stat_1_title = f"STUDENTS ({profile.assigned_class})"
        stat_1_val = StudentProfile.objects.filter(role='student', assigned_class=profile.assigned_class).count()
        stat_2_title = "ASSIGNED CLASS"
        stat_2_val = profile.assigned_class
    else:
        stat_1_title = "ENROLLED SUBJECTS"
        stat_1_val = AcademicResult.objects.filter(student=request.user).count()
        stat_2_title = "ATTENDANCE"
        stat_2_val = f"{profile.days_present} / {profile.total_school_days} Days"

    context = {
        'branding': get_branding(),
        'profile': profile,
        'today_day_name': today_name,
        'today_date_str': datetime.now().strftime('%d-%b-%Y'),
        'stat_1_title': stat_1_title,
        'stat_1_val': stat_1_val,
        'stat_2_title': stat_2_title,
        'stat_2_val': stat_2_val,
        'announcements': announcements,
        'today_schedule': today_schedule,
    }
    return render(request, 'portal/dashboard.html', context)

@login_required
def admin_oversight_view(request):
    profile, _ = StudentProfile.objects.get_or_create(user=request.user)
    if profile.role not in ['admin', 'teacher'] and not request.user.is_superuser:
        return redirect('portal:dashboard')

    students_query = StudentProfile.objects.filter(role='student')
    
    # If user is a teacher, restrict oversight strictly to their assigned class
    if profile.role == 'teacher' and not request.user.is_superuser:
        selected_class = profile.assigned_class
        students_query = students_query.filter(assigned_class=selected_class)
    else:
        selected_class = request.GET.get('class_name', 'All')
        if selected_class != 'All':
            students_query = students_query.filter(assigned_class=selected_class)

    student_data = []
    for s in students_query:
        res = AcademicResult.objects.filter(student=s.user)
        fee = FeeLedger.objects.filter(student=s.user)
        total_due = fee.aggregate(Sum('amount_due'))['amount_due__sum'] or 0
        total_paid = fee.aggregate(Sum('amount_paid'))['amount_paid__sum'] or 0
        student_data.append({
            'profile': s,
            'results': res,
            'total_due': total_due,
            'total_paid': total_paid,
            'balance': total_due - total_paid
        })

    context = {
        'branding': get_branding(),
        'profile': profile,
        'student_data': student_data,
        'selected_class': selected_class,
    }
    return render(request, 'portal/admin_oversight.html', context)

@login_required
def timetable_view(request):
    profile, _ = StudentProfile.objects.get_or_create(user=request.user)
    entries = TimetableEntry.objects.filter(class_name=profile.assigned_class).order_by('day_of_week', 'period_time')
    
    if request.method == 'POST' and (profile.role in ['admin', 'teacher'] or request.user.is_superuser):
        TimetableEntry.objects.create(
            class_name=request.POST.get('class_name'),
            day_of_week=request.POST.get('day_of_week'),
            period_time=request.POST.get('period_time'),
            subject_name=request.POST.get('subject_name'),
            teacher_name=request.POST.get('teacher_name'),
            venue=request.POST.get('venue')
        )
        messages.success(request, "Timetable period added successfully!")
        return redirect('portal:timetable')

    context = {'branding': get_branding(), 'profile': profile, 'entries': entries}
    return render(request, 'portal/timetable.html', context)

@login_required
def registration_view(request):
    profile, _ = StudentProfile.objects.get_or_create(user=request.user)
    if profile.role not in ['admin', 'teacher'] and not request.user.is_superuser:
        return redirect('portal:dashboard')

    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        role = request.POST.get('role', 'student')
        assigned_class = request.POST.get('assigned_class', 'Primary 1')
        username = request.POST.get('username') or f"AWS/{datetime.now().year}/{User.objects.count()+1:03d}"

        if User.objects.filter(username=username).exists():
            messages.error(request, f"User ID '{username}' already exists.")
        else:
            new_user = User.objects.create_user(username=username, first_name=first_name, last_name=last_name, password='123456')
            new_profile, _ = StudentProfile.objects.get_or_create(user=new_user)
            new_profile.role = role
            new_profile.assigned_class = assigned_class
            new_profile.index_number = username
            new_profile.generated_password = '123456'
            new_profile.must_change_password = True
            new_profile.phone_number = request.POST.get('phone_number')
            new_profile.address = request.POST.get('address')

            if role == 'student':
                new_profile.guardian_name = request.POST.get('guardian_name')
                new_profile.guardian_phone = request.POST.get('guardian_phone')
                new_profile.guardian_address = request.POST.get('guardian_address')
                if 'passport_picture' in request.FILES:
                    new_profile.passport_picture = request.FILES['passport_picture']
                    
            new_profile.save()

            messages.success(request, f"Account created! ID: {username} | Default Password: 123456")
            return redirect('portal:registration')

    context = {'branding': get_branding(), 'profile': profile, 'registered_users': StudentProfile.objects.select_related('user').all().order_by('-id')}
    return render(request, 'portal/registration.html', context)

@login_required
def user_logins_view(request):
    profile, _ = StudentProfile.objects.get_or_create(user=request.user)
    if profile.role not in ['admin', 'teacher'] and not request.user.is_superuser:
        return redirect('portal:dashboard')
    context = {'branding': get_branding(), 'profile': profile, 'profiles': StudentProfile.objects.select_related('user').all()}
    return render(request, 'portal/user_logins.html', context)

@login_required
def results_view(request):
    profile, _ = StudentProfile.objects.get_or_create(user=request.user)
    results = AcademicResult.objects.filter(student=request.user)
    context = {'branding': get_branding(), 'profile': profile, 'results': results, 'overall_position': '1st / Class'}
    return render(request, 'portal/student_results.html', context)

@login_required
def manage_results_view(request):
    profile, _ = StudentProfile.objects.get_or_create(user=request.user)
    if profile.role not in ['admin', 'teacher'] and not request.user.is_superuser:
        return redirect('portal:dashboard')
    if request.method == 'POST':
        AcademicResult.objects.create(
            student=get_object_or_404(User, id=request.POST.get('student_id')),
            subject_name=request.POST.get('subject_name'),
            class_score=request.POST.get('class_score', 0),
            exam_score=request.POST.get('exam_score', 0),
            academic_term=request.POST.get('academic_term', 'Term 1')
        )
        messages.success(request, "Result recorded successfully.")
        return redirect('portal:manage_results')
    context = {'branding': get_branding(), 'profile': profile, 'students': StudentProfile.objects.filter(role='student'), 'all_results': AcademicResult.objects.all()}
    return render(request, 'portal/manage_results.html', context)

@login_required
def edit_result_view(request, result_id):
    result = get_object_or_404(AcademicResult, id=result_id)
    if request.method == 'POST':
        result.subject_name = request.POST.get('subject_name')
        result.class_score = request.POST.get('class_score')
        result.exam_score = request.POST.get('exam_score')
        result.save()
        return redirect('portal:manage_results')
    context = {'branding': get_branding(), 'result': result}
    return render(request, 'portal/edit_result.html', context)

@login_required
def manage_remarks_view(request):
    profile, _ = StudentProfile.objects.get_or_create(user=request.user)
    if profile.role not in ['admin', 'teacher'] and not request.user.is_superuser:
        return redirect('portal:dashboard')
    if request.method == 'POST':
        tp = get_object_or_404(StudentProfile, user_id=request.POST.get('student_id'))
        tp.days_present = request.POST.get('days_present', 0)
        tp.conduct_rating = request.POST.get('conduct_rating', 'GOOD')
        tp.teacher_remarks = request.POST.get('teacher_remarks', '')
        tp.save()
        messages.success(request, "Remarks updated.")
        return redirect('portal:manage_remarks')
    context = {'branding': get_branding(), 'students': StudentProfile.objects.filter(role='student')}
    return render(request, 'portal/manage_remarks.html', context)

@login_required
def fees_view(request):
    profile, _ = StudentProfile.objects.get_or_create(user=request.user)
    entries = FeeLedger.objects.filter(student=request.user)
    context = {
        'branding': get_branding(), 'profile': profile, 'entries': entries,
        'total_due': entries.aggregate(Sum('amount_due'))['amount_due__sum'] or 0,
        'total_paid': entries.aggregate(Sum('amount_paid'))['amount_paid__sum'] or 0,
    }
    return render(request, 'portal/student_fees.html', context)

@login_required
def manage_fees_view(request):
    profile, _ = StudentProfile.objects.get_or_create(user=request.user)
    if profile.role not in ['admin', 'teacher'] and not request.user.is_superuser:
        return redirect('portal:dashboard')
    if request.method == 'POST':
        FeeLedger.objects.create(
            student=get_object_or_404(User, id=request.POST.get('student_id')),
            title=request.POST.get('title'),
            amount_due=request.POST.get('amount_due', 0),
            amount_paid=request.POST.get('amount_paid', 0)
        )
        messages.success(request, "Fee entry added.")
        return redirect('portal:manage_fees')
    context = {'branding': get_branding(), 'students': StudentProfile.objects.filter(role='student'), 'all_entries': FeeLedger.objects.all()}
    return render(request, 'portal/manage_fees.html', context)

@login_required
def edit_fee_view(request, entry_id):
    entry = get_object_or_404(FeeLedger, id=entry_id)
    if request.method == 'POST':
        entry.title = request.POST.get('title')
        entry.amount_due = request.POST.get('amount_due')
        entry.amount_paid = request.POST.get('amount_paid')
        entry.save()
        return redirect('portal:manage_fees')
    context = {'branding': get_branding(), 'entry': entry}
    return render(request, 'portal/edit_fee.html', context)

@login_required
def fee_receipt_view(request, entry_id):
    context = {'branding': get_branding(), 'entry': get_object_or_404(FeeLedger, id=entry_id)}
    return render(request, 'portal/fee_receipt.html', context)

@login_required
def announcements_view(request):
    profile, _ = StudentProfile.objects.get_or_create(user=request.user)
    if request.method == 'POST' and (profile.role in ['admin', 'teacher'] or request.user.is_superuser):
        Announcement.objects.create(title=request.POST.get('title'), content=request.POST.get('content'))
        messages.success(request, "Announcement posted.")
        return redirect('portal:announcements')
    context = {'branding': get_branding(), 'announcements': Announcement.objects.all()}
    return render(request, 'portal/announcements.html', context)

@login_required
def branding_view(request):
    profile, _ = StudentProfile.objects.get_or_create(user=request.user)
    if profile.role != 'admin' and not request.user.is_superuser:
        return redirect('portal:dashboard')
        
    branding = get_branding()
    if request.method == 'POST':
        branding.school_name = request.POST.get('school_name', branding.school_name)
        branding.tagline_subtext = request.POST.get('tagline_subtext', branding.tagline_subtext)
        branding.primary_color = request.POST.get('primary_color', branding.primary_color)
        branding.secondary_color = request.POST.get('secondary_color', branding.secondary_color)
        branding.sidebar_color = request.POST.get('sidebar_color', branding.sidebar_color)
        branding.contact_phone = request.POST.get('contact_phone', branding.contact_phone)
        branding.contact_email = request.POST.get('contact_email', branding.contact_email)
        branding.address = request.POST.get('address', branding.address)
        if 'logo' in request.FILES: branding.logo = request.FILES['logo']
        if 'login_background' in request.FILES: branding.login_background = request.FILES['login_background']
        branding.save()
        messages.success(request, "Branding and theme settings updated successfully!")
        return redirect('portal:branding')
        
    context = {'branding': branding, 'profile': profile}
    return render(request, 'portal/branding.html', context)

def logout_view(request):
    logout(request)
    return redirect('login')