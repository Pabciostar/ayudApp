from django.shortcuts import render

# Create your views here.
def inicio(request):
    return render(request, 'inicio.html')

def buscador_view(request):
    return render(request, 'buscador.html')

def postulacionAyudante_view(request):
    return render(request, 'postulacionAyudante.html')

def detalleClase_view(request):
    return render(request, 'detalleClase.html')

def perfilAyudante_view(request):
    return render(request, 'perfilAyudante.html')

def panelAdministrador(request):
    return render(request, 'panelAdministrador.html')

def notificaciones_view(request):
    return render(request, 'notificaciones.html')

def notificacion_view(request):
    return render(request, 'notificacion.html')

def mensajeEstudianteAyudado_view(request):
    return render(request, 'mensajeEstudianteAyudante.html')

def detallePostulacion_view(request):
    return render(request, 'detallePostulacion.html')

def editarPerfilAyudante_view(request):
    return render(request, 'editarPerfilAyudante.html')