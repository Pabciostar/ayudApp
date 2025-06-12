from rest_framework.routers import DefaultRouter
from .views import UsuarioViewSet, obtener_ayudante, lista_ayudantes, idAyudante, ayudante_autenticado, PostulacionViewSet, NotificacionesPorUsuarioAPIView, DetalleNotificacionAPIView, perfil_publico_ayudante,mejores_ayudantes_view, clases_agendadas_por_usuario_ayudante
from django.urls import path
from .views import mi_rol

router = DefaultRouter()
router.register(r'usuarios', UsuarioViewSet)
router.register(r'postulaciones', PostulacionViewSet)

urlpatterns = router.urls


urlpatterns = router.urls + [
    path('mi-rol/', mi_rol),
    path('ayudantes/<int:id>/', obtener_ayudante, name='obtener_ayudante'),
    path('ayudantes/', lista_ayudantes, name='lista_ayudantes'),
    path('perfilAyudante/', idAyudante, name='perfilAyudante_api'),
    path('ayudante/autenticado/', ayudante_autenticado, name='ayudante_autenticado'),
    path('perfil-ayudante/<int:id>/', perfil_publico_ayudante, name='perfil_publico_ayudante'),
    path('notificaciones/<str:user_id>/', NotificacionesPorUsuarioAPIView.as_view(), name='api_notificaciones_usuario'),
    path('<int:id_notificacion>/', DetalleNotificacionAPIView.as_view(), name='api_detalle_notificacion'),
    path('mejores-ayudantes/', mejores_ayudantes_view, name='mejores_ayudantes'),
    path('clases-agendadas/<str:usuario_id>/', clases_agendadas_por_usuario_ayudante, name='clases-agendadas'),
]