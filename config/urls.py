from django.contrib import admin
from django.urls import path, include


urlpatterns = [
    path('admin/', admin.site.urls),
    path('dashboard/', include('django.contrib.auth.urls')),
    path('', include('dashboard.urls')),
]

