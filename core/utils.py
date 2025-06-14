from django.db import models
from .models import Notificacion, ClaseAgendada
from datetime import date, datetime, timedelta
from decimal import Decimal

def crear_notificacion(asunto, remitente, destinatario, cuerpo, clase_agendada=None):
    ultima_id = Notificacion.objects.aggregate(max_id=models.Max('id_notificacion'))['max_id'] or 0
    nueva_id = Decimal(ultima_id) + 1
    Notificacion.objects.create(
        id_notificacion=nueva_id,
        fecha=date.today(),
        asunto=asunto,
        remitente=remitente,
        destinatario=destinatario,
        cuerpo=cuerpo,
        clase_agendada_id_clase=clase_agendada
    )



def verificar_y_enviar_recordatorios():
    ahora = datetime.now()
    clases = ClaseAgendada.objects.all()

    for clase in clases:
        fecha_hora_clase = datetime.combine(clase.fecha, clase.hora)

        diferencia_antes = (fecha_hora_clase - ahora).total_seconds()
        diferencia_despues = (ahora - fecha_hora_clase).total_seconds()

        # Recordatorio antes de la clase (hasta ~16 minutos antes)
        if 0 <= diferencia_antes <= 1000:
            ya_enviada = Notificacion.objects.filter(
                asunto="Recordatorio",
                remitente="administrador",
                destinatario=clase.usuario_id_usuario.pk,
                clase_agendada_id_clase=clase.id_clase
            ).exists()
            print(clase.id_clase)
            if not ya_enviada:
                crear_notificacion(
                    asunto="Recordatorio",
                    remitente="administrador",
                    destinatario=clase.usuario_id_usuario.pk,
                    cuerpo=f"Tiene una clase agendada que comienza a las {clase.hora}",
                    clase_agendada=clase.id_clase
                )
                print(clase.usuario_id_usuario.pk)

                crear_notificacion(
                    asunto="Recordatorio",
                    remitente="administrador",
                    destinatario=clase.id_ayudante.pk, 
                    cuerpo=f"Tiene una clase agendada que comienza a las {clase.hora}",
                    clase_agendada=clase.id_clase
                )
                print(clase.id_ayudante.pk)

        # Recordatorio después de la clase (pasada 1 hora)
        if 0 <= diferencia_despues <= 1000:
            ya_enviada = Notificacion.objects.filter(
                asunto="¿Cómo fue tu clase?",
                remitente="administrador",
                destinatario=clase.usuario_id_usuario.pk,
                clase_agendada_id_clase=clase.id_clase
            ).exists()

            if not ya_enviada:
                crear_notificacion(
                    asunto="¿Cómo fue tu clase?",
                    remitente="administrador",
                    destinatario=clase.usuario_id_usuario.pk,
                    cuerpo="Su clase terminó hace una hora. ¿Te gustaría evaluarla?",
                    clase_agendada=clase.id_clase
                )