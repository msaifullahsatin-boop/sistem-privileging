from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import (
    Permohonan, Kelayakan, Jawatan, Gred, Jabatan, 
    ProsedurPilihan, UserProfile, SiteSettings,
    CoreProcedure, SpecialisedProcedure, AdditionProcedure, ReductionProcedure
)

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profil Pengguna (Jabatan)'

class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)

admin.site.unregister(User)
admin.site.register(User, UserAdmin)

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

class GredAdmin(admin.ModelAdmin):
    list_display = ('nama',)
    search_fields = ['nama']

class ProsedurPilihanAdmin(admin.ModelAdmin):
    list_display = ('nama',)
    search_fields = ['nama']

admin.site.register(Permohonan, PermohonanAdmin)
admin.site.register(Kelayakan)
admin.site.register(Jawatan, JawatanAdmin)
admin.site.register(Gred, GredAdmin)
admin.site.register(Jabatan, JabatanAdmin)
admin.site.register(ProsedurPilihan, ProsedurPilihanAdmin)
admin.site.register(UserProfile)
admin.site.register(SiteSettings)

# Daftarkan model-model prosedur baru
admin.site.register(CoreProcedure)
admin.site.register(SpecialisedProcedure)
admin.site.register(AdditionProcedure)
admin.site.register(ReductionProcedure)