from django.conf import settings
from django.db import models
from django.db.models import Avg


class Propiedad(models.Model):

    class TipoPropiedad(models.TextChoices):
        CASA = 'casa', 'Casa'
        DEPARTAMENTO = 'departamento', 'Departamento'
        CABANA = 'cabana', 'Cabaña'
        HABITACION = 'habitacion', 'Habitación'
        ESTUDIO = 'estudio', 'Estudio'

    class Modalidad(models.TextChoices):
        HOSPEDAJE = 'hospedaje', 'Hospedaje'
        ARRIENDO = 'arriendo', 'Arriendo'
        VENTA = 'venta', 'Venta'

    class UnidadPrecio(models.TextChoices):
        NOCHE = 'noche', '/ noche'
        MES = 'mes', '/ mes'
        TOTAL = 'total', 'total'

    propietario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='propiedades',
        null=True,
        blank=True,
    )
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True)
    tipo_propiedad = models.CharField(max_length=20, choices=TipoPropiedad.choices)
    modalidad = models.CharField(max_length=20, choices=Modalidad.choices)
    ciudad = models.CharField(max_length=100)
    direccion = models.CharField(max_length=255, blank=True)
    precio = models.DecimalField(max_digits=12, decimal_places=2)
    unidad_precio = models.CharField(max_length=10, choices=UnidadPrecio.choices)
    capacidad_personas = models.PositiveIntegerField(null=True, blank=True)
    habitaciones = models.PositiveIntegerField(null=True, blank=True)
    banos = models.PositiveIntegerField(null=True, blank=True)
    metros_cuadrados = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    activa = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-fecha_creacion']
        verbose_name = 'Propiedad'
        verbose_name_plural = 'Propiedades'

    def __str__(self):
        return f'{self.titulo} ({self.ciudad})'

    @property
    def foto_principal(self):
        return self.fotos.filter(es_principal=True).first() or self.fotos.first()

    @property
    def calificacion_promedio(self):
        promedio = self.resenas.aggregate(prom=Avg('calificacion'))['prom']
        return round(promedio, 2) if promedio else None

    @property
    def num_resenas(self):
        return self.resenas.count()


class FotoPropiedad(models.Model):
    propiedad = models.ForeignKey(Propiedad, on_delete=models.CASCADE, related_name='fotos')
    imagen = models.ImageField(upload_to='propiedades/')
    es_principal = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Foto'
        verbose_name_plural = 'Fotos'

    def __str__(self):
        return f'Foto de {self.propiedad.titulo}'


class Resena(models.Model):
    propiedad = models.ForeignKey(Propiedad, on_delete=models.CASCADE, related_name='resenas')
    autor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    calificacion = models.PositiveSmallIntegerField(help_text='De 1 a 5')
    comentario = models.TextField(blank=True)
    cal_limpieza = models.PositiveSmallIntegerField(null=True, blank=True)
    cal_ubicacion = models.PositiveSmallIntegerField(null=True, blank=True)
    cal_comunicacion = models.PositiveSmallIntegerField(null=True, blank=True)
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-fecha']
        verbose_name = 'Reseña'
        verbose_name_plural = 'Reseñas'

    def __str__(self):
        return f'Reseña de {self.propiedad.titulo} — {self.calificacion}★'