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