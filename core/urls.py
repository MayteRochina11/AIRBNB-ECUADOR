from django.contrib.auth import views as auth_views
from django.urls import path

from . import views
from .forms import LoginForm

app_name = 'core'

urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('registro/', views.registro, name='registro'),
    path(
        'login/',
        auth_views.LoginView.as_view(
            template_name='core/login.html',
            authentication_form=LoginForm,
            redirect_authenticated_user=True,
        ),
        name='login',
    ),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('publicar/', views.publicar_propiedad, name='publicar'),
    path('anfitriones/', views.anfitriones, name='anfitriones'),
    path('agentes/', views.agentes, name='agentes'),
    path('ayuda/', views.ayuda, name='ayuda'),
    
    # --- NUEVAS URLS ---
    path('hospedaje/', views.hospedaje, name='hospedaje'),
    path('arriendo/', views.arriendo, name='arriendo'),
    path('venta/', views.venta, name='venta'),
    path('confianza/', views.confianza, name='confianza'),
    path('contacto/', views.contacto, name='contacto'),
    
    path('favorito/<int:propiedad_id>/', views.toggle_favorito, name='toggle_favorito'),
]