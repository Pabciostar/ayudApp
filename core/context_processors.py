from core.models import Usuario

def rol_usuario(request):
    rol = None
    if request.user.is_authenticated:
        try:
            usuario = Usuario.objects.get(correo=request.user.email)
            rol = usuario.rol
        except Usuario.DoesNotExist:
            pass
    return {'rol_usuario': rol}