from django.urls import path
from .views import (
    dashboard_view, school_fees_view, results_view, 
    register_user_view, batch_excel_upload_view, admin_branding_view
)

app_name = 'portal'

urlpatterns = [
    path('dashboard/', dashboard_view, name='dashboard'),
    path('school-fees/', school_fees_view, name='school_fees'),
    path('results/', results_view, name='results'),
    path('register/', register_user_view, name='register_user'),
    path('upload-excel/', batch_excel_upload_view, name='upload_excel'),
    path('branding/', admin_branding_view, name='admin_branding'),
]