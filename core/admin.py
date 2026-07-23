from django.contrib import admin
from .models import (
    Usuario, Agente, Anfitrion, Propiedad, FotoPropiedad, Amenidad,
    PropiedadAmenidad, Disponibilidad, ReservaHospedaje,
    ContratoArriendo, ProcesoVenta, OfertaCompra, Documento,
    Pago, Resena
)


class FotoPropiedadInline(admin.TabularInline):
    model = FotoPropiedad
    extra = 1


class ResenaInline(admin.TabularInline):
    model = Resena
    extra = 0


@admin.register(Propiedad)
class PropiedadAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'ciudad', 'modalidad', 'tipo_propiedad', 'precio', 'unidad_precio', 'activa')
    list_filter = ('modalidad', 'tipo_propiedad', 'ciudad', 'activa')
    search_fields = ('titulo', 'ciudad', 'direccion')
    inlines = [FotoPropiedadInline, ResenaInline]


@admin.register(FotoPropiedad)
class FotoPropiedadAdmin(admin.ModelAdmin):
    list_display = ('propiedad', 'es_principal')


@admin.register(Resena)
class ResenaAdmin(admin.ModelAdmin):
    list_display = ('propiedad', 'autor', 'calificacion', 'fecha')
    list_filter = ('calificacion',)


# Registra los demás modelos para que aparezcan en el admin
@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'rol', 'verificado')
    list_filter = ('rol', 'verificado')


admin.site.register(Agente)
admin.site.register(Anfitrion)
admin.site.register(Amenidad)
admin.site.register(PropiedadAmenidad)
admin.site.register(Disponibilidad)
admin.site.register(ReservaHospedaje)
admin.site.register(ContratoArriendo)
admin.site.register(ProcesoVenta)
admin.site.register(OfertaCompra)
admin.site.register(Documento)
admin.site.register(Pago)