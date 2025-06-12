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
            raise forms.ValidationError("Debe seleccionar una opción válida.")
        return sexo

    class Meta:
        model = Usuario
        fields = ['rut_usuario', 'nombres', 'apellidos', 'nacimiento', 'telefono', 'sexo']
        widgets = {
            'nacimiento': forms.DateInput(attrs={'type': 'date'}),
            'sexo': forms.Select(attrs={'class': 'form-select'}),
        }