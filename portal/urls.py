from django.urls import path
from . import views

app_name = 'portal'

urlpatterns = [
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('terminal-results/', views.terminal_results, name='terminal_results'),
    path('student-ledger/', views.student_ledger, name='student_ledger'),
    path('register-users/', views.register_users, name='register_users'),
    path('batch-excel-upload/', views.batch_excel_upload, name='batch_excel_upload'),
    path('portal-branding/', views.portal_branding, name='portal_branding'),
]