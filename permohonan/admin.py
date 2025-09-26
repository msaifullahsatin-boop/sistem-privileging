from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import (
    Permohonan, Kelayakan, Jawatan, Gred, Jabatan, 
    ProsedurPilihan, UserProfile, SiteSettings, SijilTemplate,
    CoreProcedure, SpecialisedProcedure, AdditionProcedure, ReductionProcedure, SubKategori
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

@admin.register(SijilTemplate)
class SijilTemplateAdmin(admin.ModelAdmin):
    list_display = ('nama', 'is_active', 'tarikh_dicipta')
    list_filter = ('is_active',)
    actions = ['activate_template']

    def activate_template(self, request, queryset):
        if queryset.count() == 1:
            template = queryset.first()
            template.is_active = True
            template.save()
            self.message_user(request, f"Templat '{template.nama}' telah diaktifkan.")
        else:
            self.message_user(request, "Sila pilih satu templat sahaja untuk diaktifkan.", level='error')
    activate_template.short_description = "Aktifkan templat yang dipilih"

admin.site.register(Permohonan, PermohonanAdmin)
admin.site.register(Kelayakan)
admin.site.register(Jawatan, JawatanAdmin)
admin.site.register(Gred, GredAdmin)
admin.site.register(Jabatan, JabatanAdmin)
admin.site.register(ProsedurPilihan, ProsedurPilihanAdmin)
admin.site.register(UserProfile)
admin.site.register(SiteSettings)
admin.site.register(SubKategori)

# Daftarkan model-model prosedur baru
admin.site.register(CoreProcedure)
admin.site.register(SpecialisedProcedure)
admin.site.register(AdditionProcedure)
admin.site.register(ReductionProcedure)