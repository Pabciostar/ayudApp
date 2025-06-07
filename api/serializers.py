import base64
from rest_framework import serializers
from core.models import Usuario, Ayudante, ClaseAgendada


class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = '__all__'

class AyudanteSerializer(serializers.ModelSerializer):
    usuario = UsuarioSerializer(source='id_ayudante', read_only=True)
    foto_base64 = serializers.SerializerMethodField()

    class Meta:
        model = Ayudante
        fields = [
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