# 🧠 AyudApp

AyudApp es una plataforma web para conectar estudiantes con ayudantes de diversas materias universitarias. Los estudiantes pueden agendar clases, pagar en línea y calificar a los ayudantes. Los ayudantes pueden configurar su disponibilidad y gestionar sus clases, todo desde un solo lugar.

---

## ⚙️ Requisitos

- Python 3.12+
- pip
- virtualenv (opcional pero recomendado)
- SQLite
- Git

---

## 📁 Estructura del Proyecto

```
.
├── .env                     # Variables de entorno sensibles (no versionado)
├── db.sqlite3              # Base de datos SQLite (puede estar en .gitignore)
├── manage.py               # Script principal para comandos Django
├── procfile                # Para despliegue en plataformas como Heroku
├── requirements.txt        # Dependencias del proyecto
├── ayudApp/                # App principal Django (core, static, templates)
├── core/                   # Lógica principal, modelos, vistas, utilidades
├── api/                    # Endpoints Django REST Framework
├── media/                  # Archivos subidos por los usuarios
```

---

## 🚀 Instalación

1. **Clonar el repositorio**
```bash
git clone https://github.com/Pabciostar/ayudApp.git
cd ayudapp
```

2. **Crear entorno virtual (opcional pero recomendado)**
```bash
python -m venv venv
source venv/bin/activate       # macOS/Linux
venv\Scripts\activate        # Windows
```

3. **Instalar dependencias**
```bash
pip install -r requirements.txt
```

4. **Configurar variables de entorno**

Asegúrate de tener un archivo `.env` en la raíz del proyecto con al menos las siguientes claves:

```dotenv
DEBUG=True
SECRET_KEY=tu_clave_secreta
ALLOWED_HOSTS=localhost,127.0.0.1
PAYPAL_CLIENT_ID=...
PAYPAL_SECRET=...
GOOGLE_CLIENT_ID=...
GOOGLE_CLIENT_SECRET=...
...
```

6. **Cargar archivos estáticos**
```bash
python manage.py collectstatic
```

---

## ▶️ Ejecutar el servidor

```bash
python manage.py runserver
```

---

## ⚙️ Ejecutar el proceso `proces_task`

Este proceso maneja tareas en segundo plano desde la lógica local (sin Celery).

Ejecuta en segundo plano:

```bash
python manage.py runscript proces_task
```

---

## 📬 Contacto

Para dudas técnicas o soporte, puedes contactar al desarrollador principal:  
**Carla Karinna Poveda Loyola**

---