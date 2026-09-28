from django.urls import path
from . import views

app_name = 'portal'

urlpatterns = [
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('results/', views.results_view, name='results'),
    path('fees/', views.fees_view, name='fees'),
    path('registration/', views.registration_view, name='registration'),
    path('user-logins/', views.user_logins_view, name='user_logins'),
    path('manage-results/', views.manage_results_view, name='manage_results'),
    path('edit-result/<int:result_id>/', views.edit_result_view, name='edit_result'),
    path('manage-fees/', views.manage_fees_view, name='manage_fees'),
    path('edit-fee/<int:entry_id>/', views.edit_fee_view, name='edit_fee'),
    path('fee-receipt/<int:entry_id>/', views.fee_receipt_view, name='fee_receipt'),
    path('remarks/', views.manage_remarks_view, name='manage_remarks'),
    path('announcements/', views.announcements_view, name='announcements'),
    path('branding/', views.branding_view, name='branding'),
    path('placeholder/<str:feature>/', views.placeholder_view, name='placeholder'),
    path('logout/', views.logout_view, name='logout'),
]