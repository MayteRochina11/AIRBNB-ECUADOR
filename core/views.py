from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .forms import PropiedadForm, RegistroForm
from .models import FotoPropiedad, Propiedad


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
    if num_huespedes.isdigit():
        propiedades = propiedades.filter(capacidad_personas__gte=int(num_huespedes))

    contexto = {
        'propiedades': propiedades,
        'modalidad_actual': modalidad,
        'tipo_actual': tipo_propiedad,
    }
    return render(request, 'core/index.html', contexto)


def registro(request):
    if request.user.is_authenticated:
        return redirect('core:inicio')

    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            usuario = form.save()
            login(request, usuario)
            messages.success(request, 'Cuenta creada. ¡Bienvenido/a a Estancia!')
            return redirect('core:inicio')
    else:
        form = RegistroForm()

    return render(request, 'core/registro.html', {'form': form})


@login_required
def publicar_propiedad(request):
    if request.method == 'POST':
        form = PropiedadForm(request.POST)
        fotos = request.FILES.getlist('fotos')
        if form.is_valid():
            propiedad = form.save(commit=False)
            propiedad.propietario = request.user
            propiedad.save()
            for indice, imagen in enumerate(fotos):
                FotoPropiedad.objects.create(
                    propiedad=propiedad,
                    imagen=imagen,
                    es_principal=(indice == 0),
                )
            messages.success(request, f'"{propiedad.titulo}" fue publicada correctamente.')
            return redirect('core:inicio')
    else:
        form = PropiedadForm()

    return render(request, 'core/publicar.html', {'form': form})
