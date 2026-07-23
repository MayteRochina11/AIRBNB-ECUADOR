from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User

from .models import Usuario, Propiedad, Agente, ReservaHospedaje

class StyledFormMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault('class', 'field-input')


class RegistroForm(StyledFormMixin, UserCreationForm):
    email = forms.EmailField(required=True, label='Correo electrónico')
    rol = forms.ChoiceField(
        label='Quiero registrarme como',
        choices=[
            ('viajero', 'Viajero'),
            ('host', 'Anfitrión'),
            ('agente', 'Agente'),
        ],
        initial='viajero',
    )

    class Meta:
        model = Usuario
        fields = ('username', 'email', 'rol', 'password1', 'password2')
        labels = {'username': 'Usuario'}

    def save(self, commit=True):
        usuario = super().save(commit=False)
        usuario.email = self.cleaned_data['email']
        usuario.rol = self.cleaned_data['rol']
        if commit:
            usuario.save()
            # Si se registra como agente, se le crea su perfil de agente
            if usuario.rol == 'agente':
                Agente.objects.get_or_create(usuario=usuario)
        return usuario


class LoginForm(StyledFormMixin, AuthenticationForm):
    pass


class PropiedadForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = Propiedad
        fields = [
            'titulo', 'descripcion', 'tipo_propiedad', 'modalidad',
            'ciudad', 'direccion', 'precio', 'unidad_precio',
            'capacidad_personas', 'habitaciones', 'banos', 'metros_cuadrados',
        ]
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 4}),
        }


class ReservaForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = ReservaHospedaje
        fields = ['fecha_entrada', 'fecha_salida', 'num_huespedes', 'metodo_pago']
        labels = {
            'fecha_entrada': 'Fecha de llegada',
            'fecha_salida': 'Fecha de salida',
            'num_huespedes': 'Número de huéspedes',
            'metodo_pago': 'Método de pago',
        }
        widgets = {
            'fecha_entrada': forms.DateInput(attrs={'type': 'date'}),
            'fecha_salida': forms.DateInput(attrs={'type': 'date'}),
        }

    def clean(self):
        datos = super().clean()
        entrada = datos.get('fecha_entrada')
        salida = datos.get('fecha_salida')
        if entrada and salida and salida <= entrada:
            self.add_error('fecha_salida', 'La fecha de salida debe ser posterior a la de llegada.')
        return datos