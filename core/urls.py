from django.contrib import admin
from django.urls import path, include
from portal.views import login_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', login_view, name='login'),  # Named 'login' to fix the NoReverseMatch error
    path('portal/', include('portal.urls')),
]