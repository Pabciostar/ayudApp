import base64
from rest_framework import serializers
from core.models import Usuario, Ayudante, ClaseAgendada, Postulacion, Notificacion, Evaluacion, Materia, Transaccion
from django.utils.timezone import make_aware
from datetime import datetime, time, date

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
    id = serializers.IntegerField()
    nombre = serializers.CharField()
    descripcion = serializers.CharField()
    ramos = serializers.CharField()
    promedio = serializers.FloatField()
    imagen_url = serializers.CharField(allow_null=True)


class ClaseAgendadaSerializer(serializers.ModelSerializer):
    # Asumiendo que 'id_materia' es un ForeignKey en ClaseAgendada al modelo Materia
    nombre_materia = serializers.CharField(source='materia_id_materia.nombre', read_only=True) 
    nombre_ayudante = serializers.SerializerMethodField() # Ya lo tenías, lo mantengo
    calificacion = serializers.SerializerMethodField()

    class Meta:
        model = ClaseAgendada
        fields = '__all__' # Asegúrate que 'id_materia' esté incluido en tus fields
        # Si prefieres especificar todos los campos para mayor control:
        # fields = ['id_clase', 'usuario_id_usuario', 'id_ayudante', 'id_materia', 'nombre_materia', 'fecha', 'hora', 'estado']
    
    def get_nombre_ayudante(self, obj):
        # Asegurarse de que el ayudante exista antes de intentar acceder a sus atributos de usuario
        if obj.id_ayudante and obj.id_ayudante.id_ayudante:
            return f"{obj.id_ayudante.id_ayudante.nombres} {obj.id_ayudante.id_ayudante.apellidos}"
        return None
    
    def get_calificacion(self, obj):
        evaluacion = Evaluacion.objects.filter(clase_agendada_id_clase=obj.id_clase).first()
        return evaluacion.valoracion if evaluacion else None

class EvaluacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Evaluacion
        fields = '__all__'


class MateriaSerializer(serializers.ModelSerializer):
    id_ayudante = serializers.PrimaryKeyRelatedField(
        source='ayudante_id_ayudante',
        queryset=Ayudante.objects.all()
    )
    nombre_ayudante = serializers.SerializerMethodField()

    class Meta:
        model = Materia
        fields = ['id_materia', 'nombre', 'id_ayudante', 'nombre_ayudante']

    def get_nombre_ayudante(self, obj):
        usuario = obj.ayudante_id_ayudante.id_ayudante
        return f"{usuario.nombres} {usuario.apellidos}"
    
class TransaccionSerializer(serializers.ModelSerializer):
    fecha = serializers.SerializerMethodField()

    class Meta:
        model = Transaccion
        fields = '__all__'

    def get_fecha(self, obj):
        if isinstance(obj.fecha, date) and not isinstance(obj.fecha, datetime):
            # convertir a datetime si viene como date
            return make_aware(datetime.combine(obj.fecha, time.min))
        return obj.fecha