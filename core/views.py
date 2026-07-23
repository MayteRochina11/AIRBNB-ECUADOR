from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render, get_object_or_404
from django.http import JsonResponse

from .forms import PropiedadForm, RegistroForm
from .models import FotoPropiedad, Propiedad
from django.apps import apps
Favorito = apps.get_model('core', 'Favorito')


def inicio(request):
    propiedades = (
        Propiedad.objects
        .filter(activa=True)
        .prefetch_related('fotos', 'resenas')
    )

    ciudad = request.GET.get('ciudad', '').strip()
    modalidad = request.GET.get('modalidad', '').strip()
    tipo_propiedad = request.GET.get('tipo_propiedad', '').strip()
    num_huespedes = request.GET.get('num_huespedes', '').strip()

    if ciudad:
        propiedades = propiedades.filter(ciudad__icontains=ciudad)
    if modalidad:
        propiedades = propiedades.filter(modalidad=modalidad)
    if tipo_propiedad:
        propiedades = propiedades.filter(tipo_propiedad=tipo_propiedad)
    if num_huespedes and num_huespedes.isdigit():
        propiedades = propiedades.filter(capacidad_personas__gte=int(num_huespedes))

    context = {
        'propiedades': propiedades,
        'modalidad_actual': modalidad,
        'tipo_actual': tipo_propiedad,
    }
    return render(request, 'core/index.html', context)


def registro(request):
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            usuario = form.save()
            login(request, usuario)
            messages.success(request, '¡Cuenta creada y sesión iniciada!')
            return redirect('core:inicio')
    else:
        form = RegistroForm()
    return render(request, 'core/registro.html', {'form': form})


@login_required
def publicar_propiedad(request):
    if request.method == 'POST':
        form = PropiedadForm(request.POST)
        if form.is_valid():
            propiedad = form.save(commit=False)
            propiedad.propietario = request.user
            propiedad.save()
            
            fotos = request.FILES.getlist('fotos')
            for i, foto in enumerate(fotos):
                FotoPropiedad.objects.create(
                    propiedad=propiedad,
                    url_foto=foto,
                    es_principal=(i == 0)
                )
            
            messages.success(request, '¡Propiedad publicada con éxito!')
            return redirect('core:inicio')
    else:
        form = PropiedadForm()
    
    return render(request, 'core/publicar.html', {'form': form})


def anfitriones(request):
    propiedades_host = Propiedad.objects.filter(
        activa=True,
        propietario__rol='host'
    ).prefetch_related('fotos', 'resenas')[:6]
    return render(request, 'core/anfitriones.html', {'propiedades': propiedades_host})


def agentes(request):
    propiedades_agente = Propiedad.objects.filter(
        activa=True,
        agente__isnull=False
    ).prefetch_related('fotos', 'resenas')[:6]
    return render(request, 'core/agentes.html', {'propiedades': propiedades_agente})


def ayuda(request):
    return render(request, 'core/ayuda.html')


# --- NUEVAS VISTAS PARA LAS PÁGINAS INDEPENDIENTES ---

def hospedaje(request):
    propiedades = Propiedad.objects.filter(activa=True, modalidad='hospedaje_corto').prefetch_related('fotos', 'resenas')
    return render(request, 'core/hospedaje.html', {'propiedades': propiedades})


def arriendo(request):
    propiedades = Propiedad.objects.filter(activa=True, modalidad='arriendo').prefetch_related('fotos', 'resenas')
    return render(request, 'core/arriendo.html', {'propiedades': propiedades})


def venta(request):
    propiedades = Propiedad.objects.filter(activa=True, modalidad='venta').prefetch_related('fotos', 'resenas')
    return render(request, 'core/venta.html', {'propiedades': propiedades})


def confianza(request):
    return render(request, 'core/confianza.html')


def contacto(request):
    return render(request, 'core/contacto.html')


@login_required
def toggle_favorito(request, propiedad_id):
    if request.method == 'POST':
        propiedad = get_object_or_404(Propiedad, id=propiedad_id)
        favorito, created = Favorito.objects.get_or_create(
            usuario=request.user,
            propiedad=propiedad
        )
        if not created:
            favorito.delete()
            return JsonResponse({'favorito': False})
        return JsonResponse({'favorito': True})
    return JsonResponse({'error': 'Método no permitido'}, status=405)