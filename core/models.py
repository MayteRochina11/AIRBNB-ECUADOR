from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator

# =========================================================
# 1. USUARIOS (extendiendo el User de Django)
# =========================================================
class Usuario(AbstractUser):
    # Configuración especial para evitar el error E304 (conflicto con auth.User)
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='usuario_set',          # <-- Este nombre es el que Django quiere
        related_query_name='usuario',
        blank=True
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='usuario_set',          # <-- Este nombre es el que Django quiere
        related_query_name='usuario',
        blank=True
    )

    ROLES = (
        ('host', 'Anfitrión'),
        ('agente', 'Agente'),
        ('comprador', 'Comprador'),
        ('viajero', 'Viajero'),
    )
    rol = models.CharField(max_length=20, choices=ROLES, default='viajero')
    verificado = models.BooleanField(default=False)
    telefono = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'

    def __str__(self):
        return f'{self.username} ({self.get_rol_display()})'


# =========================================================
# 2. AGENTES
# =========================================================
class Agente(models.Model):
    ESPECIALIDADES = (
        ('venta', 'Venta'),
        ('arriendo', 'Arriendo'),
        ('ambos', 'Ambos'),
    )
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, related_name='agente')
    licencia = models.CharField(max_length=100, blank=True, null=True)
    especialidad = models.CharField(max_length=20, choices=ESPECIALIDADES, default='ambos')
    comision_porcentaje = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    propiedades_activas = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = 'Agente'
        verbose_name_plural = 'Agentes'

    def __str__(self):
        return f'Agente: {self.usuario.username}'


# =========================================================
# 3. PROPIEDADES
# =========================================================
class Propiedad(models.Model):
    TIPO_PROPIEDAD = (
        ('casa', 'Casa'),
        ('cabana', 'Cabaña'),
        ('habitacion', 'Habitación'),
        ('apartamento', 'Apartamento'),
        ('estudio', 'Estudio'),
    )
    MODALIDAD = (
        ('venta', 'Venta'),
        ('arriendo', 'Arriendo'),
        ('hospedaje_corto', 'Hospedaje corto'),
    )
    UNIDAD_PRECIO = (
        ('total', 'Total'),
        ('mes', 'Por mes'),
        ('noche', 'Por noche'),
    )

    propietario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='propiedades')
    agente = models.ForeignKey(Agente, on_delete=models.SET_NULL, null=True, blank=True, related_name='propiedades')
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True)
    tipo_propiedad = models.CharField(max_length=20, choices=TIPO_PROPIEDAD)
    modalidad = models.CharField(max_length=20, choices=MODALIDAD)
    ciudad = models.CharField(max_length=100)
    direccion = models.CharField(max_length=255, blank=True)
    precio = models.DecimalField(max_digits=12, decimal_places=2)
    unidad_precio = models.CharField(max_length=10, choices=UNIDAD_PRECIO)
    capacidad_personas = models.PositiveIntegerField(null=True, blank=True)
    habitaciones = models.PositiveIntegerField(null=True, blank=True)
    banos = models.PositiveIntegerField(null=True, blank=True)
    metros_cuadrados = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    activa = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Propiedad'
        verbose_name_plural = 'Propiedades'
        ordering = ['-fecha_creacion']

    def __str__(self):
        return f'{self.titulo} - {self.ciudad}'

    @property
    def foto_principal(self):
        return self.fotos.filter(es_principal=True).first() or self.fotos.first()

    @property
    def calificacion_promedio(self):
        promedio = self.resenas.aggregate(models.Avg('calificacion'))['calificacion__avg']
        return round(promedio, 2) if promedio else None


# =========================================================
# 4. FOTOS_PROPIEDAD
# =========================================================
class FotoPropiedad(models.Model):
    propiedad = models.ForeignKey(Propiedad, on_delete=models.CASCADE, related_name='fotos')
    url_foto = models.ImageField(upload_to='propiedades/')  # Puedes cambiar a URLField si usas enlaces externos
    es_principal = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Foto'
        verbose_name_plural = 'Fotos'

    def __str__(self):
        return f'Foto de {self.propiedad.titulo}'


# =========================================================
# 5. AMENIDADES
# =========================================================
class Amenidad(models.Model):
    CATEGORIAS = (
        ('basica', 'Básica'),
        ('premium', 'Premium'),
        ('exterior', 'Exterior'),
    )
    nombre = models.CharField(max_length=100)
    categoria = models.CharField(max_length=20, choices=CATEGORIAS, default='basica')

    class Meta:
        verbose_name = 'Amenidad'
        verbose_name_plural = 'Amenidades'

    def __str__(self):
        return self.nombre


# =========================================================
# 6. PROPIEDAD_AMENIDADES (N:M)
# =========================================================
class PropiedadAmenidad(models.Model):
    propiedad = models.ForeignKey(Propiedad, on_delete=models.CASCADE)
    amenidad = models.ForeignKey(Amenidad, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Amenidad de propiedad'
        verbose_name_plural = 'Amenidades de propiedades'
        unique_together = ('propiedad', 'amenidad')

    def __str__(self):
        return f'{self.propiedad.titulo} - {self.amenidad.nombre}'


# =========================================================
# 7. DISPONIBILIDAD
# =========================================================
class Disponibilidad(models.Model):
    propiedad = models.ForeignKey(Propiedad, on_delete=models.CASCADE, related_name='disponibilidades')
    fecha = models.DateField()
    disponible = models.BooleanField(default=True)
    precio_especial = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)

    class Meta:
        verbose_name = 'Disponibilidad'
        verbose_name_plural = 'Disponibilidades'
        unique_together = ('propiedad', 'fecha')

    def __str__(self):
        return f'{self.propiedad.titulo} - {self.fecha} {"(Disponible)" if self.disponible else "(Ocupado)"}'


# =========================================================
# 8. RESERVAS_HOSPEDAJE
# =========================================================
class ReservaHospedaje(models.Model):
    ESTADOS = (
        ('pendiente', 'Pendiente'),
        ('confirmada', 'Confirmada'),
        ('cancelada', 'Cancelada'),
        ('completada', 'Completada'),
    )
    propiedad = models.ForeignKey(Propiedad, on_delete=models.CASCADE, related_name='reservas')
    huesped = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='reservas')
    fecha_entrada = models.DateField()
    fecha_salida = models.DateField()
    num_huespedes = models.PositiveIntegerField()
    precio_total = models.DecimalField(max_digits=12, decimal_places=2)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='pendiente')
    tipo_alojamiento = models.CharField(max_length=20, choices=(('hospedaje', 'Hospedaje'), ('cabana', 'Cabaña')), blank=True, null=True)

    class Meta:
        verbose_name = 'Reserva de hospedaje'
        verbose_name_plural = 'Reservas de hospedaje'

    def __str__(self):
        return f'Reserva de {self.huesped.username} en {self.propiedad.titulo}'


# =========================================================
# 9. CONTRATOS_ARRIENDO
# =========================================================
class ContratoArriendo(models.Model):
    ESTADOS = (
        ('borrador', 'Borrador'),
        ('activo', 'Activo'),
        ('vencido', 'Vencido'),
        ('terminado', 'Terminado'),
    )
    propiedad = models.ForeignKey(Propiedad, on_delete=models.CASCADE, related_name='contratos')
    arrendatario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='contratos_arrendatario')
    propietario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='contratos_propietario')
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField(null=True, blank=True)
    canon_mensual = models.DecimalField(max_digits=12, decimal_places=2)
    deposito_garantia = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='borrador')
    duracion_meses = models.PositiveIntegerField(null=True, blank=True)

    class Meta:
        verbose_name = 'Contrato de arriendo'
        verbose_name_plural = 'Contratos de arriendo'

    def __str__(self):
        return f'Contrato {self.propiedad.titulo} - {self.arrendatario.username}'


# =========================================================
# 10. PROCESO_VENTA
# =========================================================
class ProcesoVenta(models.Model):
    ESTADOS = (
        ('oferta', 'Oferta'),
        ('negociacion', 'Negociación'),
        ('aprobado', 'Aprobado'),
        ('escritura', 'Escritura'),
        ('cerrado', 'Cerrado'),
    )
    propiedad = models.ForeignKey(Propiedad, on_delete=models.CASCADE, related_name='ventas')
    comprador = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, blank=True, related_name='ventas_comprador')
    vendedor = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='ventas_vendedor')
    agente = models.ForeignKey(Agente, on_delete=models.SET_NULL, null=True, blank=True, related_name='ventas')
    precio_oferta = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    precio_acordado = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='oferta')
    fecha_oferta = models.DateField(null=True, blank=True)
    fecha_cierre = models.DateField(null=True, blank=True)

    class Meta:
        verbose_name = 'Proceso de venta'
        verbose_name_plural = 'Procesos de venta'

    def __str__(self):
        return f'Venta de {self.propiedad.titulo} - {self.estado}'


# =========================================================
# 11. OFERTAS_COMPRA
# =========================================================
class OfertaCompra(models.Model):
    ESTADOS = (
        ('enviada', 'Enviada'),
        ('aceptada', 'Aceptada'),
        ('rechazada', 'Rechazada'),
        ('contraoferta', 'Contraoferta'),
    )
    venta = models.ForeignKey(ProcesoVenta, on_delete=models.CASCADE, related_name='ofertas')
    comprador = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='ofertas')
    monto_oferta = models.DecimalField(max_digits=12, decimal_places=2)
    mensaje = models.TextField(blank=True)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='enviada')
    fecha_oferta = models.DateField(auto_now_add=True)

    class Meta:
        verbose_name = 'Oferta de compra'
        verbose_name_plural = 'Ofertas de compra'

    def __str__(self):
        return f'Oferta de {self.comprador.username} - ${self.monto_oferta}'


# =========================================================
# 12. DOCUMENTOS (referencia polimórfica)
# =========================================================
class Documento(models.Model):
    TIPO_REFERENCIA = (
        ('venta', 'Venta'),
        ('arriendo', 'Arriendo'),
        ('reserva', 'Reserva'),
    )
    TIPO_DOC = (
        ('contrato', 'Contrato'),
        ('escritura', 'Escritura'),
        ('recibo', 'Recibo'),
        ('identificacion', 'Identificación'),
    )
    id_referencia = models.PositiveIntegerField()
    tipo_referencia = models.CharField(max_length=20, choices=TIPO_REFERENCIA)
    tipo_doc = models.CharField(max_length=20, choices=TIPO_DOC)
    url_archivo = models.URLField(max_length=500)
    fecha_subida = models.DateField(auto_now_add=True)

    class Meta:
        verbose_name = 'Documento'
        verbose_name_plural = 'Documentos'

    def __str__(self):
        return f'{self.get_tipo_doc_display()} - {self.get_tipo_referencia_display()} #{self.id_referencia}'


# =========================================================
# 13. PAGOS (referencia polimórfica)
# =========================================================
class Pago(models.Model):
    TIPO_REFERENCIA = (
        ('reserva', 'Reserva'),
        ('arriendo', 'Arriendo'),
        ('venta', 'Venta'),
    )
    ESTADOS = (
        ('pendiente', 'Pendiente'),
        ('completado', 'Completado'),
        ('fallido', 'Fallido'),
        ('reembolsado', 'Reembolsado'),
    )
    CONCEPTOS = (
        ('canon', 'Canon'),
        ('deposito', 'Depósito'),
        ('reserva', 'Reserva'),
        ('cuota_inicial', 'Cuota inicial'),
    )
    id_referencia = models.PositiveIntegerField()
    tipo_referencia = models.CharField(max_length=20, choices=TIPO_REFERENCIA)
    monto = models.DecimalField(max_digits=12, decimal_places=2)
    metodo_pago = models.CharField(max_length=50, blank=True, null=True)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='pendiente')
    concepto = models.CharField(max_length=20, choices=CONCEPTOS)
    fecha_pago = models.DateField(auto_now_add=True)

    class Meta:
        verbose_name = 'Pago'
        verbose_name_plural = 'Pagos'

    def __str__(self):
        return f'Pago {self.get_concepto_display()} - ${self.monto} ({self.estado})'


# =========================================================
# 14. RESEÑAS
# =========================================================
class Resena(models.Model):
    propiedad = models.ForeignKey(Propiedad, on_delete=models.CASCADE, related_name='resenas')
    autor = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='resenas_escritas')
    id_referencia = models.PositiveIntegerField()  # FK a Reserva o Contrato
    tipo_referencia = models.CharField(max_length=20, choices=(('reserva', 'Reserva'), ('arriendo', 'Arriendo')))
    calificacion = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comentario = models.TextField(blank=True)
    cal_limpieza = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)], null=True, blank=True)
    cal_ubicacion = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)], null=True, blank=True)
    cal_comunicacion = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)], null=True, blank=True)
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Reseña'
        verbose_name_plural = 'Reseñas'
        ordering = ['-fecha']

    def __str__(self):
        return f'Reseña de {self.autor.username} a {self.propiedad.titulo} - {self.calificacion}★'
    
    class Favorito(models.Model):
        usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='favoritos')
        propiedad = models.ForeignKey(Propiedad, on_delete=models.CASCADE, related_name='favoritos')
        fecha_agregado = models.DateTimeField(auto_now_add=True)

        class Meta:
            verbose_name = 'Favorito'
            verbose_name_plural = 'Favoritos'
            unique_together = ('usuario', 'propiedad')  # Un usuario no puede guardar la misma propiedad dos veces

        def __str__(self):
            return f'{self.usuario.username} -> {self.propiedad.titulo}'
