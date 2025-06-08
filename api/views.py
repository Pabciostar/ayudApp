from django.shortcuts import redirect, render
from rest_framework import viewsets, status
from core.models import Usuario, Ayudante, Postulacion
from .serializers import UsuarioSerializer, AyudanteSerializer, PostulacionSerializer
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from rest_framework.parsers import MultiPartParser, FormParser
from django.db.models import Q

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
    query = request.GET.get('q', '').strip()

    if query:
        try:
            valor = int(query)
        except ValueError:
            valor = None

        filtros = Q(id_ayudante__nombres__icontains=query) | \
                  Q(id_ayudante__apellidos__icontains=query) | \
                  Q(carrera__icontains=query) | \
                  Q(ramos__icontains=query) | \
                  Q(valor__icontains=query)
        if valor is not None:
            filtros |= Q(valor=valor)

        ayudantes = Ayudante.objects.filter(filtros)[:10]
    else:
        ayudantes = Ayudante.objects.all()[:10]

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
    
@api_view(['GET', 'PATCH'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser]) 
def ayudante_autenticado(request):
    correo = request.user.email
    try:
        usuario = Usuario.objects.get(correo=correo)
        ayudante = Ayudante.objects.get(id_ayudante=usuario)

        if request.method == 'GET':
            serializer = AyudanteSerializer(ayudante)
            return Response(serializer.data)
        
        elif request.method == 'PATCH':
            if 'foto_perfil' in request.FILES:
                ayudante.foto = request.FILES['foto_perfil'].read()
                
            serializer = AyudanteSerializer(ayudante, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=400)
    
    except Usuario.DoesNotExist:
        return Response({'error': 'Usuario no encontrado'}, status=404)
    except Ayudante.DoesNotExist:
        return Response({'error': 'Ayudante no encontrado'}, status=404)


class PostulacionViewSet(viewsets.ModelViewSet):
    queryset = Postulacion.objects.all()
    serializer_class = PostulacionSerializer


@login_required
def perfilAyudante(request):
    correo = request.user.email
    try:
        usuario = Usuario.objects.get(correo=correo)
        ayudante = Ayudante.objects.get(id_ayudante=usuario)

        if request.method == 'POST':
            ayudante.cuentanos = request.POST.get('descripcion', ayudante.cuentanos)
            ayudante.disponibilidad = request.POST.get('disponibilidad', ayudante.disponibilidad)

            # Limpiar y convertir el valor a número
            valor_str = request.POST.get('valor', ayudante.valor)
            try:
                ayudante.valor = int(valor_str.replace('$', '').replace('.', '').strip())
            except ValueError:
                pass  # opcional: mostrar un mensaje de error si el valor es inválido

            # Foto de perfil (opcional)
            if 'foto_perfil' in request.FILES:
                ayudante.foto = request.FILES['foto_perfil'].read()

            ayudante.save()
            messages.success(request, 'Perfil actualizado exitosamente.')
            return redirect('perfilAyudante')  # asegúrate que esto coincida con tu url name

        return render(request, 'perfil_ayudante.html', {
            'ayudante': ayudante,
            'usuario': usuario,
        })

    except Usuario.DoesNotExist:
        return render(request, 'perfil_ayudante.html', {'error': 'Usuario no encontrado'})
    except Ayudante.DoesNotExist:
        return render(request, 'perfil_ayudante.html', {'error': 'Ayudante no encontrado'})