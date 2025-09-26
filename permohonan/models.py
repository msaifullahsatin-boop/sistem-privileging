from django.db import models
from django.contrib.auth.models import User

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

class Gred(models.Model):
    nama = models.CharField(max_length=50, unique=True)
    def __str__(self):
        return self.nama

class Jabatan(models.Model):
    nama = models.CharField(max_length=150, unique=True)
    def __str__(self):
        return self.nama

class ProsedurPilihan(models.Model):
    nama = models.CharField("Nama Prosedur", max_length=255, unique=True)
    def __str__(self):
        return self.nama

class SubKategori(models.Model):
    nama = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nama

    class Meta:
        verbose_name = "Sub-Kategori Pemohon"
        verbose_name_plural = "Sub-Kategori Pemohon"

class Permohonan(models.Model):
    KATEGORI_UTAMA_CHOICES = [('', '---------'), ('Pakar Perubatan / Pergigian', 'Pakar Perubatan / Pergigian'), ('Pegawai Perubatan', 'Pegawai Perubatan'), ('Jururawat', 'Jururawat'), ('Penolong Pegawai Perubatan', 'Penolong Pegawai Perubatan'), ('Juruterapi Pergigian', 'Juruterapi Pergigian'), ('Anggota Kesihatan Bersekutu', 'Anggota Kesihatan Bersekutu'), ('Pegawai Farmasi', 'Pegawai Farmasi'), ('Penolong Pegawai Farmasi', 'Penolong Pegawai Farmasi'), ('Lain-lain', 'Lain-lain')]
    KATEGORI_BAWAHAN_CHOICES = [('', '---------'), ('Pakar HWKKS', 'Pakar HWKKS'), ('Pakar KKM Lain', 'Pakar KKM dari Hospital lain selain HWKKS'), ('Pakar Bukan KKM', 'Pakar daripada institusi selain KKM'), ('Lantikan Baru', 'Lantikan baru/ bertukar masuk'), ('Ada Credentialing', 'Ada Credentialing'), ('Ada Post Basic', 'Ada Post Basic')]
    JENIS_PERMOHONAN_CHOICES = [('Baru', 'Permohonan Baru (Privileging)'), ('Penambahan', 'Permohonan Penambahan (Privileging Addition)'), ('Ulangan', 'Permohonan Ulangan (Re-Privileging)'), ('Ulangan + Tambah', 'Permohonan Ulangan bersama penambahan prosedur baru'), ('Ulangan + Kurang', 'Permohonan Ulangan bersama pengurangan prosedur baru')]
    SOKONGAN_CHOICES = [('Menunggu', 'Menunggu Semakan'), ('Menyokong', 'Menyokong'), ('Tidak Menyokong', 'Tidak Menyokong')]
    KELULUSAN_CHOICES = [('Menunggu', 'Menunggu Keputusan'), ('Ya', 'Diluluskan'), ('Tidak', 'Ditolak')]
    
    pemohon = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    nama_pemohon = models.CharField(max_length=255)
    no_kp = models.CharField("No K/P", max_length=15)
    jawatan = models.ForeignKey(Jawatan, on_delete=models.PROTECT, null=True, verbose_name="Jawatan")
    gred = models.ForeignKey(Gred, on_delete=models.PROTECT, null=True, verbose_name="Gred")
    jabatan = models.ForeignKey(Jabatan, on_delete=models.PROTECT, null=True)
    tarikh_mula_bertugas = models.DateField("Tarikh mula bertugas di jabatan sekarang")
    no_sijil_amalan = models.CharField("No. Sijil Amalan Tahunan", max_length=100, blank=True, null=True)
    jenis_permohonan = models.CharField(max_length=50, choices=JENIS_PERMOHONAN_CHOICES, null=True)
    kategori_utama = models.CharField("Kategori Pemohon Utama", max_length=100, choices=KATEGORI_UTAMA_CHOICES, null=True)
    kategori_bawahan = models.CharField("Sub-Kategori Pemohon (Lama)", max_length=100, choices=KATEGORI_BAWAHAN_CHOICES, blank=True, null=True, editable=False)
    sub_kategori = models.ManyToManyField(SubKategori, verbose_name="Sub-Kategori Pemohon", blank=True)
    jawatan_lain = models.CharField("Jawatan Lain-lain (jika berkenaan)", max_length=100, blank=True, null=True)
    tarikh_borang_dihantar = models.DateField(auto_now_add=True)
    
    # --- LABEL TELAH DIKEMAS KINI DI SINI ---
    status_sokongan_kj = models.CharField("Status Sokongan Ketua Jabatan", max_length=20, choices=SOKONGAN_CHOICES, default='Menunggu')
    ulasan_kj = models.TextField("Ulasan Ketua Jabatan", blank=True, null=True)
    nama_kj = models.CharField("Nama Ketua Jabatan", max_length=255, blank=True, null=True)
    jawatan_kj = models.CharField("Jawatan Ketua Jabatan", max_length=100, blank=True, null=True)
    tarikh_sokongan_kj = models.DateField("Tarikh Sokongan Ketua Jabatan", blank=True, null=True)
    # ------------------------------------

    keputusan_jawatanankuasa = models.CharField("Keputusan Pengarah", max_length=20, choices=KELULUSAN_CHOICES, default='Menunggu')
    tarikh_keputusan = models.DateField("Tarikh Keputusan", blank=True, null=True)
    tarikh_sah_sehingga = models.DateField("Tarikh Sah Sehingga", blank=True, null=True)
    no_siri_sijil = models.CharField("No Siri Sijil", max_length=100, blank=True, null=True, unique=True)

    def __str__(self):
        return f"Permohonan oleh {self.nama_pemohon} pada {self.tarikh_borang_dihantar}"

class Kelayakan(models.Model):
    permohonan = models.ForeignKey(Permohonan, related_name='kelayakan', on_delete=models.CASCADE)
    nama_kelayakan = models.CharField("Kelayakan (Ijazah, Master dll.)", max_length=255)
    universiti = models.CharField(max_length=255)
    tahun_lulus = models.IntegerField("Tahun Lulus")
    salinan_sijil = models.FileField("Salinan Sijil", upload_to='sijil_kelayakan/')
    def __str__(self):
        return f"{self.nama_kelayakan} dari {self.universiti}"

class CoreProcedure(models.Model):
    permohonan = models.ForeignKey(Permohonan, related_name='core_procedures', on_delete=models.CASCADE)
    prosedur = models.ForeignKey(ProsedurPilihan, on_delete=models.PROTECT)
    def __str__(self):
        return self.prosedur.nama

class SpecialisedProcedure(models.Model):
    permohonan = models.ForeignKey(Permohonan, related_name='specialised_procedures', on_delete=models.CASCADE)
    prosedur = models.ForeignKey(ProsedurPilihan, on_delete=models.PROTECT)
    def __str__(self):
        return self.prosedur.nama

class AdditionProcedure(models.Model):
    permohonan = models.ForeignKey(Permohonan, related_name='addition_procedures', on_delete=models.CASCADE)
    prosedur = models.ForeignKey(ProsedurPilihan, on_delete=models.PROTECT, verbose_name="Prosedur")
    jenis = models.CharField(max_length=20, choices=[('Core', 'Core'), ('Specialised', 'Specialised')])
    def __str__(self):
        return f"{self.prosedur.nama} ({self.jenis})"

class ReductionProcedure(models.Model):
    permohonan = models.ForeignKey(Permohonan, related_name='reduction_procedures', on_delete=models.CASCADE)
    nama_prosedur = models.CharField(max_length=255)
    def __str__(self):
        return self.nama_prosedur

class SijilTemplate(models.Model):
    nama = models.CharField(max_length=100, help_text="Nama untuk templat ini (cth: 'Templat Rasmi 2024')")
    html_content = models.TextField(help_text="Kod HTML penuh untuk templat sijil.")
    is_active = models.BooleanField(default=False, help_text="Tandakan jika ini adalah templat yang sedang digunakan. Hanya satu templat boleh aktif pada satu masa.")
    tarikh_dicipta = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nama

    def save(self, *args, **kwargs):
        if self.is_active:
            # Pastikan hanya satu templat yang aktif
            SijilTemplate.objects.filter(is_active=True).update(is_active=False)
        super(SijilTemplate, self).save(*args, **kwargs)

    class Meta:
        verbose_name = "Templat Sijil"
        verbose_name_plural = "Templat Sijil"