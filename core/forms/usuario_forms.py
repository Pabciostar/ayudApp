from django import forms
from ..models import Usuario

class DatosAdicionalesForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ['rut_usuario', 'nombres', 'apellidos', 'nacimiento', 'telefono', 'sexo']

        widgets = {
            'nacimiento': forms.DateInput(attrs={'type': 'date'}),
        }

        labels = {
            'rut_usuario': 'RUT',
            'nombres': 'Nombre',
            'apellidos': 'Apellido',
            'nacimiento': 'Fecha de nacimiento',
            'telefono': 'Teléfono',
            'sexo': 'Sexo (M/F)',
        }