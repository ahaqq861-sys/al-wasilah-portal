from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from .models import UserProfile, StudentResult, FeeLedgerEntry, PortalBranding


def get_branding():
    branding, _ = PortalBranding.objects.get_or_create(id=1)
    return branding


def login_view(request):
    if request.user.is_authenticated:
        return redirect('portal:dashboard')

    branding = get_branding()

    if request.method == 'POST':
        identifier = request.POST.get('username', '').strip()
        password_input = request.POST.get('password', '')

        user = authenticate(request, username=identifier, password=password_input)

        if user is None:
            profile = UserProfile.objects.filter(index_number__iexact=identifier).first()
            if profile:
                user = authenticate(request, username=profile.user.username, password=password_input)

        if user is not None:
            login(request, user)
            
            # Safe Profile Lookup / Auto-creation to prevent RelatedObjectDoesNotExist
            profile, created = UserProfile.objects.get_or_create(
                user=user,
                defaults={
                    'role': 'admin' if user.is_superuser else 'student',
                    'index_number': user.username,
                    'must_change_password': False if user.is_superuser else True
                }
            )

            if profile.must_change_password:
                return redirect('portal:change_password')
            return redirect('portal:dashboard')
        else:
            messages.error(request, "Invalid username/ID or password. Please try again.")

    return render(request, 'portal/login.html', {'branding': branding})


@login_required
def change_password_view(request):
    branding = get_branding()
    if request.method == 'POST':
        new_pass = request.POST.get('new_password')
        confirm_pass = request.POST.get('confirm_password')

        if new_pass == '123456':
            messages.error(request, "New password cannot be the default password '123456'.")
        elif new_pass == confirm_pass:
            request.user.set_password(new_pass)
            request.user.save()
            profile = request.user.profile
            profile.must_change_password = False
            profile.save()
            update_session_auth_hash(request, request.user)
            messages.success(request, "Password updated successfully!")
            return redirect('portal:dashboard')
        else:
            messages.error(request, "Passwords do not match!")

    return render(request, 'portal/change_password.html', {'branding': branding})


@login_required
def logout_view(request):
    logout(request)
    return redirect('portal:login')


@login_required
def dashboard_view(request):
    profile = request.user.profile
    branding = get_branding()

    context = {
        'profile': profile,
        'branding': branding,
    }

    if profile.role == 'admin':
        context['total_students'] = UserProfile.objects.filter(role='student').count()
        context['total_teachers'] = UserProfile.objects.filter(role='teacher').count()
    elif profile.role == 'teacher':
        context['class_students'] = UserProfile.objects.filter(role='student', assigned_class=profile.assigned_class)
    elif profile.role == 'student':
        context['results'] = StudentResult.objects.filter(student=profile)
        context['fee_entries'] = FeeLedgerEntry.objects.filter(student=profile)

    return render(request, 'portal/dashboard.html', context)


@login_required
def results_view(request):
    profile = request.user.profile
    branding = get_branding()

    if profile.role == 'student':
        results = StudentResult.objects.filter(student=profile)
        return render(request, 'portal/student_results.html', {'results': results, 'branding': branding, 'profile': profile})

    if profile.role == 'teacher':
        students = UserProfile.objects.filter(role='student', assigned_class=profile.assigned_class)
    else:
        selected_class = request.GET.get('class_filter', '')
        if selected_class:
            students = UserProfile.objects.filter(role='student', assigned_class=selected_class)
        else:
            students = UserProfile.objects.filter(role='student')

    if request.method == 'POST':
        student_id = request.POST.get('student_id')
        subject = request.POST.get('subject')
        class_score = float(request.POST.get('class_score', 0))
        exam_score = float(request.POST.get('exam_score', 0))
        academic_term = request.POST.get('academic_term', 'Term 1')
        academic_year = request.POST.get('academic_year', '2026/2027')

        target_student = get_object_or_404(UserProfile, id=student_id)
        
        StudentResult.objects.create(
            student=target_student,
            subject=subject,
            class_name=target_student.assigned_class,
            class_score=class_score,
            exam_score=exam_score,
            academic_term=academic_term,
            academic_year=academic_year
        )
        messages.success(request, f"Result added for {target_student.user.get_full_name()}")
        return redirect('portal:results')

    results = StudentResult.objects.filter(student__in=students)
    return render(request, 'portal/manage_results.html', {
        'students': students,
        'results': results,
        'branding': branding,
        'profile': profile
    })


@login_required
def registration_view(request):
    profile = request.user.profile
    branding = get_branding()

    if profile.role not in ['admin', 'teacher']:
        messages.error(request, "Access Denied.")
        return redirect('portal:dashboard')

    if request.method == 'POST':
        username = request.POST.get('username')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        role = request.POST.get('role', 'student') if profile.role == 'admin' else 'student'
        assigned_class = request.POST.get('assigned_class') if profile.role == 'admin' else profile.assigned_class
        index_number = request.POST.get('index_number')
        age = request.POST.get('age')
        gender = request.POST.get('gender')
        disability_status = request.POST.get('disability_status', 'None')
        can_brand = True if request.POST.get('can_brand_portal') == 'on' else False

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists!")
        else:
            user = User.objects.create_user(
                username=username,
                password='123456',
                first_name=first_name,
                last_name=last_name
            )
            
            user_profile = UserProfile.objects.get_or_create(
                user=user,
                defaults={
                    'role': role,
                    'index_number': index_number or username,
                    'assigned_class': assigned_class,
                    'age': int(age) if age else None,
                    'gender': gender,
                    'disability_status': disability_status,
                    'can_brand_portal': can_brand,
                    'must_change_password': True
                }
            )[0]

            if 'passport_picture' in request.FILES:
                user_profile.passport_picture = request.FILES['passport_picture']
                user_profile.save()

            messages.success(request, f"Registered successfully! Username: {username} | Default Password: 123456")
            return redirect('portal:registration')

    if profile.role == 'teacher':
        registered_users = UserProfile.objects.filter(assigned_class=profile.assigned_class)
    else:
        registered_users = UserProfile.objects.all()

    return render(request, 'portal/registration.html', {
        'registered_users': registered_users,
        'branding': branding,
        'profile': profile
    })


@login_required
def fees_view(request):
    profile = request.user.profile
    branding = get_branding()

    if profile.role == 'student':
        entries = FeeLedgerEntry.objects.filter(student=profile)
        return render(request, 'portal/student_fees.html', {'entries': entries, 'branding': branding, 'profile': profile})

    if profile.role == 'teacher':
        students = UserProfile.objects.filter(role='student', assigned_class=profile.assigned_class)
    else:
        selected_class = request.GET.get('class_filter', '')
        if selected_class:
            students = UserProfile.objects.filter(role='student', assigned_class=selected_class)
        else:
            students = UserProfile.objects.filter(role='student')

    if request.method == 'POST':
        student_id = request.POST.get('student_id')
        title = request.POST.get('title', 'School Fees')
        amount_due = float(request.POST.get('amount_due', 0))
        amount_paid = float(request.POST.get('amount_paid', 0))

        target_student = get_object_or_404(UserProfile, id=student_id)

        FeeLedgerEntry.objects.create(
            student=target_student,
            title=title,
            amount_due=amount_due,
            amount_paid=amount_paid,
            recorded_by=request.user
        )
        messages.success(request, f"Fee payment recorded for {target_student.user.get_full_name()}")
        return redirect('portal:fees')

    fee_entries = FeeLedgerEntry.objects.filter(student__in=students)
    return render(request, 'portal/manage_fees.html', {
        'students': students,
        'entries': fee_entries,
        'branding': branding,
        'profile': profile
    })


@login_required
def branding_view(request):
    profile = request.user.profile
    branding = get_branding()

    if profile.role != 'admin' and not profile.can_brand_portal:
        messages.error(request, "Permission denied to edit portal branding.")
        return redirect('portal:dashboard')

    if request.method == 'POST':
        branding.school_name = request.POST.get('school_name', branding.school_name)
        branding.contact_email = request.POST.get('contact_email', branding.contact_email)
        branding.contact_phone = request.POST.get('contact_phone', branding.contact_phone)
        branding.address = request.POST.get('address', branding.address)

        if 'logo' in request.FILES:
            branding.logo = request.FILES['logo']

        branding.save()
        messages.success(request, "Portal branding updated successfully!")
        return redirect('portal:branding')

    return render(request, 'portal/branding.html', {'branding': branding, 'profile': profile})