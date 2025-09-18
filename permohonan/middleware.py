from django.shortcuts import render
from .models import SiteSettings

class MaintenanceModeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Dapatkan tetapan, atau anggap mod selenggaraan tidak aktif jika tiada
        settings, created = SiteSettings.objects.get_or_create()

        # Semak jika mod selenggaraan aktif DAN pengguna tidak berada di laman admin
        if settings.maintenance_mode and not request.path.startswith('/admin/'):
            # Jika ya, paparkan halaman selenggaraan
            return render(request, 'permohonan/maintenance.html')

        # Jika tidak, teruskan seperti biasa
        response = self.get_response(request)
        return response