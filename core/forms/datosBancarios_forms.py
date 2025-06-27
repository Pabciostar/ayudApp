from django import forms
from ..models import Ctacte

BANCO_CHOICES = [
    ('Banco de Chile', 'Banco de Chile'),
    ('Banco Internacional', 'Banco Internacional'),
    ('Banco Scotiabank', 'Scotiabank Chile'),
    ('Banco de Crédito e Inversiones', 'Banco de Crédito e Inversiones (BCI)'),
    ('Banco BICE', 'Banco BICE'),
    ('HSBC Bank', 'HSBC Bank (Chile)'),
    ('Banco Santander', 'Banco Santander-Chile'),
    ('Banco Itaú', 'Banco Itaú Chile'),
    ('Banco Security', 'Banco Security'),
    ('Banco Falabella', 'Banco Falabella'),
    ('Banco Ripley', 'Banco Ripley'),
    ('Banco Estado', 'Banco del Estado de Chile'),
]

TIPO_CUENTA_CHOICES = [
    ('corriente', 'Cuenta Corriente'),
    ('vista', 'Cuenta Vista'),
]

class datosBancariosForm(forms.ModelForm):
    banco = forms.ChoiceField(choices=BANCO_CHOICES, label="Banco", widget=forms.Select(attrs={'class': 'form-select'}))
    tipodecta = forms.ChoiceField(choices=TIPO_CUENTA_CHOICES, label="Tipo de cuenta", widget=forms.Select(attrs={'class': 'form-select'}))

    class Meta:
        model = Ctacte
        fields = ['rut_usuario', 'nombres', 'apellidos', 'correo', 'banco', 'tipodecta', 'numdecta']
        labels = {
            'numdecta': 'Número de cuenta',
            'rut_usuario': 'RUT',
            'nombres': 'Nombres',
            'apellidos': 'Apellidos',
            'correo': 'Correo electrónico',
        }
        widgets = {
            'numdecta': forms.NumberInput(attrs={'placeholder': 'Número de cuenta', 'class': 'form-control'}),
            'rut_usuario': forms.TextInput(attrs={'class': 'form-control'}),
            'nombres': forms.TextInput(attrs={'class': 'form-control'}),
            'apellidos': forms.TextInput(attrs={'class': 'form-control'}),
            'correo': forms.EmailInput(attrs={'class': 'form-control'}),
        }