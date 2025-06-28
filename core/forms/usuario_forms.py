import re
from django import forms
from ..models import Usuario

class DatosAdicionalesForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'  # Bootstrap

    def clean_sexo(self):
        sexo = self.cleaned_data.get('sexo')
        if not sexo:
            raise forms.ValidationError("Debes seleccionar una opción valida.")
        return sexo
    
    def clean_rut_usuario(self):
        rut = self.cleaned_data.get('rut_usuario')

        if not rut:
            raise forms.ValidationError("El RUT es obligatorio.")

        # Elimina puntos y espacios para procesarlo
        rut = rut.replace(".", "").replace(" ", "").upper()

        # Verifica formato básico (8 o 9 dígitos + guion + 1 dígito o K)
        if not re.match(r'^(\d{7,8}-[\dK])$', rut):
            raise forms.ValidationError("Formato de RUT inválido. Ejemplo: 12.345.678-9")

        # Separa número y dígito verificador
        numero, dv = rut.split("-")

        # Calcula el dígito verificador
        reversed_digits = map(int, reversed(numero))
        factors = [2, 3, 4, 5, 6, 7] * ((len(numero) // 6) + 1)
        s = sum(d * f for d, f in zip(reversed_digits, factors))
        check_digit = (-s) % 11

        expected_dv = str(check_digit) if check_digit < 10 else 'K'

        if expected_dv != dv:
            raise forms.ValidationError("Dígito verificador incorrecto.")

        # Devuelve el RUT formateado sin puntos pero con guion
        return f"{numero}-{dv}"

        
    class Meta:
        model = Usuario
        fields = ['rut_usuario', 'nombres', 'apellidos', 'nacimiento', 'telefono', 'sexo']
        widgets = {
            'nacimiento': forms.DateInput(attrs={'type': 'date'}),
            'sexo': forms.Select(attrs={'class': 'form-select'}),
        }