from rest_framework.routers import DefaultRouter
from .views import UsuarioViewSet, obtener_ayudante, lista_ayudantes, idAyudante, ayudante_autenticado
from django.urls import path
from .views import mi_rol

router = DefaultRouter()
router.register(r'usuarios', UsuarioViewSet)

urlpatterns = router.urls


urlpatterns = router.urls + [
    path('mi-rol/', mi_rol),
    path('ayudantes/<int:id>/', obtener_ayudante, name='obtener_ayudante'),
    path('ayudantes/', lista_ayudantes, name='lista_ayudantes'),
    path('perfilAyudante/', idAyudante, name='perfilAyudante_api'),
    path('ayudante/autenticado/', ayudante_autenticado, name='ayudante_autenticado'),
]