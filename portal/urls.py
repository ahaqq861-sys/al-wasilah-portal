from django.urls import path
from . import views

app_name = 'portal'

urlpatterns = [
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('results/', views.results_view, name='results'),
    path('results/manage/', views.manage_results_view, name='manage_results'),
    path('results/edit/<int:result_id>/', views.edit_result_view, name='edit_result'),
    path('fees/', views.fees_view, name='fees'),
    path('fees/manage/', views.manage_fees_view, name='manage_fees'),
    path('fees/edit/<int:entry_id>/', views.edit_fee_view, name='edit_fee'),
    path('registration/', views.registration_view, name='registration'),
    path('logins/', views.user_logins_view, name='user_logins'),
    path('branding/', views.branding_view, name='branding'),
    path('placeholder/<str:feature>/', views.placeholder_view, name='placeholder'),
    path('logout/', views.logout_view, name='logout'),
]