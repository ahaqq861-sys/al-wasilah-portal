from django.urls import path
from . import views

app_name = 'portal'

urlpatterns = [
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('results/', views.results_view, name='results'),
    path('fees/', views.fees_view, name='fees'),
    path('registration/', views.registration_view, name='registration'),
    path('branding/', views.branding_view, name='branding'),
    path('placeholder/<str:feature>/', views.placeholder_view, name='placeholder'),
    path('logout/', views.logout_view, name='logout'),
]