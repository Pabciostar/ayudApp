from background_task import background
from core.utils import verificar_y_enviar_recordatorios
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


@background(schedule=5, remove_existing_tasks=True)
def tarea_enviar_recordatorios():
    logger.info("Recordatorio enviado: %s", datetime.now())
    verificar_y_enviar_recordatorios()

    tarea_enviar_recordatorios(schedule=10)