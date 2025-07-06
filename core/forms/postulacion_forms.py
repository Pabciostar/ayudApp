from django import forms
from ..models import Postulacion

class PostulacionForm(forms.ModelForm):
    terminos = forms.BooleanField(required=True, label='Acepto los términos y condiciones')

    class Meta:
        model = Postulacion
        fields = ['carrera', 'foto', 'cuentanos', 'disponibilidad', 'experiencia', 'ramos', 'valor', 'terminos']
        widgets = {
            'carrera': forms.TextInput(attrs={'class': 'form-control'}),
            'foto': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'cuentanos': forms.Textarea(attrs={'class': 'form-control'}),
            'disponibilidad': forms.TextInput(attrs={'class': 'form-control'}),
            'experiencia': forms.TextInput(attrs={'class': 'form-control'}),
            'ramos': forms.TextInput(attrs={'class': 'form-control'}),
            'valor': forms.NumberInput(attrs={'class': 'form-control'}),
        }

    def clean_terminos(self):
        terminos = self.cleaned_data.get('terminos')
        if not terminos:
            raise forms.ValidationError("Debes aceptar los términos y condiciones.")
        return "si" if terminos else "no"  # <-- aquí transformas True a 'si' para el modelo