import base64
from django.shortcuts import get_object_or_404, redirect, render
from rest_framework import viewsets, status, generics
from core.models import Usuario, Ayudante, Postulacion, Notificacion, Evaluacion, ClaseAgendada, Materia, Transaccion
from .serializers import ( 
    EvaluacionSerializer, 
    MejorAyudanteSerializer, 
    UsuarioSerializer, 
    AyudanteSerializer, 
    PostulacionSerializer, 
    NotificacionSerializer, 
    ClaseAgendadaSerializer,
    MateriaSerializer,
    TransaccionSerializer
)
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
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from core.utils import crear_notificacion, generar_nueva_evaluacion
from django.views.decorators.http import require_http_methods
import json

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
@login_required
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

@api_view(['GET'])
@login_required
def notificaciones_por_usuario(request, user_id):
    notificaciones = Notificacion.objects.filter(destinatario=user_id).order_by('-fecha')
    serializer = NotificacionSerializer(notificaciones, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@login_required
def detalle_notificacion(request, id_notificacion):
    try:
        notificacion = Notificacion.objects.get(id_notificacion=id_notificacion)
    except Notificacion.DoesNotExist:
        return Response({'error': 'Notificación no encontrada'}, status=404)

    serializer = NotificacionSerializer(notificacion)
    return Response(serializer.data)

def obtener_imagen_base64(foto_binaria):
    if foto_binaria:
        base64_str = base64.b64encode(foto_binaria).decode('utf-8')
        return f"data:image/jpeg;base64,{base64_str}"
    return None


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
        'id': a.id_ayudante.id_usuario,
        'nombre': f"{a.id_ayudante.nombres} {a.id_ayudante.apellidos}",
        'descripcion': f"{a.cuentanos}",
        'ramos': f"{a.ramos}",
        'promedio': round(promedios[a.id_ayudante], 1),
        'imagen_url': obtener_imagen_base64(a.foto)
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
        
        clases = clases.select_related('materia_id_materia')

        serializer = ClaseAgendadaSerializer(clases, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@login_required
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


@api_view(['GET'])
def detalle_clase_api(request, id_clase):
    try:
        clase = ClaseAgendada.objects.get(id_clase=id_clase)
    except ClaseAgendada.DoesNotExist:
        return Response({'error': 'Clase no encontrada'}, status=status.HTTP_404_NOT_FOUND)

    serializer = ClaseAgendadaSerializer(clase)
    return Response(serializer.data)

class MateriaViewSet(viewsets.ModelViewSet):
    queryset = Materia.objects.all()
    serializer_class = MateriaSerializer

class TransaccionViewSet(viewsets.ModelViewSet):
    queryset = Transaccion.objects.all()
    serializer_class = TransaccionSerializer

@api_view(['GET'])
def clases_agendadas(request):
    clases = ClaseAgendada.objects.select_related('transaccion_id_transaccion', 'id_ayudante__id_ayudante', 'usuario_id_usuario').all()
    serializer = ClaseAgendadaSerializer(clases, many=True)
    return Response(serializer.data)

class EvaluacionViewSet(viewsets.ModelViewSet):
    queryset = Evaluacion.objects.all()
    serializer_class = EvaluacionSerializer


@csrf_exempt
def recibir_calificacion(request, notif_id):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            nota = int(data.get('nota'))
            comentario = data.get('comentario', '').strip()
            
            # Obtenemos la notificación (y con ella, la clase agendada)
            notificacion = Notificacion.objects.get(id_notificacion=notif_id)

            # Llamamos a una función auxiliar para crear la evaluación
            exito = generar_nueva_evaluacion(
                clase_id=notificacion.clase_agendada_id_clase,
                estudiante_id=int(notificacion.destinatario),
                nota=nota,
                comentario=comentario
            )

            if not exito:
                return JsonResponse({'error': 'Ya existe una evaluación para esta clase.'}, status=400)

            return JsonResponse({'mensaje': 'Calificación guardada correctamente.'})
        except Exception as e:
            return JsonResponse({'error': f'Error al procesar la calificación: {str(e)}'}, status=500)
    else:
        return JsonResponse({'error': 'Método no permitido.'}, status=405)
    
@api_view(['GET'])
def listar_notificaciones(request):
    try:
        notificaciones = Notificacion.objects.all().order_by('-fecha')
        serializer = NotificacionSerializer(notificaciones, many=True)
        return Response(serializer.data)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

@csrf_exempt
@require_http_methods(["POST"])
def reportar_problema(request, clase_id):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            motivo = data.get("motivo")
            descripcion_usuario = data.get("descripcion", "").strip()

            # Obtenemos la clase agendada
            clase = get_object_or_404(ClaseAgendada, id_clase=clase_id)

            # El remitente es el estudiante que está logueado
            correo = request.user.email
            usuario = Usuario.objects.get(correo=correo)
            estudiante_id = usuario.id_usuario
            

            # Creamos la notificación
            exito = generar_reporte(
                clase_id=clase.id_clase,
                estudiante_id=estudiante_id,
                motivo=motivo,
                descripcion_usuario=descripcion_usuario
            )

            if exito:
                return JsonResponse({"mensaje": "Reporte creado correctamente."})
            else:
                return JsonResponse({"error": "Ya existe un reporte para esta clase."}, status=400)

        except Exception as e:
            return JsonResponse({"error": f"Error al procesar el reporte: {str(e)}"}, status=500)
    else:
        return JsonResponse({"error": "Método no permitido."}, status=405)


def generar_reporte(clase_id, estudiante_id, motivo, descripcion_usuario=None):
    
    ya_existe = Notificacion.objects.filter(
        clase_agendada_id_clase=clase_id,
        destinatario=estudiante_id,
        asunto="Reclamo clase"
    ).exists()

    if ya_existe:
        return False

    razon = {
        "el_ayudante_no_se_presento": "El ayudante no se presentó.",
        "no_dominio_materia": "El ayudante no mostró dominio de la materia.",
        "lenguaje_inapropiado": "El ayudante usó lenguaje inapropiado.",
        "clase_no_finalizada": "El ayudante no terminó la clase.",
        "otro": f"Otra razón: {descripcion_usuario or 'Sin detalles'}"
    }

    mensaje_cuerpo = razon.get(motivo, "Razón desconocida")

    try:
        crear_notificacion(
            asunto="Reclamo clase",
            remitente=estudiante_id,
            destinatario="administrador",
            cuerpo=mensaje_cuerpo,
            clase_agendada=clase_id
        )

        return True
    except Exception as e:
        return False