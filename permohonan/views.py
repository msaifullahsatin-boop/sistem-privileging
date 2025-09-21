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

from .models import (
    Permohonan, Kelayakan, UserProfile, SiteSettings, Jabatan, Gred, Jawatan,
    ProsedurPilihan, CoreProcedure, SpecialisedProcedure, AdditionProcedure, ReductionProcedure
)
from .forms import BorangPermohonan, BorangSokonganKJ, BorangKeputusanJK, UserProfileForm, KelayakanForm


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
    KelayakanFormSet = inlineformset_factory(Permohonan, Kelayakan, form=KelayakanForm, extra=1, widgets={'tahun_lulus': forms.Select(choices=YEAR_CHOICES)})
    CoreProcedureFormSet = inlineformset_factory(Permohonan, CoreProcedure, fields=['prosedur'], extra=1, min_num=0)
    SpecialisedProcedureFormSet = inlineformset_factory(Permohonan, SpecialisedProcedure, fields=['prosedur'], extra=1, min_num=0)
    AdditionProcedureFormSet = inlineformset_factory(Permohonan, AdditionProcedure, fields=['prosedur', 'jenis'], extra=1, min_num=0)
    ReductionProcedureFormSet = inlineformset_factory(Permohonan, ReductionProcedure, fields=['nama_prosedur'], extra=1, min_num=0)

    if request.method == 'POST':
        form_utama = BorangPermohonan(request.POST, request.FILES)
        kelayakan_formset = KelayakanFormSet(request.POST, request.FILES, prefix='kelayakan')
        core_formset = CoreProcedureFormSet(request.POST, prefix='core')
        specialised_formset = SpecialisedProcedureFormSet(request.POST, prefix='specialised')
        addition_formset = AdditionProcedureFormSet(request.POST, prefix='addition')
        reduction_formset = ReductionProcedureFormSet(request.POST, prefix='reduction')
        formsets = [kelayakan_formset, core_formset, specialised_formset, addition_formset, reduction_formset]
        
        if form_utama.is_valid() and all(fs.is_valid() for fs in formsets):
            permohonan_baru = form_utama.save(commit=False)
            permohonan_baru.pemohon = request.user
            permohonan_baru.save()
            for fs in formsets:
                fs.instance = permohonan_baru
                fs.save()
            return redirect('dashboard')
    else:
        form_utama = BorangPermohonan()
        kelayakan_formset = KelayakanFormSet(prefix='kelayakan')
        core_formset = CoreProcedureFormSet(prefix='core')
        specialised_formset = SpecialisedProcedureFormSet(prefix='specialised')
        addition_formset = AdditionProcedureFormSet(prefix='addition')
        reduction_formset = ReductionProcedureFormSet(prefix='reduction')
        
    context = {
        'form_utama': form_utama,
        'kelayakan_formset': kelayakan_formset,
        'core_formset': core_formset,
        'specialised_formset': specialised_formset,
        'addition_formset': addition_formset,
        'reduction_formset': reduction_formset,
    }
    return render(request, 'permohonan/borang.html', context)

@login_required
def kemaskini_permohonan(request, pk):
    permohonan = get_object_or_404(Permohonan, pk=pk)
    if permohonan.pemohon != request.user:
        return redirect('dashboard')
    
    YEAR_CHOICES = [(r,r) for r in range(date.today().year, date.today().year - 50, -1)]
    KelayakanFormSet = inlineformset_factory(Permohonan, Kelayakan, form=KelayakanForm, extra=1, widgets={'tahun_lulus': forms.Select(choices=YEAR_CHOICES)}, can_delete=True)
    CoreProcedureFormSet = inlineformset_factory(Permohonan, CoreProcedure, fields=['prosedur'], extra=1, min_num=0, can_delete=True)
    SpecialisedProcedureFormSet = inlineformset_factory(Permohonan, SpecialisedProcedure, fields=['prosedur'], extra=1, min_num=0, can_delete=True)
    AdditionProcedureFormSet = inlineformset_factory(Permohonan, AdditionProcedure, fields=['prosedur', 'jenis'], extra=1, min_num=0, can_delete=True)
    ReductionProcedureFormSet = inlineformset_factory(Permohonan, ReductionProcedure, fields=['nama_prosedur'], extra=1, min_num=0, can_delete=True)
    
    if request.method == 'POST':
        form_utama = BorangPermohonan(request.POST, request.FILES, instance=permohonan)
        kelayakan_formset = KelayakanFormSet(request.POST, request.FILES, instance=permohonan, prefix='kelayakan')
        core_formset = CoreProcedureFormSet(request.POST, instance=permohonan, prefix='core')
        specialised_formset = SpecialisedProcedureFormSet(request.POST, instance=permohonan, prefix='specialised')
        addition_formset = AdditionProcedureFormSet(request.POST, instance=permohonan, prefix='addition')
        reduction_formset = ReductionProcedureFormSet(request.POST, instance=permohonan, prefix='reduction')
        formsets = [kelayakan_formset, core_formset, specialised_formset, addition_formset, reduction_formset]

        if form_utama.is_valid() and all(fs.is_valid() for fs in formsets):
            form_utama.save()
            for fs in formsets:
                fs.save()
            return redirect('dashboard')
    else:
        form_utama = BorangPermohonan(instance=permohonan)
        kelayakan_formset = KelayakanFormSet(instance=permohonan, prefix='kelayakan')
        core_formset = CoreProcedureFormSet(instance=permohonan, prefix='core')
        specialised_formset = SpecialisedProcedureFormSet(instance=permohonan, prefix='specialised')
        addition_formset = AdditionProcedureFormSet(instance=permohonan, prefix='addition')
        reduction_formset = ReductionProcedureFormSet(instance=permohonan, prefix='reduction')
        
    context = {
        'form_utama': form_utama,
        'kelayakan_formset': kelayakan_formset,
        'core_formset': core_formset,
        'specialised_formset': specialised_formset,
        'addition_formset': addition_formset,
        'reduction_formset': reduction_formset,
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
        core_procs = [f"- {p.prosedur.nama} (Core)" for p in permohonan.core_procedures.all()]
        spec_procs = [f"- {p.prosedur.nama} (Specialised)" for p in permohonan.specialised_procedures.all()]
        add_procs = [f"- {p.prosedur.nama} (Addition - {p.get_jenis_display()})" for p in permohonan.addition_procedures.all()]
        red_procs = [f"- {p.nama_prosedur} (Reduction)" for p in permohonan.reduction_procedures.all()]
        senarai_prosedur = "\n".join(core_procs + spec_procs + add_procs + red_procs)
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