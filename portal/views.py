from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from .models import SchoolBranding, StudentProfile, GradeReport, LedgerEntry, AcademicTerm

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

@login_required
def dashboard_view(request):
    branding = SchoolBranding.objects.first()
    student = StudentProfile.objects.filter(user=request.user).first()
    context = {
        'branding': branding,
        'student': student,
    }
    return render(request, 'dashboard.html', context)

@login_required
def school_fees_view(request):
    branding = SchoolBranding.objects.first()
    student = get_object_or_404(StudentProfile, user=request.user)
    entries = LedgerEntry.objects.filter(student=student).order_by('-date')
    
    total_billing = entries.filter(entry_type='BILLING').aggregate(Sum('amount'))['amount__sum'] or 0
    total_payment = entries.filter(entry_type='PAYMENT').aggregate(Sum('amount'))['amount__sum'] or 0
    balance = total_billing - total_payment

    context = {
        'branding': branding,
        'student': student,
        'entries': entries,
        'total_billing': total_billing,
        'total_payment': total_payment,
        'balance': balance,
    }
    return render(request, 'school_fees.html', context)

@login_required
def results_view(request):
    branding = SchoolBranding.objects.first()
    student = get_object_or_404(StudentProfile, user=request.user)
    terms = AcademicTerm.objects.all().order_by('-academic_year')
    
    results_by_term = []
    total_credits = 0
    total_points = 0

    grade_point_map = {'A': 4.0, 'B': 3.0, 'C': 2.0, 'D': 1.0, 'F': 0.0}

    for term in terms:
        grades = GradeReport.objects.filter(student=student, term=term)
        if grades.exists():
            term_credits = sum(g.credit_hours for g in grades)
            term_points = sum(grade_point_map.get(g.grade, 0.0) * g.credit_hours for g in grades)
            gpa = round(term_points / term_credits, 2) if term_credits > 0 else 0.0
            
            total_credits += term_credits
            total_points += term_points
            
            results_by_term.append({
                'term': term,
                'grades': grades,
                'gpa': gpa,
            })

    cgpa = round(total_points / total_credits, 2) if total_credits > 0 else 0.0

    context = {
        'branding': branding,
        'student': student,
        'results_by_term': results_by_term,
        'cgpa': cgpa,
        'total_credits': total_credits,
    }
    return render(request, 'results.html', context)

def logout_view(request):
    logout(request)
    return redirect('login')