from django.db import models
from django.contrib.auth.models import User

# ... (SiteSettings & UserProfile tidak berubah) ...
class SiteSettings(models.Model):
    applications_open = models.BooleanField("Permohonan Dibuka", default=True)
    maintenance_mode = models.BooleanField("Mod Selenggaraan Aktif", default=False)
    papan_notis = models.TextField("Teks Papan Notis", blank=True, null=True, help_text="Maklumat yang akan dipaparkan di halaman log masuk.")
    class Meta:
        verbose_name = "Tetapan Laman"
        verbose_name_plural = "Tetapan Laman"
    def __str__(self):
        return "Tetapan Laman Utama"
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    jabatan = models.ForeignKey('Jabatan', on_delete=models.SET_NULL, null=True, blank=True)
    gambar_profil = models.ImageField(default='default.jpg', upload_to='profile_pics', null=True, blank=True)
    def __str__(self):
        return self.user.username

class Jawatan(models.Model):
    nama = models.CharField(max_length=100, unique=True)
    def __str__(self):
        return self.nama

# --- MODEL BARU DI SINI ---
class Gred(models.Model):
    nama = models.CharField(max_length=50, unique=True)
    def __str__(self):
        return self.nama

# ... (Jabatan & ProsedurPilihan tidak berubah) ...
class Jabatan(models.Model):
    nama = models.CharField(max_length=150, unique=True)
    def __str__(self):
        return self.nama
class ProsedurPilihan(models.Model):
    nama = models.CharField("Nama Prosedur", max_length=255, unique=True)
    def __str__(self):
        return self.nama

class Permohonan(models.Model):
    # ... (Choices tidak berubah) ...
    JENIS_PERMOHONAN_CHOICES = [('Baru', 'Permohonan Baru (Privileging)'), ('Penambahan', 'Permohonan Penambahan (Privileging Addition)'), ('Ulangan', 'Permohonan Ulangan (Re-Privileging)'), ('Ulangan + Tambah', 'Permohonan Ulangan bersama penambahan prosedur baru'), ('Ulangan + Kurang', 'Permohonan Ulangan bersama pengurangan prosedur baru')]
    KATEGORI_PEMOHON_CHOICES = [('Pakar Perubatan / Pergigian', 'Pakar Perubatan / Pergigian'), ('Pegawai Perubatan / Pergigian', 'Pegawai Perubatan / Pergigian'), ('Paramedik', 'Paramedik'), ('Anggota Kesihatan Bersekutu', 'Anggota Kesihatan Bersekutu'), ('Pegawai Farmasi', 'Pegawai Farmasi'), ('Penolong Pegawai Farmasi', 'Penolong Pegawai Farmasi'), ('Lain-lain', 'Jawatan lain-lain')]
    SOKONGAN_CHOICES = [('Menunggu', 'Menunggu Semakan'), ('Menyokong', 'Menyokong'), ('Tidak Menyokong', 'Tidak Menyokong')]
    KELULUSAN_CHOICES = [('Menunggu', 'Menunggu Keputusan'), ('Ya', 'Diluluskan'), ('Tidak', 'Ditolak')]
    
    pemohon = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    nama_pemohon = models.CharField(max_length=255)
    no_kp = models.CharField("No K/P", max_length=15)
    
    # --- PERUBAHAN DI SINI ---
    jawatan = models.ForeignKey(Jawatan, on_delete=models.PROTECT, null=True, verbose_name="Jawatan")
    gred = models.ForeignKey(Gred, on_delete=models.PROTECT, null=True, verbose_name="Gred")
    # -------------------------

    jabatan = models.ForeignKey(Jabatan, on_delete=models.PROTECT, null=True)
    tarikh_mula_bertugas = models.DateField("Tarikh mula bertugas di jabatan sekarang")
    no_sijil_amalan = models.CharField("No. Sijil Amalan Tahunan", max_length=100)
    # ... (selebihnya model Permohonan tidak berubah) ...
    jenis_permohonan = models.CharField(max_length=50, choices=JENIS_PERMOHONAN_CHOICES)
    kategori_pemohon = models.CharField(max_length=100, choices=KATEGORI_PEMOHON_CHOICES)
    tarikh_borang_dihantar = models.DateField(auto_now_add=True)
    status_sokongan_kj = models.CharField("Status Sokongan Ketua Jabatan", max_length=20, choices=SOKONGAN_CHOICES, default='Menunggu')
    ulasan_kj = models.TextField("Ulasan Ketua Jabatan", blank=True, null=True)
    nama_kj = models.CharField("Nama Ketua Jabatan", max_length=255, blank=True, null=True)
    jawatan_kj = models.CharField("Jawatan Ketua Jabatan", max_length=100, blank=True, null=True)
    tarikh_sokongan_kj = models.DateField("Tarikh Sokongan Ketua Jabatan", blank=True, null=True)
    keputusan_jawatanankuasa = models.CharField(max_length=20, choices=KELULUSAN_CHOICES, default='Menunggu')
    tarikh_keputusan = models.DateField("Tarikh Keputusan", blank=True, null=True)
    tarikh_sah_sehingga = models.DateField("Tarikh Sah Sehingga", blank=True, null=True)
    no_siri_sijil = models.CharField("No Siri Sijil", max_length=100, blank=True, null=True, unique=True)
    def __str__(self):
        return f"Permohonan oleh {self.nama_pemohon} pada {self.tarikh_borang_dihantar}"
# ... (Kelayakan & ProsedurDimohon tidak berubah) ...
class Kelayakan(models.Model):
    permohonan = models.ForeignKey(Permohonan, related_name='kelayakan', on_delete=models.CASCADE)
    nama_kelayakan = models.CharField("Kelayakan (Ijazah, Master dll.)", max_length=255)
    universiti = models.CharField(max_length=255)
    tahun_lulus = models.IntegerField("Tahun Lulus")
    salinan_sijil = models.FileField("Salinan Sijil", upload_to='sijil_kelayakan/')
    def __str__(self):
        return f"{self.nama_kelayakan} dari {self.universiti}"
class ProsedurDimohon(models.Model):
    JENIS_PROSEDUR_CHOICES = [('Core', 'Core Procedure'), ('Specialised', 'Specialised Procedure'), ('Addition', 'Addition Procedure'), ('Reduction', 'Reduction Procedure'), ('Digugurkan', 'Prosedur Digugurkan')]
    permohonan = models.ForeignKey(Permohonan, related_name='prosedur', on_delete=models.CASCADE)
    nama_prosedur = models.ForeignKey(ProsedurPilihan, on_delete=models.PROTECT, null=True)
    jenis_prosedur = models.CharField(max_length=20, choices=JENIS_PROSEDUR_CHOICES)
    def __str__(self):
        return f"({self.jenis_prosedur}) {self.nama_prosedur}"