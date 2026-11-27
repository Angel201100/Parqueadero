# API de parqueadero

API REST construida con FastAPI y PostgreSQL. Permite administrar espacios de
parqueadero y ofrece un CRUD independiente para usuarios. La aplicación se
conecta a PostgreSQL mediante la variable de entorno `DATABASE_URL`.

Repositorio: <https://github.com/Angel201100/Parqueadero>
API publicada: <https://parqueadero-gv0b.onrender.com>
Swagger publicado: <https://parqueadero-gv0b.onrender.com/docs>

## Objetivo

Desarrollar una API REST documentada con FastAPI para gestionar espacios de
parqueadero, con un módulo independiente de usuarios y persistencia en
PostgreSQL. Los datos de las dos tablas no están relacionados.

## Módulos desarrollados

- `Espacios`: creación, consulta, actualización y eliminación de espacios, además
  de filtrado por el tipo de vehículo permitido.
- `Usuarios`: creación, consulta, actualización y eliminación de usuarios.
  Los correos se normalizan y las contraseñas se almacenan con hash
  PBKDF2-SHA256 y una sal aleatoria.

## Endpoints implementados

| Módulo | Método | Endpoint | Propósito |
|---|---|---|---|
| Espacios | `POST` | `/espacios` | Registrar un espacio |
| Espacios | `GET` | `/espacios` | Consultar todos los espacios |
| Espacios | `GET` | `/espacios?tipo_vehiculo=...` | Filtrar por tipo de vehículo |
| Espacios | `GET` | `/espacios/{espacio_id}` | Consultar un espacio |
| Espacios | `PUT` | `/espacios/{espacio_id}` | Actualizar un espacio |
| Espacios | `DELETE` | `/espacios/{espacio_id}` | Eliminar un espacio |
| Usuarios | `POST` | `/usuarios/` | Registrar un usuario |
| Usuarios | `GET` | `/usuarios/` | Consultar todos los usuarios |
| Usuarios | `GET` | `/usuarios/{usuario_id}` | Consultar un usuario |
| Usuarios | `PUT` | `/usuarios/{usuario_id}` | Actualizar un usuario |
| Usuarios | `DELETE` | `/usuarios/{usuario_id}` | Eliminar un usuario |

## Responsabilidad de las capas

| Carpeta | Responsabilidad |
|---|---|
| `app/routes` | Recibe las solicitudes HTTP, usa esquemas Pydantic y traduce errores de negocio a códigos HTTP. |
| `app/services` | Aplica reglas de negocio, normalización, hash de contraseñas y manejo de duplicados o registros inexistentes. |
| `app/repositories` | Ejecuta las consultas SQL contra PostgreSQL y convierte las filas en modelos internos. |
| `app/models` | Representa los registros y sus campos en objetos Python. |
| `app/schemas` | Valida los datos de entrada y controla los campos expuestos por las respuestas. |
| `app/database` | Crea y administra las conexiones configuradas con `DATABASE_URL`. |

## Estructura del proyecto

| Archivo | Responsabilidad |
|---|---|
| `main.py` | Configuración de FastAPI y ciclo de vida de las tablas. |
| `app/routes/` | Endpoints HTTP de usuarios y espacios. |
| `app/services/` | Reglas de negocio; incluye el hash de contraseñas. |
| `app/repositories/` | Consultas PostgreSQL de usuarios y espacios. |
| `app/models/` | Modelos internos de usuarios y espacios. |
| `app/schemas/` | Validación de solicitudes y respuestas de ambos CRUD. |
| `app/database/` | Conexión compartida a PostgreSQL mediante `DATABASE_URL`. |
| `test_api.py` | Pruebas de integración de las rutas. Requiere una base de datos desechable. |
| `test_usuarios.py` | Pruebas del contrato HTTP y lógica del CRUD de usuarios. |
| `requirements.txt` | Dependencias Python necesarias para ejecutar el servicio y sus pruebas. |

Las rutas de ambos módulos se comunican con sus servicios, que aplican las
reglas de negocio antes de invocar los repositorios. Al iniciar FastAPI se
crean las tablas `espacios` y `usuarios` si todavía no existen. Los usuarios
no tienen relaciones con la tabla del parqueadero.

```mermaid
flowchart TD
    Cliente --> Routes
    Routes --> Services
    Services --> Repositories
    Repositories --> PostgreSQL[(Neon / PostgreSQL)]
    Routes --> Schemas
    Services --> Models
    Database[Database: DATABASE_URL] --> Repositories
```

## Requisitos

- Python 3.10 o posterior.
- Una instancia PostgreSQL accesible desde el equipo.
- La cadena de conexión PostgreSQL en `DATABASE_URL`.

Neon es una opción de PostgreSQL administrado, pero también se puede usar otra
instancia compatible. La cadena debe incluir las opciones TLS que requiera el
proveedor.

## Configuración y ejecución en Windows

Desde PowerShell, en la carpeta del proyecto:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Configura la cadena de conexión en la sesión actual de PowerShell:

```powershell
$env:DATABASE_URL = "postgresql://usuario:contraseña@servidor:5432/base?sslmode=require"
```

También se puede crear un archivo `.env` en la raíz y agregarle una línea como
`DATABASE_URL=...`. `python-dotenv` carga ese archivo al iniciar la aplicación.
El archivo `.env.example` muestra la estructura sin credenciales reales.
El archivo `.env` está excluido de Git; no compartas ni subas credenciales.

Inicia el servidor:

```powershell
uvicorn main:app --reload
```

La API queda disponible normalmente en `http://127.0.0.1:8000`. FastAPI genera
la documentación interactiva en `http://127.0.0.1:8000/docs`.

## Modelo de un espacio

Un espacio contiene:

- `numero_espacio`: identificador legible, obligatorio y único (hasta 20 caracteres).
- `tipo_vehiculo`: `carro`, `moto`, `bicicleta` o `camion`.
- `ubicacion`: descripción obligatoria de hasta 100 caracteres.
- `tamano`: `pequeno`, `mediano` o `grande`.
- `tarifa_hora`: tarifa numérica mayor que cero.
- `id`: identificador asignado por PostgreSQL y presente en las respuestas.

## Tablas de la base de datos

```mermaid
erDiagram
    ESPACIOS {
        int id PK
        string numero_espacio UK
        string tipo_vehiculo
        string ubicacion
        string tamano
        decimal tarifa_hora
    }
    USUARIOS {
        int id PK
        string nombre
        string correo UK
        string contrasena_hash
    }
```

Las tablas son independientes y no tienen relaciones entre sí.

Ejemplo de cuerpo para crear un espacio:

```json
{
  "numero_espacio": "A-01",
  "tipo_vehiculo": "carro",
  "ubicacion": "Sótano 1",
  "tamano": "mediano",
  "tarifa_hora": 3500
}
```

## Rutas disponibles

### Usuarios

| Operación | Método y ruta | Resultado |
|---|---|---|
| Registrar usuario | `POST /usuarios/` | Crea el usuario y responde `201`. |
| Listar usuarios | `GET /usuarios/` | Devuelve la colección sin contraseñas. |
| Consultar por ID | `GET /usuarios/{usuario_id}` | Devuelve el usuario o `404`. |
| Actualizar | `PUT /usuarios/{usuario_id}` | Reemplaza nombre, correo y contraseña. |
| Eliminar | `DELETE /usuarios/{usuario_id}` | Elimina el usuario y responde `204`. |

Para registrar o actualizar se envían `nombre`, `correo` y `contrasena`. La
contraseña debe tener entre 8 y 128 caracteres; se almacena como hash
PBKDF2-SHA256 con sal aleatoria, nunca en texto plano. Los correos duplicados
responden `409`; los datos inválidos responden `422`. Las respuestas no incluyen
la contraseña ni su hash.

### Espacios

| Operación | Método y ruta | Resultado |
|---|---|---|
| Registrar un espacio | `POST /espacios` | Crea el registro y responde `201`. |
| Listar espacios | `GET /espacios` | Devuelve todos los registros en orden de ID. |
| Filtrar por vehículo | `GET /espacios?tipo_vehiculo=moto` | Devuelve solo los espacios del tipo solicitado. |
| Consultar por ID | `GET /espacios/{espacio_id}` | Devuelve el espacio o `404` si no existe. |
| Actualizar | `PUT /espacios/{espacio_id}` | Actualiza solo los campos enviados y devuelve el registro. |
| Eliminar | `DELETE /espacios/{espacio_id}` | Elimina el registro y responde `204` sin cuerpo. |

FastAPI responde `422` cuando un dato no pasa la validación y `409` si se intenta
registrar o renombrar un espacio con un número ya utilizado.

La documentación interactiva de ambos CRUD está disponible en `/docs`.

## Despliegue en Render

En Render crea un servicio **Web Service** vinculado al repositorio y configura:

- Build Command: `pip install -r requirements.txt`
- Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
- Environment Variable: `DATABASE_URL`, con la cadena PostgreSQL de Neon y
  `sslmode=require`.

Render debe tener acceso a la instancia Neon. No publiques el valor de
`DATABASE_URL`; configúralo en el panel de variables de entorno del servicio.
Al iniciar, la aplicación crea las tablas si no existen y la documentación se
publica en `https://parqueadero-gv0b.onrender.com/docs`.

El despliegue público fue comprobado mediante Swagger, OpenAPI y las rutas
`GET /espacios` y `GET /usuarios/`. Ambas rutas responden datos almacenados,
por lo que Render puede consultar correctamente la base Neon configurada en
`DATABASE_URL`.

## Pruebas

Las pruebas unitarias del CRUD de usuarios no requieren conexión a PostgreSQL.
Ejecútalas desde PowerShell con el entorno virtual activo:

```powershell
python -m unittest -v test_usuarios
```

`test_api.py` contiene pruebas de integración que verifican las operaciones
principales, la validación de datos, los filtros y los errores esperados.
Ejecútalas desde PowerShell con el entorno virtual activo y `DATABASE_URL`
configurada:

```powershell
python test_api.py
```

**Advertencia:** las pruebas ejecutan `TRUNCATE espacios RESTART IDENTITY` al
principio y al final. Esto elimina todos los registros de esa tabla y reinicia
su contador de IDs. Usa exclusivamente una base o rama de pruebas desechable;
nunca ejecutes el script con la conexión a producción ni con datos que deban
conservarse.
