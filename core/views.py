from django.conf import settings
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from django.http import HttpResponse, JsonResponse
from google_auth_oauthlib.flow import Flow
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from .models import Usuario, Postulacion, Ayudante
from .forms import DatosAdicionalesForm, PostulacionForm
from datetime import datetime
import google.auth.transport.requests
import requests
import os

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'  # Solo para pruebas locales (HTTP)

def login_with_google(request):
    flow = Flow.from_client_config(
        {
            "web": {
                "client_id": settings.GOOGLE_CLIENT_ID,
                "client_secret": settings.GOOGLE_CLIENT_SECRET,
                "redirect_uris": [settings.GOOGLE_REDIRECT_URI],
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token"
            }
        },
       scopes=['https://www.googleapis.com/auth/userinfo.email', 'https://www.googleapis.com/auth/userinfo.profile', 'openid', 'https://www.googleapis.com/auth/calendar']
       )

    flow.redirect_uri = settings.GOOGLE_REDIRECT_URI

    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true'
    )

    request.session['oauth_state'] = state
    return redirect(authorization_url)


def oauth2callback(request):
    session_state = request.session.get('oauth_state')
    request_state = request.GET.get('state')

    if not session_state or not request_state:
        return HttpResponse("Error: Estado de autenticación faltante.")
    
    if session_state != request_state:
        return HttpResponse("Error: El estado recibido no coincide. Intenta iniciar sesión nuevamente.")
    
    flow = Flow.from_client_config(
        {
            "web": {
                "client_id": settings.GOOGLE_CLIENT_ID,
                "client_secret": settings.GOOGLE_CLIENT_SECRET,
                "redirect_uris": [settings.GOOGLE_REDIRECT_URI],
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token"
            }
        },
        scopes=['https://www.googleapis.com/auth/userinfo.email', 'https://www.googleapis.com/auth/userinfo.profile', 'openid', 'https://www.googleapis.com/auth/calendar'],
        state=session_state
    )
    flow.redirect_uri = settings.GOOGLE_REDIRECT_URI

    authorization_response = request.build_absolute_uri()
    flow.fetch_token(authorization_response=authorization_response)

    credentials = flow.credentials
    session = requests.Session()
    session.headers.update({'Authorization': f'Bearer {credentials.token}'})
    userinfo_response = session.get('https://www.googleapis.com/userinfo/v2/me')

    if userinfo_response.status_code != 200:
        return HttpResponse("Error al obtener datos del usuario")
    
    user_info = userinfo_response.json()
    # Aquí puedes manejar el login en Django
    email = user_info['email']
    name = user_info.get('name', email.split('@')[0])

    user, _ = User.objects.get_or_create(username=email, defaults={'first_name': name, 'email': email})
    login(request, user)

    try:
        usuario = Usuario.objects.get(correo=email)
        return redirect('buscador')
    except Usuario.DoesNotExist:
        return redirect('completar_datos')
    
@login_required
def datos_adicionales(request):
    if Usuario.objects.filter(correo=request.user.email).exists():
        return redirect('buscador')

    if request.method == 'POST':
        form = DatosAdicionalesForm(request.POST)
        if form.is_valid():
            usuario = form.save(commit=False)
            usuario.correo = request.user.email
            usuario.id_usuario = usuario.rut_usuario.replace('.', '').split('-')[0]
            usuario.rol = 'estudiante'  # Rol fijo
            usuario.save()
            messages.success(request, 'Tus datos fueron registrados exitosamente.')
            return redirect('buscador')
    else:
        form = DatosAdicionalesForm()

    return render(request, 'registro.html', {'form': form})

@login_required
def completar_datos(request):
    # Si ya tiene un perfil de Usuario, redirige al buscador
    if Usuario.objects.filter(correo=request.user.email).exists():
        return redirect('buscador')
    
    return redirect('datos_adicionales')

def logout_view(request):
    logout(request)
    return redirect('inicio')

# Create your views here.
def inicio(request):
    return render(request, 'inicio.html')

@login_required
def buscador_view(request):
    return render(request, 'buscador.html')

@login_required
def postulacionAyudante_view(request):
    try:
        usuario = Usuario.objects.get(correo=request.user.email)
    except Usuario.DoesNotExist:
        messages.error(request, "No se pudo encontrar tu información como usuario.")
        return redirect('completar_datos')

    # Verifica si ya tiene una postulación
    if Postulacion.objects.filter(usuario_id_usuario=usuario).exists():
        messages.warning(request, "Ya has enviado una postulación.")
        return redirect('buscador')

    if request.method == 'POST':
        form = PostulacionForm(request.POST, request.FILES)
        if form.is_valid():
            postulacion = form.save(commit=False)
            postulacion.usuario_id_usuario = usuario
            postulacion.save()
            messages.success(request, "Postulación enviada correctamente.")
            return redirect('buscador')
    else:
        form = PostulacionForm()

    return render(request, 'postulacionAyudante.html', {'form': form})

def detalleClase_view(request):
    return render(request, 'detalleClase.html')

def perfilAyudante_view(request):
    return render(request, 'perfilAyudante.html')

def panelAdministrador(request):
    return render(request, 'panelAdministrador.html')

def notificaciones_view(request):
    return render(request, 'notificaciones.html')

def notificacion_view(request):
    return render(request, 'notificacion.html')

def mensajeEstudianteAyudado_view(request):
    return render(request, 'mensajeEstudianteAyudante.html')

def detallePostulacion_view(request):
    id_postulacion = request.GET.get('id')
    postulacion = get_object_or_404(Postulacion, id_postulacion=id_postulacion)
    fecha_hora = datetime.strptime(str(postulacion.id_postulacion), '%y%m%d%H%M%S')

    return render(request, 'detallePostulacion.html', {
        'postulacion': postulacion,
        'fecha_hora': fecha_hora,
    })

@csrf_exempt
def aceptar_postulacion(request):
    if request.method == "POST":
        import json
        data = json.loads(request.body)
        id_postulacion = data.get("id_postulacion")

        try:
            postulacion = Postulacion.objects.get(id_postulacion=id_postulacion)
            usuario = postulacion.usuario_id_usuario
            
            foto_bytes = bytes(postulacion.foto) if postulacion.foto else None

            timestamp_validado = datetime.now().strftime('%y%m%d%H%M%S')

            # Crear Ayudante si no existe
            ayudante, created = Ayudante.objects.get_or_create(
                id_ayudante=usuario,
                defaults={
                    'carrera': postulacion.carrera,
                    'foto': foto_bytes,
                    'cuentanos': postulacion.cuentanos,
                    'disponibilidad': postulacion.disponibilidad,
                    'experiencia': postulacion.experiencia,
                    'ramos': postulacion.ramos,
                    'valor': postulacion.valor,
                    'terminos': postulacion.terminos,
                    'validado': timestamp_validado,
                })

            # Cambiar rol del usuario
            usuario.rol = 'ayudante'
            usuario.save()

            # Cambiar estado de la postulación
            Postulacion.objects.filter(id_postulacion=id_postulacion).update(estado='aceptada')

            return JsonResponse({"mensaje": "Postulación aceptada y ayudante creado"})
        except Postulacion.DoesNotExist:
            return JsonResponse({"error": "Postulación no encontrada"}, status=404)
    return JsonResponse({"error": "Método no permitido"}, status=405)

@csrf_exempt
def rechazar_postulacion(request):
    if request.method == "POST":
        import json
        data = json.loads(request.body)
        id_postulacion = data.get("id_postulacion")

        try:
            postulacion = Postulacion.objects.get(id_postulacion=id_postulacion)
            postulacion.estado = 'rechazada'
            postulacion.save(update_fields=['estado'])
            return JsonResponse({"mensaje": "Postulación rechazada"})
        except Postulacion.DoesNotExist:
            return JsonResponse({"error": "Postulación no encontrada"}, status=404)
    return JsonResponse({"error": "Método no permitido"}, status=405)

def editarPerfilAyudante_view(request):
    return render(request, 'editarPerfilAyudante.html')

def registro_view(request):
    return render(request, 'registro.html')

def seccionarFechaClase_view(request):
    return render(request, 'seleccionarFechaClase.html')