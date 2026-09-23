from django.urls import path
from . import views

app_name = 'portal'

urlpatterns = [
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('finance/ledger/', views.school_fees_view, name='school_fees'),
    path('academics/results/', views.results_view, name='results'),
]