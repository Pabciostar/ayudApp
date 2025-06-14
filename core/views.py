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
from django.db.models import Q
from django.views.decorators.http import require_GET
from .models import Usuario, Postulacion, Ayudante, Googlecalendartoken, Disponibilidad, Materia, ClaseAgendada, Transaccion
from .forms import DatosAdicionalesForm, PostulacionForm
from datetime import datetime, timedelta, time
from .paypal_client import PayPalClient
from paypalrestsdk import Payment
from decimal import Decimal
import paypalrestsdk
import google.auth.transport.requests
import requests
import os
import json
from .utils import crear_notificacion, obtener_tasa_clp_usd, obtener_tasa_usd_a_clp
from .decorators import rol_requerido

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
       scopes=['https://www.googleapis.com/auth/userinfo.email', 
               'https://www.googleapis.com/auth/userinfo.profile', 
               'openid', 
               'https://www.googleapis.com/auth/calendar',
               'https://www.googleapis.com/auth/calendar.events']
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
        scopes=['https://www.googleapis.com/auth/userinfo.email', 
                'https://www.googleapis.com/auth/userinfo.profile', 
                'openid', 
                'https://www.googleapis.com/auth/calendar',
                'https://www.googleapis.com/auth/calendar.events'],
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

        request.session['usuario_id'] = usuario.id_usuario

        if Ayudante.objects.filter(id_ayudante=usuario).exists():

            token_expiry = credentials.expiry
            
            if timezone.is_naive(token_expiry):
                token_expiry = timezone.make_aware(token_expiry)
            
            Googlecalendartoken.objects.update_or_create(
                id_usuario=usuario,
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
    token = Googlecalendartoken.objects.get(id_usuario=usuario)
    creds = Credentials(
        token=token.access_token,
        refresh_token=token.refresh_token,
        token_uri='https://oauth2.googleapis.com/token',
        client_id=settings.GOOGLE_CLIENT_ID,
        client_secret=settings.GOOGLE_CLIENT_SECRET,
        scopes=['https://www.googleapis.com/auth/calendar.events'],
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
    try:
        usuario = Usuario.objects.get(correo=request.user.email)
    except Usuario.DoesNotExist:
        messages.error(request, "No se pudo encontrar tu información como usuario.")
        return redirect('completar_datos')
    
    id_usuario = usuario.id_usuario
    
    return render(request, 'buscador.html', {
        'id_usuario': id_usuario
    })

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

            crear_notificacion(
            asunto="Postulación recibida",
            remitente="Admin",
            destinatario=str(usuario.id_usuario),
            cuerpo=f"Su postulación fue enviada exitosamente",
            clase_agendada=None
        )
            return redirect('buscador')
    else:
        form = PostulacionForm()

    return render(request, 'postulacionAyudante.html', {'form': form})

def detalleClase_view(request):
    return render(request, 'detalleClase.html')

def detalleClase_detalle_view(request, id):
    clase = get_object_or_404(ClaseAgendada, id_clase=id)
    return render(request, 'detalleClase.html', {'clase': clase})

def perfilAyudante_view(request):
    return render(request, 'perfilAyudante.html')

def panelAdministrador(request):
    return render(request, 'panelAdministrador.html')

def notificaciones_view(request):
    usuario = Usuario.objects.get(correo=request.user.email)
    return render(request, 'notificaciones.html', {
        'usuario_id': usuario.id_usuario
    })

def detalle_notificacion_view(request, id_notificacion):
    return render(request, 'notificacion.html', {
        'id_notificacion': id_notificacion
    })

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

            crear_notificacion(
                asunto="Postulación aceptada",
                remitente="Admin",  
                destinatario= str(usuario),  
                cuerpo="Su postulación ha sido aceptada",
                clase_agendada=None
            )

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
            usuario = postulacion.usuario_id_usuario
            postulacion.estado = 'rechazada'
            postulacion.save(update_fields=['estado'])

            crear_notificacion(
                asunto="Postulación rechazada",
                remitente="Admin",  
                destinatario= str(usuario),  
                cuerpo="Su postulación ha sido aceptada",
                clase_agendada=None
            )

            return JsonResponse({"mensaje": "Postulación rechazada"})
        
        except Postulacion.DoesNotExist:
            return JsonResponse({"error": "Postulación no encontrada"}, status=404)
    return JsonResponse({"error": "Método no permitido"}, status=405)

def editarPerfilAyudante_view(request):
    return render(request, 'editarPerfilAyudante.html')

def registro_view(request):
    return render(request, 'registro.html')

def perfil_ayudante_html(request, id):
    # 1) Saca el id de tu modelo Usuario desde la sesión
    correo_usuario = request.user.email
    usuario_visitante = get_object_or_404(Usuario, correo=correo_usuario)

    # 2) Carga el ayudante cuyo perfil ves
    ayudante = get_object_or_404(Ayudante, id_ayudante_id=id)
    usuario_perfil = ayudante.id_ayudante  # instancia de Usuario

    return render(request, "perfilAyudante.html", {
        "usuario_visitante": usuario_visitante,
        "usuario_perfil":    usuario_perfil,
        "ayudante":          ayudante,
    })


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
        materia_id = request.POST.get('id_materia')
        fecha_str = request.POST.get('fecha')
        hora_str = request.POST.get('hora_inicio')
        duracion = request.POST.get('duracion_min')
    
        if not fecha_str or not hora_str or not duracion or not materia_id:
            return render(request, 'seleccionarFechaClase.html', {
                'clases': Disponibilidad.objects.filter(id_ayudante=ayudante),  # Cambiado ayudante -> id_ayudante
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
                id_ayudante=ayudante,  
                id_materia=materia,     # Cambiado materia -> id_materia
                fecha=fecha,
                hora_inicio=hora_inicio.time(),
                duracion_min=duracion,
                disponible=True
            )
            disponibilidad.save()

            return redirect('seleccionarFechaClase')
        except Exception as e:
            return render(request, 'seleccionarFechaClase.html', {
                'clases': Disponibilidad.objects.filter(id_ayudante=ayudante),
                'materias': materias,
                'error': f'Error al guardar: {str(e)}'
            })

    clases_agendadas = ClaseAgendada.objects.filter(id_ayudante=ayudante)
    clases_agendadas_q = Q()
    
    for clase in clases_agendadas:
        clases_agendadas_q |= Q(fecha=clase.fecha, hora_inicio=clase.hora)

    clases = Disponibilidad.objects.filter(id_ayudante=ayudante)

    if clases_agendadas_q:
        clases = clases.exclude(clases_agendadas_q)
    
    clases = clases.order_by('fecha', 'hora_inicio')
    
    return render(request, 'seleccionarFechaClase.html', {
        'clases': clases,
        'materias': materias
    })

@login_required
def eliminar_disponibilidad_view(request, id_disponibilidad):
    try:
        usuario = Usuario.objects.get(correo=request.user.email)
        ayudante = Ayudante.objects.get(id_ayudante=usuario)
        disponibilidad = get_object_or_404(Disponibilidad, id_disponibilidad=id_disponibilidad, id_ayudante=ayudante)
        disponibilidad.delete()
        return redirect('seleccionarFechaClase')
    except (Usuario.DoesNotExist, Ayudante.DoesNotExist):
        return render(request, 'error.html', {'mensaje': 'No tienes permiso para eliminar esta disponibilidad.'})


@require_GET
@login_required
def obtener_disponibilidades(request, id_ayudante):
    materia_id = request.GET.get('id_materia')

    if not materia_id:
        return JsonResponse({'error': 'Materia no especificada'}, status=400)

    ayudante = get_object_or_404(Ayudante, id_ayudante_id=id_ayudante)

    disponibilidades = Disponibilidad.objects.filter(
        id_ayudante=ayudante,
        disponible=True,
        id_materia_id=materia_id
    )

    clases_agendadas = ClaseAgendada.objects.filter(
        id_ayudante=ayudante,
        estado='confirmada'
    )

    clases_agendadas_q = Q()
    for clase in clases_agendadas:
        clases_agendadas_q |= Q(fecha=clase.fecha, hora_inicio=clase.hora)

    if clases_agendadas_q:
        disponibilidades = disponibilidades.exclude(clases_agendadas_q)

    data = [{
        'id': d.id_disponibilidad,
        'fecha': d.fecha.strftime('%Y-%m-%d'),
        'hora_inicio': d.hora_inicio.strftime('%H:%M'),
        'duracion': d.duracion_min
    } for d in disponibilidades.order_by('fecha', 'hora_inicio')]

    return JsonResponse({'disponibilidades': data})

@login_required
def agendarClase_view(request, id):
    try:
        usuario = get_object_or_404(Usuario, correo=request.user.email)
        ayudante = get_object_or_404(Ayudante, id_ayudante_id=id)
        materias = Materia.objects.filter(ayudante_id_ayudante=ayudante)

        disponibilidades = Disponibilidad.objects.filter(
            id_ayudante=ayudante,
            disponible=True
        )

        clases_agendadas = ClaseAgendada.objects.filter(
            id_ayudante=ayudante,
            estado='confirmada'
            )
        
        # Generar condiciones de exclusión
        clases_agendadas_q = Q()

        for clase in clases_agendadas:
            clases_agendadas_q |= Q(fecha=clase.fecha, hora_inicio=clase.hora)

        # Excluir disponibilidades ya usadas
        if clases_agendadas_q:
            disponibilidades = disponibilidades.exclude(clases_agendadas_q)

        # Finalmente ordenar
        disponibilidades = disponibilidades.order_by('fecha', 'hora_inicio')
        
        if request.method == 'POST':
            materia_id = request.POST.get('id_materia')
            fecha = request.POST.get('fecha')
            hora_inicio = request.POST.get('hora_inicio')
            duracion_min = request.POST.get('duracion_min')

            if not all([materia_id, fecha, hora_inicio, duracion_min]):
                return render(request, 'agendarClase.html', {
                    'ayudante': ayudante,
                    'materias': materias,
                    'disponibilidades': disponibilidades,
                    'error': 'Todos los campos son obligatorios.'
                })

            # Guardar datos en la sesión temporalmente
            request.session['datos_clase'] = {
                'id_materia': materia_id,
                'fecha': fecha,
                'hora_inicio': hora_inicio,
                'duracion_min': duracion_min,
                'id_ayudante': ayudante.pk
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

    materia = get_object_or_404(Materia, pk=datos['id_materia'])
    ayudante = get_object_or_404(Ayudante, pk=datos['id_ayudante'])
    usuario = get_object_or_404(Usuario, correo=request.user.email)
    monto = Decimal(ayudante.valor)
    moneda = 'USD'

    tasa = obtener_tasa_clp_usd()
    if tasa is None:
        return render(request, 'pago_cancelado.html', {'error': 'No se pudo obtener la tasa de cambio'})
    
    valor_usd = (monto * tasa).quantize(Decimal('0.01'))

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
                    "price": str(valor_usd),
                    "currency": moneda,
                    "quantity": 1
                }]
            },
            "amount": {
                "total": str(valor_usd),
                "currency": moneda
            },
            "description": "Pago de clase agendada"
        }]
    })

    if payment.create():
        transaccion = Transaccion.objects.create(
            id_payment=payment.id,
            estado=payment.state,
            monto=valor_usd,
            moneda=moneda,
            id_usuario=usuario
        )

        # Guardar ID transacción temporalmente
        request.session['id_transaccion'] = transaccion.id_transaccion

        for link in payment.links:
            if link.rel == "approval_url":
                return redirect(link.href)
        return render(request, 'error_pago.html', {'error': 'No se encontró URL de aprobación.'})
    else:
        return render(request, 'error_pago.html', {"error": payment.error})


def paypal_cancel_view(request):
    request.session.pop('datos_clase', None)
    request.session.pop('id_transaccion', None)
    return render(request, 'pago_cancelado.html')
  

@login_required
def paypal_return_view(request):
    payment_id = request.GET.get('paymentId')
    payer_id = request.GET.get('PayerID')

    datos = request.session.get('datos_clase')
    id_transaccion = request.session.get('id_transaccion')

    if not datos or not id_transaccion:
        return render(request, 'error.html', {'mensaje': 'Faltan datos para finalizar la clase.'})

    payment = Payment.find(payment_id)

    if payment.execute({"payer_id": payer_id}):
        transaccion = get_object_or_404(Transaccion, pk=id_transaccion)
        transaccion.estado = 'approved'
        transaccion.save()

        usuario = get_object_or_404(Usuario, correo=request.user.email)
        ayudante = get_object_or_404(Ayudante, pk=datos['id_ayudante'])
        materia = get_object_or_404(Materia, pk=datos['id_materia'])

        fecha_obj = datetime.strptime(datos['fecha'], "%Y-%m-%d").date()
        hora_obj = datetime.strptime(datos['hora_inicio'], "%H:%M").time()

        tasa_usd_a_clp = obtener_tasa_usd_a_clp()
        if tasa_usd_a_clp is None:
            return render(request, 'error_pago.html', {'error': 'No se pudo obtener la tasa de cambio desde mindicador.cl'})

        valor_en_clp = (transaccion.monto * tasa_usd_a_clp).quantize(Decimal('0.01'))

        clase = ClaseAgendada.objects.create(
            id_clase=int(datetime.now().strftime('%y%m%d%H%M%S')),
            fecha=fecha_obj,
            hora=hora_obj,
            duracion_min=int(datos['duracion_min']),
            valor=valor_en_clp,
            materia_id_materia=materia,
            usuario_id_usuario=usuario,
            transaccion_id_transaccion=transaccion,
            id_ayudante=ayudante
        )

        # Crear evento en Google Calendar
        enlace_meet = crear_evento_google(clase)
        if enlace_meet:
            clase.link_meet = enlace_meet
            clase.save()

        # Limpiar sesión
        request.session.pop('datos_clase', None)
        request.session.pop('id_transaccion', None)

        crear_notificacion("Se agendó una nueva clase", "Administrador", usuario.id_usuario, f"Se ha agendado exitosamente una clase para el día {fecha_obj}, sobre la materia de {materia}. Recuerda conectarte a tiempo.", clase.id_clase)
        crear_notificacion("Se agendó una nueva clase", "Administrador", ayudante.id_ayudante.id_usuario, f"Se ha agendado exitosamente una clase para el día {fecha_obj}, sobre la materia de {materia}. Recuerda conectarte a tiempo.", clase.id_clase)
        # Mostrar éxito y datos
        return render(request, 'pago_exitoso.html', {'clase': clase})
    else:
        return render(request, 'error_pago.html', {'error': payment.error})

   
def crear_evento_google(clase):
    try:
        ayudante = clase.id_ayudante
        usuario_ayudante = ayudante.id_ayudante
        cred = Googlecalendartoken.objects.get(id_usuario=usuario_ayudante)

        credentials = Credentials(
            token=cred.access_token,
            refresh_token=cred.refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=settings.GOOGLE_CLIENT_ID,
            client_secret=settings.GOOGLE_CLIENT_SECRET,
            scopes=['https://www.googleapis.com/auth/calendar.events']
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
            id_ayudante=ayudante,
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
            'attendees': [
                {'email': clase.usuario_id_usuario.correo},
            ],
            'conferenceData': {
                'createRequest': {
                    'requestId': f"clase-{clase.id_clase}",  # Debe ser único por evento
                    'conferenceSolutionKey': {'type': 'hangoutsMeet'}
                }
            }
        }
        

        evento_creado = service.events().insert(calendarId='primary', body=evento, conferenceDataVersion=1).execute()
        enlace_meet = evento_creado.get('hangoutLink', None)
        clase.evento_google_id = evento_creado.get('id')
        clase.save()

        print("Enlace de Google Meet:", enlace_meet)
        return enlace_meet 
    except Exception as e:
        print("Error al crear evento en Google Calendar:", e)
        return None


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

def detalleClase_detalle_view(request, id):
    clase = get_object_or_404(ClaseAgendada, id_clase=id)
    ayudante = get_object_or_404(Ayudante, id_ayudante =clase.id_ayudante)
    usuario_ayudante = ayudante.id_ayudante 
    return render(request, 'detalleClase.html', {'clase': clase, 'usuario_ayudante': usuario_ayudante})

@login_required
@csrf_exempt
def cancelar_clase_view(request, id_clase):
    clase = get_object_or_404(ClaseAgendada, id_clase=id_clase)

    usuario = get_object_or_404(Usuario, correo=request.user.email)

    # Validar si el usuario es estudiante o ayudante asignado a la clase
    if not (clase.usuario_id_usuario == usuario or clase.id_ayudante.id_ayudante == usuario):
        return render(request, 'error.html', {'mensaje': 'No tienes permiso para cancelar esta clase.'})

    if request.method == 'POST':
        # Cambiar estado a cancelado
        clase.estado = 'cancelada'
        clase.save()

        # Cancelar evento en Google Calendar
        try:
            cred = Googlecalendartoken.objects.get(id_usuario=clase.id_ayudante.id_ayudante)

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

            # Buscar el evento por ID único usado en crear_evento_google
            if clase.evento_google_id:
                service.events().delete(calendarId='primary', eventId=clase.evento_google_id).execute()

        except Exception as e:
            print("Error al cancelar en Google Calendar:", e)

        # Notificar (opcional)
        crear_notificacion(
            "Clase Cancelada",
            "Administrador",
            clase.usuario_id_usuario.id_usuario,
            f"La clase con {clase.id_ayudante.id_ayudante.nombres} ha sido cancelada.",
            clase.id_clase
        )

        crear_notificacion(
            "Clase Cancelada",
            "Administrador",
            clase.id_ayudante.id_ayudante.id_usuario,
            f"La clase con {clase.usuario_id_usuario.nombres} ha sido cancelada.",
            clase.id_clase
        )

        messages.success(request, 'La clase fue cancelada correctamente.')
        return redirect('detalleClase_detalle', id=clase.id_clase)

    return render(request, 'error.html', {'mensaje': 'Método no permitido.'})