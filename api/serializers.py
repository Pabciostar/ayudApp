import base64
from rest_framework import serializers

from core.models import Usuario, Ayudante, ClaseAgendada, Postulacion, Notificacion, Evaluacion
from datetime import datetime

class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = '__all__'

class AyudanteSerializer(serializers.ModelSerializer):
    usuario = UsuarioSerializer(source='id_ayudante', read_only=True)
    foto_base64 = serializers.SerializerMethodField()
    id = serializers.SerializerMethodField()  

    class Meta:
        model = Ayudante
        fields = [
            'id',  
            'usuario',
            'carrera',
            'foto_base64',
            'cuentanos',
            'disponibilidad',
            'experiencia',
            'ramos',
            'valor',
            'terminos',
            'validado',
        ]

    def get_foto_base64(self, obj):
        if obj.foto:
            return f"data:image/jpeg;base64,{base64.b64encode(obj.foto).decode('utf-8')}"
        return None

    def get_id(self, obj):
        return obj.id_ayudante.pk 

    
class PostulacionSerializer(serializers.ModelSerializer):
    usuario = serializers.StringRelatedField()

    class Meta:
        model = Postulacion
        fields = '__all__'

    def get_fecha_hora(self, obj):
        try:
            fecha = datetime.strptime(str(obj.id_postulacion), "%d%m%y%H%M%S")
            return fecha.strftime("%d/%m/%Y %H:%M")
        except:
            return "Formato inválido"


class NotificacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notificacion
        fields = '__all__'


class MejorAyudanteSerializer(serializers.Serializer):
    id = serializers.CharField()
    promedio = serializers.FloatField()


class ClaseAgendadaSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClaseAgendada
        fields = '__all__'

class EvaluacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Evaluacion
        fields = '__all__'