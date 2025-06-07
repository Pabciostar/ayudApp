from django.urls import path
from . import views

urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('buscador/', views.buscador_view, name='buscador'),
    path('postulacionAyudante/', views.postulacionAyudante_view, name='postulacionAyudante'),
    path('detalleClase', views.detalleClase_view, name='detalleClase'),
    path('perfilAyudante', views.perfilAyudante_view, name='perfilAyudante'),
    path('panelAdministrador', views.panelAdministrador, name='panelAdministrador'),
    path('notificaciones', views.notificaciones_view, name='notificaciones'),
    path('notificacion', views.notificacion_view, name='notificacion'),
    path('mensajeEstudianteAyudante', views.mensajeEstudianteAyudado_view, name='mensajeEstudianteAyudante'),
    path('detallePostulacion', views.detallePostulacion_view, name='detallePostulacion'),
    path('editarPerfilAyudante', views.editarPerfilAyudante_view, name='editarPerfilAyudante'),
    path('registro', views.registro_view, name='registro'),
    path('seleccionarFechaClase', views.seccionarFechaClase_view, name='seleccionarFechaClase'),
    path('login/', views.login_with_google, name='login'),
    path('oauth2callback/', views.oauth2callback, name='oauth2callback'),
    path('logout/', views.logout_view, name='logout'),
    path('datos_adicionales/', views.datos_adicionales, name='datos_adicionales'),
    path('completar_datos/', views.completar_datos, name='completar_datos'),
    path('aceptarPostulacion/', views.aceptar_postulacion, name='aceptar_postulacion'),
    path('rechazarPostulacion/', views.rechazar_postulacion, name='rechazar_postulacion'),
]