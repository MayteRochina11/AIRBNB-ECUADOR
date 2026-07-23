from django.contrib import admin
from .models import Propiedad, FotoPropiedad, Resena


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