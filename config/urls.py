from django.contrib import admin
from django.urls import path, re_path, include
from django.conf import settings
from django.conf.urls.static import static

from dashboard.views import SaleFileGalleryView


urlpatterns = [
    path('admin/', admin.site.urls),
    re_path(r'sale-file/gallery/(?P<slug>[-\w]+)/(?P<unique_url_id>[-\w]+)/', SaleFileGalleryView.as_view(), name='sale_file_gallery'),
    path('__debug__/', include('debug_toolbar.urls')),
    path('dashboard/', include('django.contrib.auth.urls')),
    path('', include('dashboard.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

