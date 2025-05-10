from django.urls import path
from . import views

urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('buscador/', views.buscador_view, name='buscador'),
    path('postulacionAyudante/', views.postulacionAyudante_view, name='postulacionAyudante'),
]