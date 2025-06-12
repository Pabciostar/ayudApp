from functools import wraps
from django.http import HttpResponseRedirect
from django.urls import reverse
from .models import Usuario

def rol_requerido(rol_requerido):
    def decorator(view_func):
        @wraps(view_func)
        def vista_protegida(request, *args, **kwargs):
            if request.user.is_authenticated:
                try:
                    usuario = Usuario.objects.get(correo=request.user.email)
                    if usuario.rol == rol_requerido:
                        return view_func(request, *args, **kwargs)
                except Usuario.DoesNotExist:
                    pass
            return HttpResponseRedirect(reverse('buscador'))
        return vista_protegida
    return decorator