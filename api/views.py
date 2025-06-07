from rest_framework import viewsets
from core.models import Usuario, Postulacion
from .serializers import UsuarioSerializer, PostulacionSerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response

class UsuarioViewSet(viewsets.ModelViewSet):
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer


@api_view(['GET'])
def mi_rol(request):
    if not request.user.is_authenticated:
        return Response({'rol': 'anonimo'}, status=401)

    correo = request.user.email
    try:
        usuario = Usuario.objects.get(correo=correo)
        return Response({'rol': usuario.rol})
    except Usuario.DoesNotExist:
        return Response({'rol': 'desconocido'}, status=404)
    
class PostulacionViewSet(viewsets.ModelViewSet):
    queryset = Postulacion.objects.all()
    serializer_class = PostulacionSerializer