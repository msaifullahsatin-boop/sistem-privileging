from django import forms
from .models import Permohonan, UserProfile

class BorangPermohonan(forms.ModelForm):
    tarikh_mula_bertugas = forms.DateField(
        label="Tarikh mula bertugas di jabatan sekarang",
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    class Meta:
        model = Permohonan
        # Gantikan 'jawatan_gred' dengan 'jawatan' dan 'gred'
        fields = [
            'nama_pemohon', 'no_kp', 'jawatan', 'gred', 'jabatan', 
            'tarikh_mula_bertugas', 'no_sijil_amalan', 'jenis_permohonan', 'kategori_pemohon',
        ]

class BorangSokonganKJ(forms.ModelForm):
    class Meta:
        model = Permohonan
        fields = ['status_sokongan_kj', 'ulasan_kj']

class BorangKeputusanJK(forms.ModelForm):
    class Meta:
        model = Permohonan
        fields = ['keputusan_jawatanankuasa']

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['gambar_profil']