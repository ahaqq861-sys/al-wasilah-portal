from django.urls import path
from . import views

app_name = 'portal'

urlpatterns = [
    path('', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('change-password/', views.change_password_view, name='change_password'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('academic/results/', views.results_view, name='results'),
    path('registration/', views.registration_view, name='registration'),
    path('fees/', views.fees_view, name='fees'),
    path('branding/', views.branding_view, name='branding'),
]