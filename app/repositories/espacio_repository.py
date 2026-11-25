"""Operaciones PostgreSQL para los espacios del parqueadero."""

from typing import Optional

import psycopg

from app.database.conexion import conectar
from app.models.espacio import Espacio


def crear_tabla_espacios(conn: psycopg.Connection) -> None:
    """Crea la tabla de espacios si todavía no existe."""
    conn.execute("""
        CREATE TABLE IF NOT EXISTS espacios (
            id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            numero_espacio VARCHAR(20) NOT NULL UNIQUE,
            tipo_vehiculo VARCHAR(20) NOT NULL,
            ubicacion VARCHAR(100) NOT NULL,
            tamano VARCHAR(20) NOT NULL,
            tarifa_hora NUMERIC(10, 2) NOT NULL CHECK (tarifa_hora > 0)
        )
        """)


def crear(datos: dict) -> Espacio:
    with conectar() as conn:
        fila = conn.execute(
            """
            INSERT INTO espacios (
                numero_espacio, tipo_vehiculo, ubicacion, tamano, tarifa_hora
            )
            VALUES (%s, %s, %s, %s, %s)
            RETURNING *
            """,
            (
                datos["numero_espacio"],
                datos["tipo_vehiculo"],
                datos["ubicacion"],
                datos["tamano"],
                datos["tarifa_hora"],
            ),
        ).fetchone()
    return Espacio(**fila)


def listar(tipo_vehiculo: Optional[str] = None) -> list[Espacio]:
    sql = "SELECT * FROM espacios"
    parametros = []
    if tipo_vehiculo:
        sql += " WHERE tipo_vehiculo = %s"
        parametros.append(tipo_vehiculo)
    with conectar() as conn:
        filas = conn.execute(sql + " ORDER BY id", parametros).fetchall()
    return [Espacio(**fila) for fila in filas]


def obtener(espacio_id: int) -> Optional[Espacio]:
    with conectar() as conn:
        fila = conn.execute(
            "SELECT * FROM espacios WHERE id = %s", (espacio_id,)
        ).fetchone()
    return Espacio(**fila) if fila else None


def actualizar(espacio_id: int, cambios: dict) -> Optional[Espacio]:
    with conectar() as conn:
        fila = conn.execute(
            "SELECT * FROM espacios WHERE id = %s", (espacio_id,)
        ).fetchone()
        if fila is None:
            return None
        if cambios:
            sets = ", ".join(f"{columna} = %s" for columna in cambios)
            fila = conn.execute(
                f"UPDATE espacios SET {sets} WHERE id = %s RETURNING *",
                (*cambios.values(), espacio_id),
            ).fetchone()
    return Espacio(**fila) if fila else None


def eliminar(espacio_id: int) -> bool:
    with conectar() as conn:
        fila = conn.execute(
            "DELETE FROM espacios WHERE id = %s RETURNING id",
            (espacio_id,),
        ).fetchone()
    return fila is not None
