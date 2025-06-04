from django import forms
from ..models import Postulacion

class PostulacionForm(forms.ModelForm):
    class Meta:
        model = Postulacion
        fields = ['carrera', 'foto', 'cuentanos', 'disponibilidad', 'experiencia', 'ramos', 'valor', 'terminos']