from rest_framework.routers import DefaultRouter
from .views import (
    UsuarioViewSet, 
    obtener_ayudante, 
    lista_ayudantes, 
    idAyudante, 
    ayudante_autenticado, 
    PostulacionViewSet, 
    detalle_notificacion, 
    perfil_publico_ayudante,
    listar_notificaciones,
    mejores_ayudantes_view, 
    clases_agendadas_por_usuario_ayudante, 
    notificaciones_por_usuario, 
    detalle_clase_api,
    MateriaViewSet,
    TransaccionViewSet,
    clases_agendadas,
    EvaluacionViewSet,
    recibir_calificacion,
    reportar_problema
)
from django.urls import path
from .views import mi_rol

router = DefaultRouter()
router.register(r'usuarios', UsuarioViewSet)
router.register(r'postulaciones', PostulacionViewSet)
router.register(r'materias', MateriaViewSet)
router.register(r'transaccion', TransaccionViewSet)
router.register(r'evaluacion', EvaluacionViewSet)

urlpatterns = router.urls

urlpatterns = router.urls + [
    path('mi-rol/', mi_rol),
    path('ayudantes/<int:id>/', obtener_ayudante, name='obtener_ayudante'),
    path('ayudantes/', lista_ayudantes, name='lista_ayudantes'),
    path('perfilAyudante/', idAyudante, name='perfilAyudante_api'),
    path('ayudante/autenticado/', ayudante_autenticado, name='ayudante_autenticado'),
    path('perfil-ayudante/<int:id>/', perfil_publico_ayudante, name='perfil_publico_ayudante'),
    path('notificaciones/', listar_notificaciones, name='listar_notificaciones'),
    path('notificaciones/<int:user_id>/', notificaciones_por_usuario, name='api_notificaciones_usuario'),
    path('notificacion/<int:id_notificacion>/', detalle_notificacion, name='api_detalle_notificacion'),
    path('mejores-ayudantes/', mejores_ayudantes_view, name='mejores_ayudantes'),
    path('clases-agendadas/<int:usuario_id>/', clases_agendadas_por_usuario_ayudante, name='clases-agendadas'),
    path('detalleClase/<int:id_clase>/', detalle_clase_api, name='detalle_clase_api'),
    path('clases-agendadas/', clases_agendadas, name='clases_agendadas_global'),
    path('notificacion/<int:notif_id>/calificar/', recibir_calificacion, name='recibir_calificacion'),
    path('reportar-problema/<int:clase_id>/', reportar_problema, name='reportar_problema'),
]