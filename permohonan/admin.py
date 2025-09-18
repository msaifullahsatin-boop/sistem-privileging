from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import (
    Permohonan, Kelayakan, ProsedurDimohon, 
    Jawatan, Jabatan, ProsedurPilihan, UserProfile, SiteSettings, Gred # Tambah Gred
)

# ... (UserProfileInline & UserAdmin tidak berubah) ...
class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profil Pengguna (Jabatan)'
class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

# ... (Kelas-kelas admin lain tidak berubah) ...
class PermohonanAdmin(admin.ModelAdmin):
    list_display = ('nama_pemohon', 'jabatan', 'tarikh_borang_dihantar', 'status_sokongan_kj', 'keputusan_jawatanankuasa')
    search_fields = ['nama_pemohon', 'no_kp']
    list_filter = ('status_sokongan_kj', 'keputusan_jawatanankuasa', 'jabatan')
class JabatanAdmin(admin.ModelAdmin):
    list_display = ('nama',)
    search_fields = ['nama']
class JawatanAdmin(admin.ModelAdmin):
    list_display = ('nama',)
    search_fields = ['nama']
class ProsedurPilihanAdmin(admin.ModelAdmin):
    list_display = ('nama',)
    search_fields = ['nama']

# --- KELAS ADMIN BARU DI SINI ---
class GredAdmin(admin.ModelAdmin):
    list_display = ('nama',)
    search_fields = ['nama']

# ... (Pendaftaran model) ...
admin.site.register(Permohonan, PermohonanAdmin)
admin.site.register(Kelayakan)
admin.site.register(ProsedurDimohon)
admin.site.register(Jawatan, JawatanAdmin)
admin.site.register(Jabatan, JabatanAdmin)
admin.site.register(ProsedurPilihan, ProsedurPilihanAdmin)
admin.site.register(UserProfile)
admin.site.register(SiteSettings)
admin.site.register(Gred, GredAdmin) # Daftar Gred di sini