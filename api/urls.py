from rest_framework.routers import DefaultRouter
from .views import UsuarioViewSet
from django.urls import path
from .views import mi_rol

router = DefaultRouter()
router.register(r'usuarios', UsuarioViewSet)

urlpatterns = router.urls


urlpatterns = router.urls + [
    path('mi-rol/', mi_rol),
]