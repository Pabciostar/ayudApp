from rest_framework import serializers
from core.models import Usuario, Ayudante, ClaseAgendada 

class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = '__all__'