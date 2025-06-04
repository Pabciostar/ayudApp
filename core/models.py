# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models
from datetime import datetime

ROL_CHOICES = [
    ('estudiante', 'Estudiante'),
    ('ayudante', 'Ayudante'),
    ('administrador', 'Administrador'),
]

ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('aceptada', 'Aceptada'),
        ('rechazada', 'Rechazada'),
    ]

class AuthGroup(models.Model):
    name = models.CharField(unique=True, max_length=150)

    class Meta:
        managed = False
        db_table = 'auth_group'


class AuthGroupPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)
    permission = models.ForeignKey('AuthPermission', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_group_permissions'
        unique_together = (('group', 'permission'),)


class AuthPermission(models.Model):
    name = models.CharField(max_length=255)
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING)
    codename = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'auth_permission'
        unique_together = (('content_type', 'codename'),)


class AuthUser(models.Model):
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.BooleanField()
    username = models.CharField(unique=True, max_length=150)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.CharField(max_length=254)
    is_staff = models.BooleanField()
    is_active = models.BooleanField()
    date_joined = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'auth_user'


class AuthUserGroups(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_groups'
        unique_together = (('user', 'group'),)


class AuthUserUserPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    permission = models.ForeignKey(AuthPermission, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_user_permissions'
        unique_together = (('user', 'permission'),)


class Ayudante(models.Model):
    id_ayudante = models.OneToOneField('Usuario', models.DO_NOTHING, db_column='id_ayudante', primary_key=True)
    carrera = models.CharField(max_length=30)
    foto = models.BinaryField(blank=True, null=True)
    cuentanos = models.CharField(max_length=100)
    disponibilidad = models.CharField(max_length=50)
    experiencia = models.CharField(max_length=2)
    ramos = models.CharField(max_length=30)
    valor = models.DecimalField(max_digits=7, decimal_places=0)
    terminos = models.CharField(max_length=2)
    validado = models.CharField(max_length=12)

    class Meta:
        managed = False
        db_table = 'ayudante'


class ClaseAgendada(models.Model):
    id_clase = models.DecimalField(primary_key=True, max_digits=12, decimal_places=0)
    fecha = models.DateField()
    hora = models.TimeField()
    valor = models.DecimalField(max_digits=7, decimal_places=0)
    materia_id_materia = models.ForeignKey('Materia', models.DO_NOTHING, db_column='materia_id_materia')
    usuario_id_usuario = models.ForeignKey('Usuario', models.DO_NOTHING, db_column='usuario_id_usuario')
    transaccion_id_transaccion = models.ForeignKey('Transaccion', models.DO_NOTHING, db_column='transaccion_id_transaccion')

    class Meta:
        managed = False
        db_table = 'clase_agendada'


class CoreUsuario(models.Model):
    id_usuario = models.CharField(primary_key=True, max_length=20)
    rut_usuario = models.CharField(max_length=20)
    nombres = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=100)
    nacimiento = models.DateField(blank=True, null=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    correo = models.CharField(unique=True, max_length=254)
    rol = models.CharField(max_length=50)
    sexo = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'core_usuario'


class DjangoAdminLog(models.Model):
    action_time = models.DateTimeField()
    object_id = models.TextField(blank=True, null=True)
    object_repr = models.CharField(max_length=200)
    action_flag = models.SmallIntegerField()
    change_message = models.TextField()
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING, blank=True, null=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'django_admin_log'


class DjangoContentType(models.Model):
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'django_content_type'
        unique_together = (('app_label', 'model'),)


class DjangoMigrations(models.Model):
    id = models.BigAutoField(primary_key=True)
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40)
    session_data = models.TextField()
    expire_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_session'


class Evaluacion(models.Model):
    id_evaluacion = models.DecimalField(primary_key=True, max_digits=5, decimal_places=0)
    valoracion = models.DecimalField(max_digits=1, decimal_places=0)
    comentario = models.CharField(max_length=100, blank=True, null=True)
    clase_agendada_id_clase = models.ForeignKey(ClaseAgendada, models.DO_NOTHING, db_column='clase_agendada_id_clase')

    class Meta:
        managed = False
        db_table = 'evaluacion'


class Materia(models.Model):
    id_materia = models.CharField(primary_key=True, max_length=20)
    nombre = models.CharField(max_length=30)
    ayudante_id_ayudante = models.ForeignKey(Ayudante, models.DO_NOTHING, db_column='ayudante_id_ayudante')

    class Meta:
        managed = False
        db_table = 'materia'


class Notificacion(models.Model):
    id_notificacion = models.DecimalField(primary_key=True, max_digits=12, decimal_places=0)
    fecha = models.DateField()
    asunto = models.CharField(max_length=30)
    remitente = models.CharField(max_length=30)
    destinatario = models.CharField(max_length=50)
    cuerpo = models.CharField(max_length=300)
    clase_agendada_id_clase = models.ForeignKey(ClaseAgendada, models.DO_NOTHING, db_column='clase_agendada_id_clase')

    class Meta:
        managed = False
        db_table = 'notificacion'


class Postulacion(models.Model):
    id_postulacion = models.DecimalField(primary_key=True, max_digits=12, decimal_places=0)
    carrera = models.CharField(max_length=30)
    foto = models.ImageField(upload_to='postulaciones/')
    cuentanos = models.CharField(max_length=100)
    disponibilidad = models.CharField(max_length=50)
    experiencia = models.CharField(max_length=2)
    ramos = models.CharField(max_length=50)
    valor = models.DecimalField(max_digits=7, decimal_places=0)
    terminos = models.CharField(max_length=2)
    estado = models.CharField(max_length=10, choices=ESTADO_CHOICES, default='pendiente')
    usuario_id_usuario = models.ForeignKey('Usuario', models.DO_NOTHING, db_column='usuario_id_usuario')

    def save(self, *args, **kwargs):
        if not self.id_postulacion:
            self.id_postulacion = int(datetime.now().strftime('%y%m%d%H%M%S'))
        super().save(*args, **kwargs)

    class Meta:
        managed = False
        db_table = 'postulacion'


class Transaccion(models.Model):
    id_transaccion = models.DecimalField(primary_key=True, max_digits=12, decimal_places=0)
    voucher = models.CharField(max_length=30)

    class Meta:
        managed = False
        db_table = 'transaccion'


class Usuario(models.Model):
    id_usuario = models.CharField(primary_key=True, max_length=8)
    rut_usuario = models.CharField(max_length=10)
    nombres = models.CharField(max_length=30)
    apellidos = models.CharField(max_length=30)
    nacimiento = models.DateField()
    telefono = models.CharField(max_length=11)
    correo = models.CharField(max_length=50)
    rol = models.CharField(max_length=15)
    sexo = models.CharField(max_length=20)

    class Meta:
        managed = False
        db_table = 'usuario'
