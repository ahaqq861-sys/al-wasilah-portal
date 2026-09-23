from django.contrib import admin
from django.urls import path, include
from portal.views import login_view, logout_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('portal/', include('portal.urls')),  # Links to portal app URLs
]