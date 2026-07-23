from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render, get_object_or_404
from django.http import JsonResponse

from .forms import PropiedadForm, RegistroForm
from .models import FotoPropiedad, Propiedad, Usuario
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


def _puede_publicar(usuario):
    """Solo anfitriones, agentes y administradores pueden publicar propiedades."""
    if usuario.is_staff or usuario.is_superuser:
        return True
    return usuario.rol in ('host', 'agente')


@login_required
def publicar_propiedad(request):
    if not _puede_publicar(request.user):
        messages.error(request, 'Como viajero solo puedes reservar propiedades, no publicarlas. Cambia tu rol a Anfitrión o Agente para publicar.')
        return redirect('core:inicio')

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
def detalle_propiedad(request, propiedad_id):
    from .forms import ReservaForm
    propiedad = get_object_or_404(
        Propiedad.objects.select_related('propietario', 'agente__usuario'),
        id=propiedad_id,
    )
    resenas = propiedad.resenas.select_related('autor')

    reserva = None
    form = ReservaForm()

    if request.method == 'POST':
        if not request.user.is_authenticated:
            messages.error(request, 'Debes iniciar sesión para reservar.')
            return redirect('core:login')

        form = ReservaForm(request.POST)
        if form.is_valid():
            reserva = form.save(commit=False)
            reserva.propiedad = propiedad
            reserva.huesped = request.user

            dias = (reserva.fecha_salida - reserva.fecha_entrada).days
            if propiedad.unidad_precio == 'noche':
                unidades = max(dias, 1)
            elif propiedad.unidad_precio == 'mes':
                unidades = max(round(dias / 30), 1)
            else:
                unidades = 1
            reserva.precio_total = propiedad.precio * unidades
            reserva.save()

            messages.success(
                request,
                f'¡Reserva realizada! Total a pagar: ${reserva.precio_total} '
                f'({reserva.get_metodo_pago_display}). Estado: pendiente de confirmación.'
            )
            return redirect('core:detalle_propiedad', propiedad_id=propiedad.id)

    return render(request, 'core/detalle_propiedad.html', {
        'propiedad': propiedad,
        'resenas': resenas,
        'form': form,
    })


def _puede_editar(usuario, propiedad):
    """Puede editar/eliminar si es el dueño, el agente asignado o un administrador."""
    if usuario.is_staff or usuario.is_superuser:
        return True
    if propiedad.propietario_id == usuario.id:
        return True
    if propiedad.agente and propiedad.agente.usuario_id == usuario.id:
        return True
    return False


@login_required
def mis_propiedades(request):
    from django.db.models import Q
    propiedades = Propiedad.objects.filter(
        Q(propietario=request.user) | Q(agente__usuario=request.user)
    ).distinct().prefetch_related('fotos')
    return render(request, 'core/mis_propiedades.html', {'propiedades': propiedades})


@login_required
def editar_propiedad(request, propiedad_id):
    propiedad = get_object_or_404(Propiedad, id=propiedad_id)

    if not _puede_editar(request.user, propiedad):
        messages.error(request, 'No puedes editar una propiedad que no es tuya.')
        return redirect('core:mis_propiedades')

    if request.method == 'POST':
        form = PropiedadForm(request.POST, instance=propiedad)
        if form.is_valid():
            form.save()

            fotos = request.FILES.getlist('fotos')
            for i, foto in enumerate(fotos):
                FotoPropiedad.objects.create(
                    propiedad=propiedad,
                    url_foto=foto,
                    es_principal=(i == 0 and not propiedad.fotos.exists()),
                )

            messages.success(request, '¡Propiedad actualizada con éxito!')
            return redirect('core:mis_propiedades')
    else:
        form = PropiedadForm(instance=propiedad)

    return render(request, 'core/editar_propiedad.html', {'form': form, 'propiedad': propiedad})


@login_required
def eliminar_propiedad(request, propiedad_id):
    propiedad = get_object_or_404(Propiedad, id=propiedad_id)

    if not _puede_editar(request.user, propiedad):
        messages.error(request, 'No puedes eliminar una propiedad que no es tuya.')
        return redirect('core:mis_propiedades')

    if request.method == 'POST':
        titulo = propiedad.titulo
        propiedad.delete()
        messages.success(request, f'La propiedad "{titulo}" fue eliminada.')
        if request.user.is_staff or request.user.is_superuser:
            return redirect('core:panel_admin')
        return redirect('core:mis_propiedades')

    return redirect('core:mis_propiedades')


def _es_admin(usuario):
    return usuario.is_staff or usuario.is_superuser


@login_required
def panel_admin(request):
    if not _es_admin(request.user):
        messages.error(request, 'No tienes permiso para acceder al panel de administración.')
        return redirect('core:inicio')

    propiedades = Propiedad.objects.all().select_related('propietario').prefetch_related('fotos')
    usuarios = Usuario.objects.all().order_by('rol', 'username')
    return render(request, 'core/panel_admin.html', {
        'propiedades': propiedades,
        'usuarios': usuarios,
    })


@login_required
def eliminar_usuario(request, usuario_id):
    if not _es_admin(request.user):
        messages.error(request, 'No tienes permiso para eliminar usuarios.')
        return redirect('core:inicio')

    usuario = get_object_or_404(Usuario, id=usuario_id)

    if request.method == 'POST':
        if usuario.id == request.user.id:
            messages.error(request, 'No puedes eliminar tu propia cuenta desde aquí.')
        elif usuario.is_superuser:
            messages.error(request, 'No se puede eliminar a otro administrador.')
        else:
            nombre = usuario.username
            usuario.delete()
            messages.success(request, f'El usuario "{nombre}" fue eliminado.')
    return redirect('core:panel_admin')


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