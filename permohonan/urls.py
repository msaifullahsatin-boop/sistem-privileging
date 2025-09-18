from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.index, name='index'), 
    path('dashboard/', views.dashboard, name='dashboard'),
    path('hod/dashboard/', views.hod_dashboard, name='hod_dashboard'),
    path('jawatankuasa/dashboard/', views.jawatankuasa_dashboard, name='jawatankuasa_dashboard'),
    path('pic/dashboard/', views.pic_dashboard, name='pic_dashboard'),
    
    # URL UNTUK LAPORAN
    path('laporan/', views.laporan_permohonan, name='laporan_permohonan'),
    path('laporan/export/excel/', views.laporan_export_excel, name='laporan_export_excel'),

    path('hod/permohonan/<int:pk>/sokong/', views.sokong_permohonan, name='sokong_permohonan'),
    path('jawatankuasa/permohonan/<int:pk>/keputusan/', views.keputusan_jawatankuasa, name='keputusan_jawatankuasa'),

    path('permohonan/<int:pk>/sijil/', views.jana_sijil_pdf, name='jana_sijil_pdf'),
    path('mohon/', views.papar_borang, name='borang_permohonan'),
    path('berjaya/', views.laman_berjaya, name='laman_berjaya'),
    
    path('daftar/', views.daftar, name='daftar'),
    path('logmasuk/', views.custom_login_view, name='laman_log_masuk'),
    path('logkeluar/', auth_views.LogoutView.as_view(), name='laman_log_keluar'),

    path('permohonan/<int:pk>/kemaskini/', views.kemaskini_permohonan, name='kemaskini_permohonan'),
    
    path('export/excel/', views.export_excel, name='export_excel'),
]