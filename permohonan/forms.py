from django import forms
from .models import Permohonan, UserProfile, Kelayakan

class KelayakanForm(forms.ModelForm):
    class Meta:
        model = Kelayakan
        fields = ['nama_kelayakan', 'universiti', 'tahun_lulus', 'salinan_sijil']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.required = False

class BorangPermohonan(forms.ModelForm):
    pengesahan = forms.BooleanField(
        label="Saya mengesahkan semua maklumat yang diberikan adalah benar dan tepat.",
        required=True
    )
    class Meta:
        model = Permohonan
        fields = [
            'nama_pemohon', 'no_kp', 'jawatan', 'gred', 'jabatan', 
            'tarikh_mula_bertugas', 'no_sijil_amalan', 'jenis_permohonan', 
            'kategori_utama', 'kategori_bawahan', 'jawatan_lain',
        ]
        widgets = {
            'tarikh_mula_bertugas': forms.DateInput(attrs={'type': 'date'}),
        }
        help_texts = {
            'no_sijil_amalan': 'Abaikan jika tidak berkenaan.',
        }

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