from background_task import background
from core.utils import verificar_y_enviar_recordatorios
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

@background(schedule=1)
def tarea_enviar_recordatorios():
    logger.info("🔄 Iniciando verificación de recordatorios... %s", datetime.now())
    
    try:
        verificar_y_enviar_recordatorios()
    except Exception as e:
        logger.error("❌ Error al ejecutar las notificaciones: %s", str(e))
    
    logger.info("⏳ Programando próxima ejecución...")
    programar_nueva_tarea()


def programar_nueva_tarea():
    """
    Función auxiliar que programa nuevamente la tarea,
    asegurando que se repita indefinidamente.
    """
    tarea_enviar_recordatorios(schedule=10) 