"""Aplicación FastAPI para los CRUD independientes del proyecto."""

from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI

from app.database.conexion import conectar
from app.repositories.espacio_repository import crear_tabla_espacios
from app.repositories.usuario_repository import crear_tabla_usuarios
from app.routes.espacios import router as espacios_router
from app.routes.usuarios import router as usuarios_router

load_dotenv()


@asynccontextmanager
async def lifespan(_: FastAPI):
    """Prepara las tablas antes de aceptar solicitudes."""
    with conectar() as conn:
        crear_tabla_espacios(conn)
        crear_tabla_usuarios(conn)
    yield


app = FastAPI(
    title="API Parqueadero",
    version="1.1.0",
    description="Administración de parqueadero y usuarios (Neon / PostgreSQL)",
    lifespan=lifespan,
)

app.include_router(espacios_router)
app.include_router(usuarios_router)
