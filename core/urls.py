from django.contrib.auth import views as auth_views
from django.urls import path

from . import views
from .forms import LoginForm

app_name = 'core'

urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('propiedad/<int:propiedad_id>/', views.detalle_propiedad, name='detalle_propiedad'),
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
    path('mis-propiedades/', views.mis_propiedades, name='mis_propiedades'),
    path('editar/<int:propiedad_id>/', views.editar_propiedad, name='editar_propiedad'),
    path('eliminar/<int:propiedad_id>/', views.eliminar_propiedad, name='eliminar_propiedad'),
    path('panel-admin/', views.panel_admin, name='panel_admin'),
    path('panel-admin/usuario/<int:usuario_id>/eliminar/', views.eliminar_usuario, name='eliminar_usuario'),
    path('anfitriones/', views.anfitriones, name='anfitriones'),
    path('agentes/', views.agentes, name='agentes'),
    path('ayuda/', views.ayuda, name='ayuda'),
    
    path('hospedaje/', views.hospedaje, name='hospedaje'),
    path('arriendo/', views.arriendo, name='arriendo'),
    path('venta/', views.venta, name='venta'),
    path('confianza/', views.confianza, name='confianza'),
    path('contacto/', views.contacto, name='contacto'),
    
    path('favorito/<int:propiedad_id>/', views.toggle_favorito, name='toggle_favorito'),
]