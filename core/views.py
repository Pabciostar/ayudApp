from django.conf import settings
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from django.http import HttpResponse, JsonResponse
from google_auth_oauthlib.flow import Flow
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.utils.timezone import make_aware
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from .models import Usuario, Postulacion, Ayudante, GoogleCalendarToken, Disponibilidad, Materia, ClaseAgendada, Transaccion
from .forms import DatosAdicionalesForm, PostulacionForm
from datetime import datetime, timedelta, time
from .paypal_client import PayPalClient
from paypalrestsdk import Payment
import paypalrestsdk
import google.auth.transport.requests
import requests
import os
import json

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
        include_granted_scopes='true',
        prompt='consent'
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

        if Ayudante.objects.filter(id_ayudante=usuario).exists():

            token_expiry = credentials.expiry
            
            if timezone.is_naive(token_expiry):
                token_expiry = timezone.make_aware(token_expiry)
            
            GoogleCalendarToken.objects.update_or_create(
                usuario=usuario,
                defaults={
                    'access_token': credentials.token,
                    'refresh_token': credentials.refresh_token,
                    'token_expiry': credentials.expiry,  # esto ya es datetime con timezone
                    'updated_at': timezone.now()
                }
            )
        return redirect('buscador')
    except Usuario.DoesNotExist:
        return redirect('completar_datos')


def get_calendar_service(usuario):
    token = GoogleCalendarToken.objects.get(usuario=usuario)
    creds = Credentials(
        token=token.access_token,
        refresh_token=token.refresh_token,
        token_uri='https://oauth2.googleapis.com/token',
        client_id=settings.GOOGLE_CLIENT_ID,
        client_secret=settings.GOOGLE_CLIENT_SECRET,
        scopes=['https://www.googleapis.com/auth/calendar'],
    )
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        token.access_token = creds.token
        token.token_expiry = creds.expiry
        token.updated_at = timezone.now()
        token.save()
    return build('calendar', 'v3', credentials=creds)    


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

def perfil_ayudante_html(request, id):
    return render(request, 'perfilAyudante.html', {'ayudante_id': id})

@csrf_exempt
@login_required
def seccionarFechaClase_view(request):
    try:
        usuario = Usuario.objects.get(correo=request.user.email)
    except Usuario.DoesNotExist:
        return render(request, 'error.html', {'mensaje': 'No tienes un perfil de usuario registrado.'})

    try:
        ayudante = Ayudante.objects.get(id_ayudante=usuario)
    except Ayudante.DoesNotExist:
        return render(request, 'error.html', {'mensaje': 'No estás registrado como ayudante.'})

    materias = Materia.objects.filter(ayudante_id_ayudante=ayudante)

    if request.method == 'POST':
        materia_id = request.POST.get('materia_id')
        fecha_str = request.POST.get('fecha')
        hora_str = request.POST.get('hora')
        duracion = request.POST.get('duracion_min')
        
        if not fecha_str or not hora_str or not duracion or not materia_id:
            return render(request, 'seleccionarFechaClase.html', {
                'clases': Disponibilidad.objects.filter(ayudante=ayudante),
                'materias': materias,
                'error': 'Todos los campos son obligatorios'
            })

        try:
            materia = Materia.objects.get(id_materia=materia_id)
            duracion = int(duracion)
            fecha = datetime.strptime(fecha_str, "%Y-%m-%d").date()
            hora_inicio_dt = datetime.strptime(hora_str, "%H:%M").time()
            hora_inicio = datetime.combine(fecha, hora_inicio_dt)


            disponibilidad = Disponibilidad.objects.create(
                ayudante=ayudante,
                materia=materia, 
                fecha=fecha,
                hora_inicio=hora_inicio.time(),
                duracion_min=duracion
            )
            disponibilidad.save()

            return redirect('seleccionarFechaClase')
        except Exception as e:
            return render(request, 'seleccionarFechaClase.html', {
                'clases': Disponibilidad.objects.filter(ayudante=ayudante),
                'materias': materias,
                'error': f'Error al guardar: {str(e)}'
            })

    clases = Disponibilidad.objects.filter(ayudante=ayudante).order_by('fecha', 'hora_inicio')
    return render(request, 'seleccionarFechaClase.html', {
        'clases': clases,
        'materias': materias
    })

@login_required
def agendarClase_view(request, id_ayudante):
    try:
        usuario = get_object_or_404(Usuario, correo=request.user.email)
        ayudante = get_object_or_404(Ayudante, pk=id_ayudante)
        materias = Materia.objects.filter(ayudante_id_ayudante=ayudante)
        disponibilidades = Disponibilidad.objects.filter(
            ayudante=ayudante,
            disponible=True
        ).order_by('fecha', 'hora_inicio')

        if request.method == 'POST':
            materia_id = request.POST.get('materia_id')
            fecha = request.POST.get('fecha')
            hora = request.POST.get('hora')
            duracion_min = request.POST.get('duracion_min')

            if not all([materia_id, fecha, hora, duracion_min]):
                return render(request, 'agendarClase.html', {
                    'ayudante': ayudante,
                    'materias': materias,
                    'disponibilidades': disponibilidades,
                    'error': 'Todos los campos son obligatorios.'
                })

            # Guardar datos en la sesión temporalmente
            request.session['datos_clase'] = {
                'materia_id': materia_id,
                'fecha': fecha,
                'hora': hora,
                'duracion_min': duracion_min,
                'ayudante_id': ayudante.pk
            }

            return redirect('pago_clase')

        return render(request, 'agendarClase.html', {
            'ayudante': ayudante,
            'materias': materias,
            'disponibilidades': disponibilidades
        })

    except Exception as e:
        return render(request, 'error.html', {'mensaje': f'Error: {e}'})


paypalrestsdk.configure({
    "mode": "sandbox",  # Cambia a 'live' en producción
    "client_id": settings.PAYPAL_CLIENT_ID,
    "client_secret": settings.PAYPAL_CLIENT_SECRET,
})


@login_required
def pagar_clase_view(request):
    datos = request.session.get('datos_clase')
    if not datos:
        return render(request, 'error.html', {'mensaje': 'No se encontraron datos de clase.'})

    materia = get_object_or_404(Materia, pk=datos['materia_id'])
    ayudante = get_object_or_404(Ayudante, pk=datos['ayudante_id'])
    usuario = get_object_or_404(Usuario, correo=request.user.email)
    monto = float(ayudante.valor)
    moneda = 'USD'

    payment = Payment({
        "intent": "sale",
        "payer": {"payment_method": "paypal"},
        "redirect_urls": {
            "return_url": request.build_absolute_uri('/paypal-return/'),
            "cancel_url": request.build_absolute_uri('/paypal-cancel/')
        },
        "transactions": [{
            "item_list": {
                "items": [{
                    "name": f"Clase con {ayudante.id_ayudante.nombres}",
                    "sku": "001",
                    "price": str(monto),
                    "currency": moneda,
                    "quantity": 1
                }]
            },
            "amount": {
                "total": str(monto),
                "currency": moneda
            },
            "description": "Pago de clase agendada"
        }]
    })

    if payment.create():
        transaccion = Transaccion.objects.create(
            payment_id=payment.id,
            estado=payment.state,
            monto=monto,
            moneda=moneda,
            usuario=usuario
        )

        # Guardar ID transacción temporalmente
        request.session['transaccion_id'] = transaccion.id_transaccion

        for link in payment.links:
            if link.rel == "approval_url":
                return redirect(link.href)
        return render(request, 'error_pago.html', {'error': 'No se encontró URL de aprobación.'})
    else:
        return render(request, 'error_pago.html', {"error": payment.error})


def paypal_cancel_view(request):
    return render(request, 'pago_cancelado.html')

@login_required
def paypal_return_view(request):
    payment_id = request.GET.get('paymentId')
    payer_id = request.GET.get('PayerID')

    datos = request.session.get('datos_clase')
    transaccion_id = request.session.get('transaccion_id')

    if not datos or not transaccion_id:
        return render(request, 'error.html', {'mensaje': 'Faltan datos para finalizar la clase.'})

    payment = Payment.find(payment_id)

    if payment.execute({"payer_id": payer_id}):
        transaccion = get_object_or_404(Transaccion, pk=transaccion_id)
        transaccion.estado = 'approved'
        transaccion.save()

        usuario = get_object_or_404(Usuario, correo=request.user.email)
        ayudante = get_object_or_404(Ayudante, pk=datos['ayudante_id'])
        materia = get_object_or_404(Materia, pk=datos['materia_id'])

        fecha_obj = datetime.strptime(datos['fecha'], "%Y-%m-%d").date()
        hora_obj = datetime.strptime(datos['hora'], "%H:%M").time()

        clase = ClaseAgendada.objects.create(
            id_clase=int(datetime.now().strftime('%y%m%d%H%M%S')),
            fecha=fecha_obj,
            hora=hora_obj,
            duracion_min=int(datos['duracion_min']),
            valor=transaccion.monto,
            materia_id_materia=materia,
            usuario_id_usuario=usuario,
            transaccion_id_transaccion=transaccion,
            id_ayudante=ayudante
        )

        # Crear evento en Google Calendar
        crear_evento_google(clase)

        # Limpiar sesión
        request.session.pop('datos_clase', None)
        request.session.pop('transaccion_id', None)

        # Mostrar éxito y datos
        return render(request, 'pago_exitoso.html', {'clase': clase})
    else:
        return render(request, 'error_pago.html', {'error': payment.error})

   
def crear_evento_google(clase):
    try:
        ayudante = clase.id_ayudante.id_ayudante
        cred = GoogleCalendarToken.objects.get(usuario=ayudante.id_ayudante)

        credentials = Credentials(
            token=cred.access_token,
            refresh_token=cred.refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=settings.GOOGLE_CLIENT_ID,
            client_secret=settings.GOOGLE_CLIENT_SECRET,
            scopes=['https://www.googleapis.com/auth/calendar']
        )

        if credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
            cred.access_token = credentials.token
            cred.token_expiry = credentials.expiry
            cred.updated_at = timezone.now()
            cred.save()

        service = build("calendar", "v3", credentials=credentials)

        fecha_inicio = datetime.combine(clase.fecha, clase.hora)

        # Buscar la disponibilidad relacionada
        disponibilidad = Disponibilidad.objects.filter(
            ayudante=ayudante,
            fecha=clase.fecha,
            hora_inicio=clase.hora
        ).first()

        fecha_fin = fecha_inicio + timedelta(minutes=clase.duracion_min)

        evento = {
            'summary': f"Clase con estudiante {clase.usuario_id_usuario.nombres}",
            'description': f"Materia: {clase.materia_id_materia.nombre}",
            'start': {
                'dateTime': fecha_inicio.isoformat(),
                'timeZone': 'America/Santiago',
            },
            'end': {
                'dateTime': fecha_fin.isoformat(),
                'timeZone': 'America/Santiago',
            },
        }

        service.events().insert(calendarId='primary', body=evento).execute()

    except Exception as e:
        print("Error al crear evento en Google Calendar:", e)


@csrf_exempt
def paypal_webhook(request):
    if request.method == 'POST':
        try:
            webhook_id = os.getenv('PAYPAL_WEBHOOK_ID')
            body = json.loads(request.body.decode('utf-8'))

            paypal = PayPalClient()
            headers = {
                'Paypal-Transmission-Id': request.headers.get('Paypal-Transmission-Id'),
                'Paypal-Transmission-Time': request.headers.get('Paypal-Transmission-Time'),
                'Paypal-Transmission-Sig': request.headers.get('Paypal-Transmission-Sig'),
                'Paypal-Cert-Url': request.headers.get('Paypal-Cert-Url')
            }

            verified = paypal.get_paypal_client().notifications.WebhookEvent.verify(
                headers['Paypal-Transmission-Id'],
                headers['Paypal-Transmission-Time'],
                headers['Paypal-Transmission-Sig'],
                webhook_id,
                body
            )

            if verified:
                event_type = body.get('event_type')
                resource = body.get('resource')

                if event_type == 'PAYMENT.SALE.COMPLETED':
                    payment_id = resource.get('parent_payment')
                    transaccion = Transaccion.objects.filter(id_transaccion=payment_id).first()
                    if transaccion:
                        transaccion.estado = 'completed'
                        transaccion.save()

                return JsonResponse({"status": "success"})

            return JsonResponse({"status": "verification failed"}, status=400)

        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=400)

    return JsonResponse({"status": "method not allowed"}, status=405)
