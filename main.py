"""Aplicación FastAPI para los CRUD independientes del proyecto."""

from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI

from app.database.conexion import conectar
from app.repositories.espacio_repository import crear_tabla_espacios
from app.repositories.usuario_repository import crear_tabla_usuarios
from app.routes.espacios import router as espacios_router
from app.routes.usuarios import router as usuarios_router

# Lee DATABASE_URL desde el archivo local .env, si está presente.
# En Render, la variable se configura desde el panel del servicio.
load_dotenv()


@asynccontextmanager
async def lifespan(_: FastAPI):
    """Prepara la base de datos al iniciar y deja terminar la aplicación."""
    # La misma conexión se usa para comprobar/crear las dos tablas.
    with conectar() as conn:
        crear_tabla_espacios(conn)
        crear_tabla_usuarios(conn)
    # FastAPI empieza a aceptar solicitudes después de este punto.
    yield


# FastAPI utiliza este objeto para servir la API y generar /docs.
app = FastAPI(
    title="API Parqueadero",
    version="1.1.0",
    description="Administración de parqueadero y usuarios (Neon / PostgreSQL)",
    lifespan=lifespan,
)

# Registra las rutas de ambos módulos para que formen parte de esta aplicación.
app.include_router(espacios_router)
app.include_router(usuarios_router)
