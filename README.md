## API de Gestión de Citas Médicas

API REST construida con FastAPI para gestionar citas médicas: registro y autenticación de usuarios, agendamiento, consulta, edición y cancelación de citas, con administración basada en roles.

![FastAPI](https://img.shields.io/badge/FastAPI-109989?logo=fastapi&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-14+-336791?logo=postgresql&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&logoColor=white)
![License](https://img.shields.io/badge/License-Propietaria-lightgray)

### Tabla de contenidos
- [Tecnologías](#tecnologías)
- [Características](#características)
- [Estructura del proyecto](#estructura-del-proyecto)
- [Requisitos](#requisitos)
- [Configuración](#configuración)
- [Ejecución con Docker](#ejecución-con-docker)
- [Ejecución local](#ejecución-local-sin-docker)
- [Documentación](#documentación-de-la-api)
- [Variables de entorno](#variables-de-entorno)
- [Roles y permisos](#roles-y-permisos)
- [Endpoints](#endpoints-reales)
- [Ejemplos](#ejemplos-de-uso)
- [Despliegue](#despliegue)
- [Notas de seguridad](#notas-de-seguridad)
- [Autor](#autor)
- [Licencia](#licencia)

## Tecnologías
- FastAPI, Pydantic
- PostgreSQL (via `DATABASE_URL`)
- Autenticación JWT y autorización por roles (paciente, doctor, admin)
- Docker y Docker Compose

## Características
- Registro y autenticación de usuarios (paciente, doctor, admin)
- CRUD de citas médicas (crear, leer, actualizar, cancelar)
- Administración de usuarios y citas (solo admin)
- Seguridad con JWT, contraseñas hasheadas y control de acceso por roles
- **Gestión inteligente de horarios**: Las citas canceladas liberan automáticamente el horario para otros pacientes

## Estructura del proyecto
```
.env
docker-compose.yml
Dockerfile
requirements.txt
app/
    main.py
    database.py
    models/
    routers/
    schemas/
    services/
    utils/
```

## Requisitos
- Docker y Docker Compose
- (Opcional) Python 3.11+ si quieres correr sin Docker

## Configuración
1) Crea un archivo `.env` en la raíz con al menos:
```
SECRET_KEY=claveromohospital
DATABASE_URL=postgresql+psycopg2://postgres:postgres@db:5432/hospital
```
2) Revisa/ajusta `docker-compose.yml` si cambias credenciales o puertos.

## Ejecución con Docker
```sh
docker-compose up --build
```
La API quedará disponible en `http://localhost:8000`.

## Ejecución local (sin Docker)
1) Asegura una base de datos PostgreSQL en marcha y exporta `DATABASE_URL`.
2) Crea entorno e instala dependencias:
```sh
python -m venv .venv && .venv\\Scripts\\activate
pip install -r requirements.txt
```
3) Inicia el servidor:
```sh
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Documentación de la API
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Variables de entorno
- `SECRET_KEY`: Clave secreta para firmar JWT
- `DATABASE_URL`: Cadena de conexión a PostgreSQL (driver recomendado `psycopg2`)
- (Opcional) `ACCESS_TOKEN_EXPIRE_MINUTES`: Minutos de expiración del token

## Roles y permisos
- Paciente: crear/consultar sus citas
- Doctor: consultar/gestionar sus citas
- Admin: administrar usuarios y todas las citas

## Endpoints reales

Con las rutas normalizadas (sin doble prefijo):

| Método | Ruta                    | Descripción                         | Rol requerido |
|--------|-------------------------|-------------------------------------|---------------|
| POST   | `/auth/registro`       | Registrar un nuevo usuario          | Público       |
| POST   | `/auth/login`          | Obtener token de acceso (OAuth2)    | Público       |
| POST   | `/users/admin/crear`   | Crear usuario (por admin)           | Admin         |
| POST   | `/users/crear_admin`   | Crear usuario administrador         | Admin         |
| POST   | `/citas/`              | Agendar una cita                    | Autenticado   |
| GET    | `/citas/`              | Consultar mis citas                 | Autenticado   |
| GET    | `/citas/hoy`           | Ver mis citas de hoy                | Autenticado   |
| PUT    | `/citas/{cita_id}`     | Editar mi cita                      | Autenticado   |
| DELETE | `/citas/{cita_id}`     | Cancelar mi propia cita (libera horario) | Autenticado   |
| GET    | `/citas/admin`         | Ver todas las citas                 | Admin         |
| PUT    | `/citas/admin/{cita_id}` | Editar cita (admin)               | Admin         |
| DELETE | `/citas/admin/{cita_id}` | Eliminar una cita (admin)         | Admin         |

## Ejemplos de uso

Autenticación (login con formulario x-www-form-urlencoded):
```sh
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=user@example.com&password=Passw0rd!" # ahora también acepta username o email
```

Registro de usuario (JSON):
```sh
curl -X POST http://localhost:8000/auth/registro \
  -H "Content-Type: application/json" \
  -d '{
    "username":"usuario1",
    "email":"user@example.com",
    "password":"Passw0rd!",
    "full_name":"Nombre Apellido",
    "role":"paciente"
  }'
```

Crear cita (token Bearer requerido):
```sh
TOKEN=eyJ... # reemplaza por tu token
curl -X POST http://localhost:8000/citas/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "motivo":"Medicina General",
    "fecha_hora":"2025-10-01T09:00:00Z",
    "notas":"Primera consulta"
  }'
```

Listar mis citas:
```sh
curl -X GET http://localhost:8000/citas/ \
  -H "Authorization: Bearer $TOKEN"
```

## Despliegue
- Ajusta variables en `.env` para entorno productivo (clave fuerte y URL DB gestionada).
- Construye imagen: `docker build -t hospital_backend:latest .`
- Orquesta con `docker-compose` o en tu plataforma (Kubernetes/Swarm).
- Configura un proxy reverso (Nginx/Caddy) y HTTPS (Let's Encrypt).

## Notas de seguridad
- Usa `SECRET_KEY` robusta y rota credenciales periódicamente.
- Limita el CORS a dominios confiables en producción.
- Asegura la base de datos con red privada y usuarios de mínimo privilegio.

## Autor
- Dev Daniel Rodriguez

## Licencia
Derechos reservados del autor.


