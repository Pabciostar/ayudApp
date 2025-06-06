from rest_framework import serializers
from core.models import Usuario, Ayudante, ClaseAgendada, Postulacion
from datetime import datetime

class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = '__all__'

class PostulacionSerializer(serializers.ModelSerializer):
    usuario = serializers.StringRelatedField()

    class Meta:
        model = Postulacion
        fields = '__all__'

    def get_fecha_hora(self, obj):
        try:
            # Suponiendo que el ID tiene formato ddMMyyHHMMSS (25 mayo 2020 14:00:05)
            fecha = datetime.strptime(str(obj.id_postulacion), "%d%m%y%H%M%S")
            return fecha.strftime("%d/%m/%Y %H:%M")
        except:
            return "Formato inválido"