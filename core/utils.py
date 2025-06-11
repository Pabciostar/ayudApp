from django.db import models
from .models import Notificacion
from datetime import date
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