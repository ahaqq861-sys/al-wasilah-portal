from django.urls import path
from . import views

app_name = 'portal'

urlpatterns = [
    path('', views.login_view, name='login'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('change-password/', views.change_password_view, name='change_password'),
    path('results/', views.results_view, name='results'),
    path('registration/', views.registration_view, name='registration'),
    path('fees/', views.fees_view, name='fees'),
    path('branding/', views.branding_view, name='branding'),
    
    # Placeholder route for features under development
    path('placeholder/<str:feature_name>/', views.placeholder_view, name='placeholder'),
]