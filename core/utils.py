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
        diferencia = (fecha_hora_clase - ahora).total_seconds()
        
        if 3540 <= diferencia <= 3660:
            notificacion_existente = Notificacion.objects.filter(
                asunto="Recordatorio: tu clase comienza en 1 hora",
                clase_agendada=clase.id_clase,
                destinatario=clase.usuario_id_usuario
            ).exists()

        if not notificacion_existente:
            crear_notificacion(
                asunto="Recordatorio: tu clase comienza en 1 hora",
                remitente = "administrador",
                destinatario= clase.usuario_id_usuario,
                cuerpo=f"La clase con el ayudante {clase.id_ayudante} comienza a las {clase.hora}",
                clase_agendada = clase.id_clase
            )
        

        # Enviar recordatorio 1 hora después
        diferencia_despues = (ahora - fecha_hora_clase).total_seconds()
        if 3540 <= diferencia_despues <= 3660:
             notificacion_existente = Notificacion.objects.filter(
                asunto="¿Cómo fue tu clase?",
                clase_agendada=clase.id_clase,
                destinatario=clase.usuario_id_usuario
            ).exists()
             
        if not notificacion_existente:
            crear_notificacion(
                asunto="¿Cómo fue tu clase?",
                cuerpo=f"Tu clase con el ayudante {clase.id_ayudante} terminó hace una hora. ¿Te gustaría evaluarla?",
                destinatario=clase.usuario_id_usuario
            )