from django.shortcuts import redirect, render
from rest_framework import viewsets, status, generics
from core.models import Usuario, Ayudante, Postulacion, Notificacion, Evaluacion, ClaseAgendada
from .serializers import EvaluacionSerializer, MejorAyudanteSerializer, UsuarioSerializer, AyudanteSerializer, PostulacionSerializer, NotificacionSerializer, ClaseAgendadaSerializer
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from rest_framework.parsers import MultiPartParser, FormParser
from django.db.models import Q, Func
from decimal import Decimal  
from django.db.models.functions import Lower
from collections import defaultdict

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


class Unaccent(Func):
    function = 'unaccent'
    template = "%(function)s(%(expressions)s)"


@api_view(['GET'])
def lista_ayudantes(request):
    query = request.GET.get('q', '').strip().lower()

    if query:
        try:
            valor = int(query)
        except ValueError:
            valor = None

        palabras = query.split()
        filtros = Q()

        for palabra in palabras:
            filtros |= Q(carrera__unaccent__icontains=palabra)
            filtros |= Q(ramos__unaccent__icontains=palabra)
            filtros |= Q(valor__icontains=palabra)
            filtros |= Q(id_ayudante__nombres__unaccent__icontains=palabra)
            filtros |= Q(id_ayudante__apellidos__unaccent__icontains=palabra)

        ayudantes = Ayudante.objects.annotate(
            carrera_unaccent=Unaccent(Lower('carrera')),
            ramos_unaccent=Unaccent(Lower('ramos')),
            nombres_unaccent=Unaccent(Lower('id_ayudante__nombres')),
            apellidos_unaccent=Unaccent(Lower('id_ayudante__apellidos'))
        ).filter(
            Q(carrera_unaccent__icontains=query) |
            Q(ramos_unaccent__icontains=query) |
            Q(nombres_unaccent__icontains=query) |
            Q(apellidos_unaccent__icontains=query)
        ).distinct()[:10]

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
    

@api_view(['GET'])
@permission_classes([AllowAny])
def perfil_publico_ayudante(request, id):
    try:
        ayudante = Ayudante.objects.get(pk=id)
        serializer = AyudanteSerializer(ayudante)
        return Response(serializer.data)
    except Ayudante.DoesNotExist:
        return Response({'error': 'Ayudante no encontrado'}, status=404)
    

class NotificacionesPorUsuarioAPIView(generics.ListAPIView):
    serializer_class = NotificacionSerializer

    def get_queryset(self):
        user_id = self.kwargs['user_id']
        return Notificacion.objects.filter(destinatario=user_id).order_by('-fecha')


class DetalleNotificacionAPIView(generics.RetrieveAPIView):
    queryset = Notificacion.objects.all()
    serializer_class = NotificacionSerializer
    lookup_field = 'id_notificacion'


@api_view(['GET'])
def mejores_ayudantes_view(request):
    evaluaciones = Evaluacion.objects.all()


    valoraciones_por_ayudante = defaultdict(list)

    for evaluacion in evaluaciones:
        clase_evaluada = evaluacion.clase_agendada_id_clase
        if clase_evaluada:
            clase_agendada = ClaseAgendada.objects.get(id_clase=clase_evaluada)
            ayudante = clase_agendada.id_ayudante
            valoraciones_por_ayudante[ayudante.id_ayudante].append(float(evaluacion.valoracion))

    # Calculamos promedios
    promedios = {
        aid: sum(valores) / len(valores)
        for aid, valores in valoraciones_por_ayudante.items()
        if valores
    }

    # Obtenemos los 9 mejores ayudantes
    ids_ordenados = sorted(promedios.keys(), key=lambda x: promedios[x], reverse=True)[:9]
    ayudantes = Ayudante.objects.filter(id_ayudante__in=ids_ordenados)

    # Aquí puedes crear una lista con datos extra (nombre, foto, etc.)
    resultado = [
        {
            'id': a.id_ayudante,
            'promedio': round(promedios[a.id_ayudante], 1)
        }
        for a in ayudantes
    ]

    serializer = MejorAyudanteSerializer(resultado, many=True)
        
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def clases_agendadas_por_usuario_ayudante(request, usuario_id):
    try:
        clases_estudiante = ClaseAgendada.objects.filter(usuario_id_usuario=usuario_id)

        clases_ayudante = ClaseAgendada.objects.filter(id_ayudante__id_ayudante=usuario_id)

        clases = (clases_estudiante | clases_ayudante).distinct()

        serializer = ClaseAgendadaSerializer(clases, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def guardar_evaluacion(request):
    data = dict(request.data)
    
    try:
        data['valoracion'] = Decimal(data['valoracion'])
        data['clase_agendada_id_clase'] = Decimal(data['clase_agendada_id_clase'])
    except Exception as e:
        return Response({'error': 'Datos inválidos'}, status=400)
    
    if Evaluacion.objects.filter(clase_agendada_id_clase=data['clase_agendada_id_clase']).exists():
        return Response({'error': 'Esta clase ya fue evaluada'}, status=400)
    serializer = EvaluacionSerializer(data=data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
