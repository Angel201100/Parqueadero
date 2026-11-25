"""API REST para administrar espacios de un parqueadero.

La aplicación expone operaciones CRUD sobre PostgreSQL y obtiene la cadena de
conexión de la variable de entorno ``DATABASE_URL``. Al iniciar, verifica que
exista la tabla necesaria; FastAPI publica la documentación interactiva en
``/docs``.
"""

import os
from contextlib import asynccontextmanager
from enum import Enum
from typing import List, Optional

from fastapi import FastAPI, HTTPException, Query, Response, status
from dotenv import load_dotenv
import psycopg
from psycopg.errors import UniqueViolation
from psycopg.rows import dict_row
from pydantic import BaseModel, Field

# Carga las variables definidas en .env durante el desarrollo local. En otros
# entornos, las variables pueden configurarse directamente en el sistema.
load_dotenv()


def conectar() -> psycopg.Connection:
    """Abre una conexión PostgreSQL configurada mediante ``DATABASE_URL``.

    Cada operación crea y cierra su propia conexión. Las filas se devuelven
    como diccionarios para que coincidan directamente con los modelos de salida
    de la API. Se informa explícitamente si falta la configuración requerida.
    """
    url = os.getenv("DATABASE_URL")
    if not url:
        raise RuntimeError(
            "Falta DATABASE_URL; consulta la sección de configuración del README."
        )
    return psycopg.connect(url, row_factory=dict_row, autocommit=True)


@asynccontextmanager
async def lifespan(_: FastAPI):
    """Prepara el esquema antes de aceptar solicitudes.

    ``CREATE TABLE IF NOT EXISTS`` permite iniciar la API repetidamente sin
    reemplazar la tabla ni borrar los espacios que ya estén almacenados. Las
    restricciones de PostgreSQL protegen también los datos fuera de la API.
    """
    with conectar() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS espacios (
                id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                numero_espacio VARCHAR(20) NOT NULL UNIQUE,
                tipo_vehiculo VARCHAR(20) NOT NULL,
                ubicacion VARCHAR(100) NOT NULL,
                tamano VARCHAR(20) NOT NULL,
                tarifa_hora NUMERIC(10, 2) NOT NULL CHECK (tarifa_hora > 0)
            )""")
    yield


# ---------- Aplicación ----------
app = FastAPI(
    title="API Parqueadero",
    version="1.1.0",
    description="Administración de espacios de un parqueadero (Neon / PostgreSQL)",
    lifespan=lifespan,
)


# ---------- Modelos de dominio y validación ----------
class TipoVehiculo(str, Enum):
    """Tipos de vehículo que la API permite asignar a un espacio."""

    carro = "carro"
    moto = "moto"
    bicicleta = "bicicleta"
    camion = "camion"


class Tamano(str, Enum):
    """Tamaños disponibles para describir un espacio."""

    pequeno = "pequeno"
    mediano = "mediano"
    grande = "grande"


class EspacioBase(BaseModel):
    """Campos compartidos por los datos de entrada y salida de un espacio.

    Pydantic valida los límites de longitud, los valores de los enums y que la
    tarifa sea positiva antes de ejecutar una consulta a la base de datos.
    """

    numero_espacio: str = Field(..., min_length=1, max_length=20, examples=["A-01"])
    tipo_vehiculo: TipoVehiculo
    ubicacion: str = Field(..., min_length=1, max_length=100, examples=["Sótano 1, zona norte"])
    tamano: Tamano
    tarifa_hora: float = Field(..., gt=0, examples=[3500])


class EspacioCrear(EspacioBase):
    """Representación validada que se exige al registrar un espacio."""


class EspacioActualizar(BaseModel):
    """Campos opcionales para actualizar solo los valores enviados.

    Un campo omitido o con valor ``None`` no cambia el valor almacenado. Las
    mismas restricciones de formato que en la creación se aplican cuando se
    proporciona un valor.
    """

    numero_espacio: Optional[str] = Field(None, min_length=1, max_length=20)
    tipo_vehiculo: Optional[TipoVehiculo] = None
    ubicacion: Optional[str] = Field(None, min_length=1, max_length=100)
    tamano: Optional[Tamano] = None
    tarifa_hora: Optional[float] = Field(None, gt=0)


class Espacio(EspacioBase):
    """Respuesta de la API, que añade el identificador generado por PostgreSQL."""

    id: int


# ---------- Acceso y utilidades de datos ----------
def obtener_o_404(conn: psycopg.Connection, espacio_id: int) -> dict:
    """Busca un espacio por ID y genera HTTP 404 si no existe.

    Centralizar esta consulta mantiene el mismo comportamiento para las rutas
    de lectura, actualización y eliminación.
    """
    fila = conn.execute("SELECT * FROM espacios WHERE id = %s", (espacio_id,)).fetchone()
    if fila is None:
        raise HTTPException(404, f"No existe el espacio con id {espacio_id}")
    return fila


# ---------- Rutas HTTP ----------
@app.post("/espacios", response_model=Espacio, status_code=status.HTTP_201_CREATED)
def crear_espacio(datos: EspacioCrear):
    """Registra un espacio nuevo y devuelve el registro creado.

    La restricción UNIQUE de la base de datos impide duplicar el número. Su
    violación se convierte en HTTP 409, una respuesta útil para el cliente.
    """
    conn = conectar()
    try:
        with conn.transaction():
            nuevo = conn.execute(
                """
                INSERT INTO espacios (
                    numero_espacio, tipo_vehiculo, ubicacion, tamano, tarifa_hora
                )
                VALUES (%s, %s, %s, %s, %s)
                RETURNING *
                """,
                (
                    datos.numero_espacio,
                    datos.tipo_vehiculo.value,
                    datos.ubicacion,
                    datos.tamano.value,
                    datos.tarifa_hora,
                ),
            ).fetchone()
        return nuevo
    except UniqueViolation:
        raise HTTPException(409, f"Ya existe el espacio '{datos.numero_espacio}'")
    finally:
        conn.close()


@app.get("/espacios", response_model=List[Espacio])
def listar_espacios(
    tipo_vehiculo: Optional[TipoVehiculo] = Query(
        None,
        description=(
            "Filtra por tipo de vehículo permitido "
            "(carro, moto, bicicleta, camion)"
        ),
    )
):
    """Lista los espacios, opcionalmente filtrados por tipo de vehículo.

    El valor del filtro se envía como parámetro SQL, no se concatena en la
    consulta. El orden por ID hace que la respuesta sea predecible.
    """
    sql, params = "SELECT * FROM espacios", []
    if tipo_vehiculo:
        sql += " WHERE tipo_vehiculo = %s"
        params.append(tipo_vehiculo.value)
    with conectar() as conn:
        return conn.execute(sql + " ORDER BY id", params).fetchall()


@app.get("/espacios/{espacio_id}", response_model=Espacio)
def consultar_espacio(espacio_id: int):
    """Devuelve el espacio solicitado o HTTP 404 cuando no existe."""
    with conectar() as conn:
        return obtener_o_404(conn, espacio_id)


@app.put("/espacios/{espacio_id}", response_model=Espacio)
def actualizar_espacio(espacio_id: int, datos: EspacioActualizar):
    """Actualiza los campos proporcionados y devuelve el espacio actualizado.

    Se comprueba primero que el ID exista. Si no se enviaron cambios, se
    devuelve el registro sin ejecutar un UPDATE. Los nombres de columna se
    obtienen exclusivamente de los campos definidos en ``EspacioActualizar``;
    los valores se mantienen parametrizados en SQL.
    """
    cambios = datos.model_dump(exclude_none=True)
    conn = conectar()
    try:
        obtener_o_404(conn, espacio_id)
        if cambios:
            # Los enums de Pydantic se guardan en la base como sus valores de texto.
            cambios = {k: (v.value if isinstance(v, Enum) else v) for k, v in cambios.items()}
            sets = ", ".join(f"{c} = %s" for c in cambios)
            with conn.transaction():
                conn.execute(
                    f"UPDATE espacios SET {sets} WHERE id = %s",
                    (*cambios.values(), espacio_id),
                )
        return obtener_o_404(conn, espacio_id)
    except UniqueViolation:
        raise HTTPException(409, "Ya existe otro espacio con ese número")
    finally:
        conn.close()


@app.delete("/espacios/{espacio_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_espacio(espacio_id: int):
    """Elimina el espacio solicitado y responde sin cuerpo (HTTP 204).

    Si el ID no existe, la comprobación previa devuelve HTTP 404 en lugar de
    informar un borrado exitoso que no ocurrió.
    """
    conn = conectar()
    try:
        obtener_o_404(conn, espacio_id)
        with conn.transaction():
            conn.execute("DELETE FROM espacios WHERE id = %s", (espacio_id,))
    finally:
        conn.close()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
