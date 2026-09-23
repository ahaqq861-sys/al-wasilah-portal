import openpyxl
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Sum
from django.contrib import messages
from .models import (
    SchoolBranding, StudentProfile, TeacherProfile, UserProfile, 
    GradeReport, LedgerEntry, AcademicTerm, SchoolDocument, CLASS_LEVEL_CHOICES
)

def login_view(request):
    branding = SchoolBranding.objects.first()
    if request.user.is_authenticated:
        return redirect('portal:dashboard')
    
    if request.method == 'POST':
        u = request.POST.get('username')
        p = request.POST.get('password')
        user = authenticate(request, username=u, password=p)
        if user is not None:
            login(request, user)
            return redirect('portal:dashboard')
        else:
            return render(request, 'login.html', {'branding': branding, 'error': 'Invalid Username or Password'})
            
    return render(request, 'login.html', {'branding': branding})

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def dashboard_view(request):
    branding = SchoolBranding.objects.first()
    user = request.user
    profile = getattr(user, 'profile', None)
    
    student = StudentProfile.objects.filter(user=user).first()
    teacher = TeacherProfile.objects.filter(user=user).first()

    context = {
        'branding': branding,
        'student': student,
        'teacher': teacher,
        'profile': profile,
        'is_admin': user.is_superuser or (profile and profile.role == 'admin'),
        'is_teacher': profile and profile.role == 'teacher',
        'is_student': profile and profile.role == 'student',
    }
    return render(request, 'dashboard.html', context)

@login_required
def register_user_view(request):
    user = request.user
    profile = getattr(user, 'profile', None)
    teacher = TeacherProfile.objects.filter(user=user).first()
    is_admin = user.is_superuser or (profile and profile.role == 'admin')

    if not is_admin and not teacher:
        messages.error(request, "Permission denied.")
        return redirect('portal:dashboard')

    if request.method == 'POST':
        role = request.POST.get('role')
        username = request.POST.get('username')
        password = request.POST.get('password', '123456')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        gender = request.POST.get('gender')
        age = request.POST.get('age', 10)
        class_level = request.POST.get('class_level')

        # Scoping check for Teachers
        if not is_admin and teacher and teacher.class_assigned != class_level:
            messages.error(request, f"You can only register students for {teacher.get_class_assigned_display()}.")
            return redirect('portal:register_user')

        new_user, created = User.objects.get_or_create(
            username=username,
            defaults={'first_name': first_name, 'last_name': last_name, 'email': email}
        )
        if created:
            new_user.set_password(password)
            new_user.save()
            UserProfile.objects.create(user=new_user, role=role, phone=phone, class_assigned=class_level)

        if role == 'student':
            StudentProfile.objects.create(
                user=new_user,
                index_number=username,
                class_level=class_level,
                gender=gender,
                age=age,
                parent_name=request.POST.get('parent_name', ''),
                parent_contact=request.POST.get('parent_contact', ''),
                parent_email=request.POST.get('parent_email', '')
            )
        elif role == 'teacher' and is_admin:
            TeacherProfile.objects.create(
                user=new_user,
                staff_id=username,
                class_assigned=class_level,
                gender=gender,
                age=age
            )

        messages.success(request, f"User '{username}' created successfully!")
        return redirect('portal:dashboard')

    return render(request, 'register.html', {
        'branding': SchoolBranding.objects.first(),
        'class_choices': CLASS_LEVEL_CHOICES,
        'is_admin': is_admin
    })

@login_required
def batch_excel_upload_view(request):
    if request.method == 'POST' and request.FILES.get('excel_file'):
        excel_file = request.FILES['excel_file']
        wb = openpyxl.load_workbook(excel_file)
        worksheet = wb.active

        term = AcademicTerm.objects.filter(is_active=True).first()

        for row in worksheet.iter_rows(min_row=2, values_only=True):
            if not row or not row[0]:
                continue
            index_no, subject_code, subject_name, class_score, exam_score = row[:5]
            student = StudentProfile.objects.filter(index_number=str(index_no)).first()
            if student and term:
                GradeReport.objects.create(
                    student=student,
                    subject_code=str(subject_code),
                    subject_name=str(subject_name),
                    class_score=float(class_score or 0),
                    exam_score=float(exam_score or 0),
                    term=term
                )
        messages.success(request, "Marks batch uploaded successfully!")
        return redirect('portal:results')

    return render(request, 'upload_excel.html', {'branding': SchoolBranding.objects.first()})

@login_required
def school_fees_view(request):
    branding = SchoolBranding.objects.first()
    user = request.user
    profile = getattr(user, 'profile', None)
    is_admin = user.is_superuser or (profile and profile.role == 'admin')
    teacher = TeacherProfile.objects.filter(user=user).first()

    if is_admin:
        students = StudentProfile.objects.all()
    elif teacher:
        students = StudentProfile.objects.filter(class_level=teacher.class_assigned)
    else:
        students = StudentProfile.objects.filter(user=user)

    student = students.first()
    entries = LedgerEntry.objects.filter(student=student).order_by('-date') if student else []

    total_billing = entries.filter(entry_type='BILLING').aggregate(Sum('amount'))['amount__sum'] or 0 if entries else 0
    total_payment = entries.filter(entry_type='PAYMENT').aggregate(Sum('amount'))['amount__sum'] or 0 if entries else 0
    balance = total_billing - total_payment

    return render(request, 'school_fees.html', {
        'branding': branding,
        'student': student,
        'students': students,
        'entries': entries,
        'total_billing': total_billing,
        'total_payment': total_payment,
        'balance': balance,
    })

@login_required
def results_view(request):
    branding = SchoolBranding.objects.first()
    user = request.user
    profile = getattr(user, 'profile', None)
    is_admin = user.is_superuser or (profile and profile.role == 'admin')
    teacher = TeacherProfile.objects.filter(user=user).first()

    if is_admin:
        student = StudentProfile.objects.first()
    elif teacher:
        student = StudentProfile.objects.filter(class_level=teacher.class_assigned).first()
    else:
        student = get_object_or_404(StudentProfile, user=user)

    terms = AcademicTerm.objects.all().order_by('-academic_year')
    results_by_term = []

    if student:
        for term in terms:
            grades = GradeReport.objects.filter(student=student, term=term)
            if grades.exists():
                results_by_term.append({'term': term, 'grades': grades})

    return render(request, 'results.html', {
        'branding': branding,
        'student': student,
        'results_by_term': results_by_term,
    })

@login_required
def admin_branding_view(request):
    user = request.user
    profile = getattr(user, 'profile', None)
    is_admin = user.is_superuser or (profile and profile.role == 'admin')
    teacher = TeacherProfile.objects.filter(user=user).first()

    if not is_admin and not (teacher and request.GET.get('approved') == 'true'):
        messages.error(request, "Branding modifications require Admin approval.")
        return redirect('portal:dashboard')

    branding, _ = SchoolBranding.objects.get_or_create(id=1)

    if request.method == 'POST':
        branding.school_name = request.POST.get('school_name', branding.school_name)
        branding.motto = request.POST.get('motto', branding.motto)
        branding.phone_numbers = request.POST.get('phone_numbers', branding.phone_numbers)
        branding.email = request.POST.get('email', branding.email)
        branding.postal_address = request.POST.get('postal_address', branding.postal_address)
        if request.FILES.get('logo'):
            branding.logo = request.FILES['logo']
        branding.save()
        messages.success(request, "Portal branding updated successfully!")
        return redirect('portal:dashboard')

    return render(request, 'branding.html', {'branding': branding})