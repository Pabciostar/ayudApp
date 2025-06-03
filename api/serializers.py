from rest_framework import serializers
from core.models import Usuario, Ayudante, ClaseAgendada  # etc.

class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = '__all__'