from rest_framework.routers import DefaultRouter
from .views import UsuarioViewSet, PostulacionViewSet
from django.urls import path
from .views import mi_rol

router = DefaultRouter()
router.register(r'usuarios', UsuarioViewSet)
router.register(r'postulaciones', PostulacionViewSet)

urlpatterns = router.urls


urlpatterns = router.urls + [
    path('mi-rol/', mi_rol),
]