from django.shortcuts import render
from .models import Propiedad


def inicio(request):
    propiedades = (
        Propiedad.objects
        .filter(activa=True)
        .prefetch_related('fotos', 'resenas')
    )
    return render(request, 'core/index.html', {'propiedades': propiedades})