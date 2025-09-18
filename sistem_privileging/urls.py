from django.contrib import admin
from django.urls import path, include
# Tambah import di bawah
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('permohonan.urls')),
]

# Tambah baris ini di bahagian bawah
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)