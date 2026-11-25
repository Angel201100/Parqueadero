"""API de gestión de espacios de parqueadero (FastAPI + PostgreSQL en Neon)."""
import os
from contextlib import asynccontextmanager
from enum import Enum
from typing import List, Optional

from fastapi import FastAPI, HTTPException, Query, Response, status
import psycopg
from dotenv import load_dotenv
from psycopg.errors import UniqueViolation
from psycopg.rows import dict_row
from pydantic import BaseModel, Field

load_dotenv()


def conectar() -> psycopg.Connection:
    """Abre una conexión a Neon usando DATABASE_URL (variable de entorno)."""
    url = os.getenv("DATABASE_URL")
    if not url:
        raise RuntimeError("Falta la variable de entorno DATABASE_URL (ver .env.example)")
    return psycopg.connect(url, row_factory=dict_row, autocommit=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Crea la tabla al iniciar si no existe
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


app = FastAPI(title="API Parqueadero", version="1.1.0",
              description="Administración de espacios de un parqueadero (Neon / PostgreSQL)",
              lifespan=lifespan)


# ---------- Modelos ----------
class TipoVehiculo(str, Enum):
    carro = "carro"
    moto = "moto"
    bicicleta = "bicicleta"
    camion = "camion"


class Tamano(str, Enum):
    pequeno = "pequeno"
    mediano = "mediano"
    grande = "grande"


class EspacioBase(BaseModel):
    numero_espacio: str = Field(..., min_length=1, max_length=20, examples=["A-01"])
    tipo_vehiculo: TipoVehiculo
    ubicacion: str = Field(..., min_length=1, max_length=100, examples=["Sótano 1, zona norte"])
    tamano: Tamano
    tarifa_hora: float = Field(..., gt=0, examples=[3500])


class EspacioCrear(EspacioBase):
    pass


class EspacioActualizar(BaseModel):
    """Actualización parcial: solo se modifican los campos enviados."""
    numero_espacio: Optional[str] = Field(None, min_length=1, max_length=20)
    tipo_vehiculo: Optional[TipoVehiculo] = None
    ubicacion: Optional[str] = Field(None, min_length=1, max_length=100)
    tamano: Optional[Tamano] = None
    tarifa_hora: Optional[float] = Field(None, gt=0)


class Espacio(EspacioBase):
    id: int


# ---------- Utilidades ----------
def obtener_o_404(conn: psycopg.Connection, espacio_id: int) -> dict:
    fila = conn.execute("SELECT * FROM espacios WHERE id = %s", (espacio_id,)).fetchone()
    if fila is None:
        raise HTTPException(404, f"No existe el espacio con id {espacio_id}")
    return fila


# ---------- Endpoints ----------
@app.post("/espacios", response_model=Espacio, status_code=status.HTTP_201_CREATED)
def crear_espacio(datos: EspacioCrear):
    """1. Registrar un espacio."""
    conn = conectar()
    try:
        with conn.transaction():
            nuevo = conn.execute(
                "INSERT INTO espacios (numero_espacio, tipo_vehiculo, ubicacion, tamano, tarifa_hora) "
                "VALUES (%s, %s, %s, %s, %s) RETURNING *",
                (datos.numero_espacio, datos.tipo_vehiculo.value, datos.ubicacion,
                 datos.tamano.value, datos.tarifa_hora)).fetchone()
        return nuevo
    except UniqueViolation:
        raise HTTPException(409, f"Ya existe el espacio '{datos.numero_espacio}'")
    finally:
        conn.close()


@app.get("/espacios", response_model=List[Espacio])
def listar_espacios(
    tipo_vehiculo: Optional[TipoVehiculo] = Query(
        None, description="Filtra por tipo de vehículo permitido (carro, moto, bicicleta, camion)")
):
    """2 y 5. Consultar todos los espacios, con filtro opcional por tipo de vehículo."""
    sql, params = "SELECT * FROM espacios", []
    if tipo_vehiculo:
        sql += " WHERE tipo_vehiculo = %s"
        params.append(tipo_vehiculo.value)
    with conectar() as conn:
        return conn.execute(sql + " ORDER BY id", params).fetchall()


@app.get("/espacios/{espacio_id}", response_model=Espacio)
def consultar_espacio(espacio_id: int):
    """3. Consultar un espacio por ID."""
    with conectar() as conn:
        return obtener_o_404(conn, espacio_id)


@app.put("/espacios/{espacio_id}", response_model=Espacio)
def actualizar_espacio(espacio_id: int, datos: EspacioActualizar):
    """4. Actualizar la información de un espacio (parcial)."""
    cambios = datos.model_dump(exclude_none=True)
    conn = conectar()
    try:
        obtener_o_404(conn, espacio_id)
        if cambios:
            cambios = {k: (v.value if isinstance(v, Enum) else v) for k, v in cambios.items()}
            sets = ", ".join(f"{c} = %s" for c in cambios)
            with conn.transaction():
                conn.execute(f"UPDATE espacios SET {sets} WHERE id = %s",
                             (*cambios.values(), espacio_id))
        return obtener_o_404(conn, espacio_id)
    except UniqueViolation:
        raise HTTPException(409, "Ya existe otro espacio con ese número")
    finally:
        conn.close()


@app.delete("/espacios/{espacio_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_espacio(espacio_id: int):
    """6. Eliminar un espacio."""
    conn = conectar()
    try:
        obtener_o_404(conn, espacio_id)
        with conn.transaction():
            conn.execute("DELETE FROM espacios WHERE id = %s", (espacio_id,))
    finally:
        conn.close()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
