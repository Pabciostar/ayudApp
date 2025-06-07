from django.shortcuts import render
from rest_framework import viewsets, status
from core.models import Usuario, Ayudante, Postulacion
from .serializers import UsuarioSerializer, AyudanteSerializer, PostulacionSerializer
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.decorators import login_required

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
    

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def obtener_ayudante(request, id):
    try:
        ayudante = Ayudante.objects.get(pk=id) 
    except Ayudante.DoesNotExist:
        return Response({'error': 'Ayudante no encontrado'}, status=status.HTTP_404_NOT_FOUND)

    serializer = AyudanteSerializer(ayudante)
    return Response(serializer.data)

@api_view(['GET'])
def lista_ayudantes(request):
    ayudantes = Ayudante.objects.all()
    serializer = AyudanteSerializer(ayudantes, many=True)
    return Response(serializer.data)

@login_required
def idAyudante(request):
    correo = request.user.email  # Esto lo entrega Google OAuth
    print("Correo autenticado:", correo)
    try:
        usuario = Usuario.objects.get(correo=correo)
        ayudante = Ayudante.objects.get(id_ayudante=usuario)
        return render(request, 'perfil_ayudante.html', {'user_id': usuario.id_usuario})
    except Usuario.DoesNotExist:
        return render(request, 'perfil_ayudante.html', {'error': 'Usuario no encontrado'})
    except Ayudante.DoesNotExist:
        return render(request, 'perfil_ayudante.html', {'error': 'Ayudante no encontrado'})
    
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def ayudante_autenticado(request):
    correo = request.user.email
    try:
        usuario = Usuario.objects.get(correo=correo)
        ayudante = Ayudante.objects.get(id_ayudante=usuario)
        serializer = AyudanteSerializer(ayudante)
        return Response(serializer.data)
    except Usuario.DoesNotExist:
        return Response({'error': 'Usuario no encontrado'}, status=404)
    except Ayudante.DoesNotExist:
        return Response({'error': 'Ayudante no encontrado'}, status=404)


class PostulacionViewSet(viewsets.ModelViewSet):
    queryset = Postulacion.objects.all()
    serializer_class = PostulacionSerializer
