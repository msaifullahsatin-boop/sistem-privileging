from django.shortcuts import render, redirect, get_object_or_404
from django.forms import inlineformset_factory
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django import forms
from datetime import date
from django.http import HttpResponse
import pandas as pd
from .utils import render_to_pdf 

from .models import Permohonan, Kelayakan, ProsedurDimohon, UserProfile, SiteSettings, Jabatan, Gred
from .forms import BorangPermohonan, BorangSokonganKJ, BorangKeputusanJK, UserProfileForm


def custom_login_view(request, *args, **kwargs):
    settings, created = SiteSettings.objects.get_or_create()
    if settings and not settings.applications_open:
        return render(request, 'permohonan/permohonan_ditutup.html')
    
    login_view = LoginView.as_view(
        template_name='permohonan/log_masuk.html',
        extra_context={'settings': settings}
    )
    return login_view(request, *args, **kwargs)

def index(request):
    if request.user.is_authenticated:
        if request.user.is_superuser or request.user.groups.filter(name='Jawatankuasa').exists():
            return redirect('jawatankuasa_dashboard')
        elif request.user.groups.filter(name='KetuaJabatan').exists():
            return redirect('hod_dashboard')
        elif request.user.groups.filter(name='PICPrivileging').exists():
            return redirect('pic_dashboard')
        else:
            return redirect('dashboard')
    else:
        return redirect('laman_log_masuk')

@login_required
def dashboard(request):
    profil, dicipta = UserProfile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        profile_form = UserProfileForm(request.POST, request.FILES, instance=profil)
        if profile_form.is_valid():
            profile_form.save()
            return redirect('dashboard')
    else:
        profile_form = UserProfileForm(instance=profil)
    senarai_permohonan = Permohonan.objects.filter(pemohon=request.user).order_by('-tarikh_borang_dihantar')
    context = { 
        'senarai_permohonan': senarai_permohonan,
        'profile_form': profile_form,
    }
    return render(request, 'permohonan/dashboard.html', context)

@login_required
def pic_dashboard(request):
    if not request.user.groups.filter(name='PICPrivileging').exists():
        return redirect('dashboard') 
    try:
        jabatan_pic = request.user.userprofile.jabatan
    except UserProfile.DoesNotExist:
        jabatan_pic = None
    if jabatan_pic:
        senarai_permohonan = Permohonan.objects.filter(jabatan=jabatan_pic).order_by('-tarikh_borang_dihantar')
    else:
        senarai_permohonan = Permohonan.objects.none()
    context = {
        'senarai_permohonan': senarai_permohonan,
        'jabatan_pic': jabatan_pic
    }
    return render(request, 'permohonan/pic_dashboard.html', context)

@login_required
def hod_dashboard(request):
    if not request.user.groups.filter(name='KetuaJabatan').exists():
        return redirect('dashboard') 
    try:
        jabatan_hod = request.user.userprofile.jabatan
    except UserProfile.DoesNotExist:
        jabatan_hod = None
    if jabatan_hod:
        senarai_semua_permohonan = Permohonan.objects.filter(jabatan=jabatan_hod).order_by('-tarikh_borang_dihantar')
    else:
        senarai_semua_permohonan = Permohonan.objects.none()
    context = {
        'senarai_semua_permohonan': senarai_semua_permohonan,
        'jabatan_hod': jabatan_hod
    }
    return render(request, 'permohonan/hod_dashboard.html', context)

@login_required
def jawatankuasa_dashboard(request):
    if not request.user.groups.filter(name='Jawatankuasa').exists():
        return redirect('dashboard')
    senarai_permohonan_sedia = Permohonan.objects.filter(status_sokongan_kj='Menyokong').order_by('-tarikh_borang_dihantar')
    context = { 'senarai_permohonan_sedia': senarai_permohonan_sedia }
    return render(request, 'permohonan/jawatankuasa_dashboard.html', context)

@login_required
def laporan_permohonan(request):
    user = request.user
    if not (user.is_superuser or user.groups.filter(name__in=['Jawatankuasa', 'PICPrivileging']).exists()):
        return redirect('dashboard')
    permohonan_list = Permohonan.objects.all().order_by('-tarikh_borang_dihantar')
    jabatan_filter_id = request.GET.get('jabatan')
    if jabatan_filter_id:
        permohonan_list = permohonan_list.filter(jabatan__id=jabatan_filter_id)
    context = {
        'senarai_permohonan': permohonan_list,
        'senarai_jabatan': Jabatan.objects.all(),
        'jabatan_terpilih': int(jabatan_filter_id) if jabatan_filter_id else None,
    }
    return render(request, 'permohonan/laporan.html', context)

@login_required
def papar_borang(request):
    YEAR_CHOICES = [(r,r) for r in range(date.today().year, date.today().year - 50, -1)]
    KelayakanFormSet = inlineformset_factory(Permohonan, Kelayakan, fields=('nama_kelayakan', 'universiti', 'tahun_lulus', 'salinan_sijil'), extra=2, widgets={'tahun_lulus': forms.Select(choices=YEAR_CHOICES)}, min_num=0)
    ProsedurFormSet = inlineformset_factory(Permohonan, ProsedurDimohon, fields=('nama_prosedur', 'jenis_prosedur'), extra=4, min_num=1, validate_min=True)
    
    if request.method == 'POST':
        form_utama = BorangPermohonan(request.POST, request.FILES)
        kelayakan_formset = KelayakanFormSet(request.POST, request.FILES, prefix='kelayakan')
        prosedur_formset = ProsedurFormSet(request.POST, prefix='prosedur')
        if form_utama.is_valid() and kelayakan_formset.is_valid() and prosedur_formset.is_valid():
            permohonan_baru = form_utama.save(commit=False)
            permohonan_baru.pemohon = request.user
            permohonan_baru.save()
            kelayakan_formset.instance = permohonan_baru
            kelayakan_formset.save()
            prosedur_formset.instance = permohonan_baru
            prosedur_formset.save()
            return redirect('dashboard')
    else:
        form_utama = BorangPermohonan()
        kelayakan_formset = KelayakanFormSet(prefix='kelayakan')
        prosedur_formset = ProsedurFormSet(prefix='prosedur')
    context = {
        'form_utama': form_utama,
        'kelayakan_formset': kelayakan_formset,
        'prosedur_formset': prosedur_formset,
    }
    return render(request, 'permohonan/borang.html', context)

@login_required
def kemaskini_permohonan(request, pk):
    permohonan = get_object_or_404(Permohonan, pk=pk)
    if permohonan.pemohon != request.user:
        return redirect('dashboard')
    YEAR_CHOICES = [(r,r) for r in range(date.today().year, date.today().year - 50, -1)]
    KelayakanFormSet = inlineformset_factory(Permohonan, Kelayakan, fields=('nama_kelayakan', 'universiti', 'tahun_lulus', 'salinan_sijil'), extra=1, widgets={'tahun_lulus': forms.Select(choices=YEAR_CHOICES)}, can_delete=True, min_num=0)
    ProsedurFormSet = inlineformset_factory(Permohonan, ProsedurDimohon, fields=('nama_prosedur', 'jenis_prosedur'), extra=1, can_delete=True, min_num=0)
    
    if request.method == 'POST':
        form_utama = BorangPermohonan(request.POST, request.FILES, instance=permohonan)
        kelayakan_formset = KelayakanFormSet(request.POST, request.FILES, instance=permohonan, prefix='kelayakan')
        prosedur_formset = ProsedurFormSet(request.POST, instance=permohonan, prefix='prosedur')
        if form_utama.is_valid() and kelayakan_formset.is_valid() and prosedur_formset.is_valid():
            form_utama.save()
            kelayakan_formset.save()
            prosedur_formset.save()
            return redirect('dashboard')
    else:
        form_utama = BorangPermohonan(instance=permohonan)
        kelayakan_formset = KelayakanFormSet(instance=permohonan, prefix='kelayakan')
        prosedur_formset = ProsedurFormSet(instance=permohonan, prefix='prosedur')
    context = {
        'form_utama': form_utama,
        'kelayakan_formset': kelayakan_formset,
        'prosedur_formset': prosedur_formset,
    }
    return render(request, 'permohonan/borang.html', context)

@login_required
def sokong_permohonan(request, pk):
    if not request.user.groups.filter(name='KetuaJabatan').exists():
        return redirect('dashboard')
    permohonan = get_object_or_404(Permohonan, pk=pk)
    try:
        if permohonan.jabatan != request.user.userprofile.jabatan:
            return redirect('hod_dashboard')
    except UserProfile.DoesNotExist:
        return redirect('hod_dashboard')
    if request.method == 'POST':
        form_sokongan = BorangSokonganKJ(request.POST, instance=permohonan)
        if form_sokongan.is_valid():
            permohonan_disokong = form_sokongan.save(commit=False)
            permohonan_disokong.nama_kj = request.user.get_full_name() or request.user.username
            permohonan_disokong.jawatan_kj = "Ketua Jabatan" 
            permohonan_disokong.tarikh_sokongan_kj = date.today()
            permohonan_disokong.save()
            return redirect('hod_dashboard')
    else:
        form_sokongan = BorangSokonganKJ(instance=permohonan)
    context = {'permohonan': permohonan, 'form_sokongan': form_sokongan}
    return render(request, 'permohonan/sokong_permohonan.html', context)

@login_required
def keputusan_jawatankuasa(request, pk):
    if not request.user.groups.filter(name='Jawatankuasa').exists():
        return redirect('dashboard')
    permohonan = get_object_or_404(Permohonan, pk=pk)
    if request.method == 'POST':
        form_keputusan = BorangKeputusanJK(request.POST, instance=permohonan)
        if form_keputusan.is_valid():
            keputusan_final = form_keputusan.save(commit=False)
            keputusan_final.tarikh_keputusan = date.today()
            if keputusan_final.keputusan_jawatanankuasa == 'Ya' and not keputusan_final.no_siri_sijil:
                kod_jabatan = keputusan_final.jabatan.nama[:3].upper()
                tahun = date.today().year
                bilangan_sedia_ada = Permohonan.objects.filter(jabatan=keputusan_final.jabatan, tarikh_keputusan__year=tahun,keputusan_jawatanankuasa='Ya').count()
                nombor_baru = bilangan_sedia_ada + 1
                keputusan_final.no_siri_sijil = f"{kod_jabatan}/{tahun}/{nombor_baru:03d}"
                keputusan_final.tarikh_sah_sehingga = keputusan_final.tarikh_keputusan.replace(year=keputusan_final.tarikh_keputusan.year + 3)
            elif keputusan_final.keputusan_jawatanankuasa != 'Ya':
                keputusan_final.tarikh_sah_sehingga = None
                keputusan_final.no_siri_sijil = None
            keputusan_final.save()
            return redirect('jawatankuasa_dashboard')
    else:
        form_keputusan = BorangKeputusanJK(instance=permohonan)
    context = {'permohonan': permohonan, 'form_keputusan': form_keputusan}
    return render(request, 'permohonan/keputusan_jawatankuasa.html', context)

def daftar(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            UserProfile.objects.create(user=user)
            return redirect('laman_log_masuk')
    else:
        form = UserCreationForm()
    return render(request, 'permohonan/daftar.html', {'form': form})

def laman_berjaya(request):
    return render(request, 'permohonan/berjaya.html')

@login_required
def jana_sijil_pdf(request, pk):
    permohonan = get_object_or_404(Permohonan, pk=pk)
    user = request.user
    is_owner = (user == permohonan.pemohon)
    is_admin_role = user.is_superuser or user.groups.filter(name__in=['Jawatankuasa', 'PICPrivileging', 'KetuaJabatan']).exists()
    
    if (not is_owner and not is_admin_role) or permohonan.keputusan_jawatanankuasa != 'Ya':
        return redirect('dashboard')
        
    context = {'permohonan': permohonan}
    pdf = render_to_pdf('permohonan/sijil_template.html', context)
    if pdf:
        response = HttpResponse(pdf, content_type='application/pdf')
        filename = f"Sijil_Privileging_{permohonan.nama_pemohon}.pdf"
        content = f"attachment; filename={filename}"
        response['Content-Disposition'] = content
        return response
    return HttpResponse("Tidak dapat menjana PDF.", status=400)

@login_required
def laporan_export_excel(request):
    user = request.user
    if not (user.is_superuser or user.groups.filter(name__in=['Jawatankuasa', 'PICPrivileging']).exists()):
        return redirect('dashboard')
    permohonan_list = Permohonan.objects.all()
    jabatan_filter_id = request.GET.get('jabatan')
    if jabatan_filter_id:
        permohonan_list = permohonan_list.filter(jabatan__id=jabatan_filter_id)
    data_rows = []
    for permohonan in permohonan_list:
        prosedur_texts = [f"- {p.nama_prosedur.nama} ({p.get_jenis_prosedur_display()})" for p in permohonan.prosedur.all()]
        senarai_prosedur = "\n".join(prosedur_texts)
        data_rows.append({
            'Nama Pemohon': permohonan.nama_pemohon, 'No. K/P': permohonan.no_kp,
            'Jawatan': permohonan.jawatan.nama if permohonan.jawatan else '',
            'Gred': permohonan.gred.nama if permohonan.gred else '',
            'Jabatan': permohonan.jabatan.nama if permohonan.jabatan else '',
            'Tarikh Mohon': permohonan.tarikh_borang_dihantar,
            'Status Sokongan KJ': permohonan.get_status_sokongan_kj_display(),
            'Keputusan Jawatankuasa': permohonan.get_keputusan_jawatanankuasa_display(),
            'Sah Sehingga': permohonan.tarikh_sah_sehingga,
            'No Siri Sijil': permohonan.no_siri_sijil,
            'Senarai Prosedur Dipohon': senarai_prosedur,
        })
    df = pd.DataFrame(data_rows)
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',)
    filename = "laporan_privileging_ditapis.xlsx" if jabatan_filter_id else "laporan_privileging_semua.xlsx"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    df.to_excel(response, index=False)
    return response

@login_required
def export_excel(request):
    # FUNGSI INI KINI DIGANTIKAN DENGAN laporan_export_excel YANG LEBIH BAIK
    # Anda boleh memadamnya jika mahu, tetapi pastikan URL juga dipadam.
    if not request.user.groups.filter(name='Jawatankuasa').exists():
        return redirect('dashboard')
    queryset = Permohonan.objects.all().values('nama_pemohon', 'no_kp', 'jawatan__nama', 'gred__nama', 'jabatan__nama', 'tarikh_borang_dihantar', 'status_sokongan_kj', 'ulasan_kj','nama_kj', 'tarikh_sokongan_kj', 'keputusan_jawatanankuasa', 'tarikh_keputusan', 'tarikh_sah_sehingga')
    df = pd.DataFrame(list(queryset))
    df.rename(columns={'jawatan__nama': 'Jawatan', 'gred__nama': 'Gred', 'jabatan__nama': 'Jabatan','tarikh_borang_dihantar': 'Tarikh Mohon','status_sokongan_kj': 'Status Sokongan KJ','ulasan_kj': 'Ulasan KJ','nama_kj': 'Nama KJ','tarikh_sokongan_kj': 'Tarikh Sokongan KJ','keputusan_jawatanankuasa': 'Keputusan Jawatankuasa','tarikh_keputusan': 'Tarikh Keputusan','tarikh_sah_sehingga': 'Sah Sehingga'}, inplace=True)
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',)
    response['Content-Disposition'] = 'attachment; filename="laporan_privileging.xlsx"'
    df.to_excel(response, index=False)
    return response