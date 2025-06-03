from django.conf import settings
from django.shortcuts import redirect, render
from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from django.http import HttpResponse
from google_auth_oauthlib.flow import Flow
from django.contrib.auth.decorators import login_required
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
    try:
        state = request.session['oauth_state']
    except KeyError:
        return HttpResponse("Error: No se encontró el estado de autenticación. Intenta iniciar sesión desde el botón de Google.")
    
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
        scopes=['https://www.googleapis.com/auth/userinfo.email', 'https://www.googleapis.com/auth/userinfo.profile', 'openid'],
        state=state
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

    return redirect('buscador')

def logout_view(request):
    logout(request)
    return redirect('inicio')

# Create your views here.
def inicio(request):
    return render(request, 'inicio.html')

@login_required
def buscador_view(request):
    return render(request, 'buscador.html')

def buscador_view(request):
    return render(request, 'buscador.html')

def postulacionAyudante_view(request):
    return render(request, 'postulacionAyudante.html')

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
    return render(request, 'detallePostulacion.html')

def editarPerfilAyudante_view(request):
    return render(request, 'editarPerfilAyudante.html')

def registro_view(request):
    return render(request, 'registro.html')

def seccionarFechaClase_view(request):
    return render(request, 'seleccionarFechaClase.html')