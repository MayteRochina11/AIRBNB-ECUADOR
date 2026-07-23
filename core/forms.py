from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User

from .models import Propiedad


class StyledFormMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault('class', 'field-input')


class RegistroForm(StyledFormMixin, UserCreationForm):
    email = forms.EmailField(required=True, label='Correo electrónico')

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
        labels = {'username': 'Usuario'}

    def save(self, commit=True):
        usuario = super().save(commit=False)
        usuario.email = self.cleaned_data['email']
        if commit:
            usuario.save()
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
