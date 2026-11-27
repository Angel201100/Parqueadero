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
    """Guarda un espacio nuevo y devuelve sus datos."""
    with conectar() as conn:
        fila = conn.execute(
            """
            INSERT INTO espacios (
                numero_espacio, tipo_vehiculo, ubicacion, tamano, tarifa_hora
            )
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id, numero_espacio, tipo_vehiculo, ubicacion, tamano, tarifa_hora
            """,
            (
                datos["numero_espacio"],
                datos["tipo_vehiculo"],
                datos["ubicacion"],
                datos["tamano"],
                datos["tarifa_hora"],
            ),
        ).fetchone()

    return Espacio(
        id=fila["id"],
        numero_espacio=fila["numero_espacio"],
        tipo_vehiculo=fila["tipo_vehiculo"],
        ubicacion=fila["ubicacion"],
        tamano=fila["tamano"],
        tarifa_hora=fila["tarifa_hora"],
    )


def listar(tipo_vehiculo: Optional[str] = None) -> list[Espacio]:
    """Devuelve todos los espacios, con filtro de vehículo si se solicita."""
    with conectar() as conn:
        if tipo_vehiculo:
            filas = conn.execute(
                """
                SELECT id, numero_espacio, tipo_vehiculo, ubicacion, tamano, tarifa_hora
                FROM espacios
                WHERE tipo_vehiculo = %s
                ORDER BY id
                """,
                (tipo_vehiculo,),
            ).fetchall()
        else:
            filas = conn.execute(
                """
                SELECT id, numero_espacio, tipo_vehiculo, ubicacion, tamano, tarifa_hora
                FROM espacios
                ORDER BY id
                """
            ).fetchall()

    espacios = []
    for fila in filas:
        espacio = Espacio(
            id=fila["id"],
            numero_espacio=fila["numero_espacio"],
            tipo_vehiculo=fila["tipo_vehiculo"],
            ubicacion=fila["ubicacion"],
            tamano=fila["tamano"],
            tarifa_hora=fila["tarifa_hora"],
        )
        espacios.append(espacio)

    return espacios


def obtener(espacio_id: int) -> Optional[Espacio]:
    """Busca un espacio por su ID."""
    with conectar() as conn:
        fila = conn.execute(
            """
            SELECT id, numero_espacio, tipo_vehiculo, ubicacion, tamano, tarifa_hora
            FROM espacios
            WHERE id = %s
            """,
            (espacio_id,),
        ).fetchone()

    if fila is None:
        return None

    return Espacio(
        id=fila["id"],
        numero_espacio=fila["numero_espacio"],
        tipo_vehiculo=fila["tipo_vehiculo"],
        ubicacion=fila["ubicacion"],
        tamano=fila["tamano"],
        tarifa_hora=fila["tarifa_hora"],
    )


def actualizar(espacio_id: int, cambios: dict) -> Optional[Espacio]:
    """Actualiza los campos enviados y conserva los demás."""
    with conectar() as conn:
        fila = conn.execute(
            """
            SELECT id, numero_espacio, tipo_vehiculo, ubicacion, tamano, tarifa_hora
            FROM espacios
            WHERE id = %s
            """,
            (espacio_id,),
        ).fetchone()
        if fila is None:
            return None

        fila = conn.execute(
            """
            UPDATE espacios
            SET numero_espacio = %s,
                tipo_vehiculo = %s,
                ubicacion = %s,
                tamano = %s,
                tarifa_hora = %s
            WHERE id = %s
            RETURNING id, numero_espacio, tipo_vehiculo, ubicacion, tamano, tarifa_hora
            """,
            (
                cambios.get("numero_espacio", fila["numero_espacio"]),
                cambios.get("tipo_vehiculo", fila["tipo_vehiculo"]),
                cambios.get("ubicacion", fila["ubicacion"]),
                cambios.get("tamano", fila["tamano"]),
                cambios.get("tarifa_hora", fila["tarifa_hora"]),
                espacio_id,
            ),
        ).fetchone()

    if fila is None:
        return None

    return Espacio(
        id=fila["id"],
        numero_espacio=fila["numero_espacio"],
        tipo_vehiculo=fila["tipo_vehiculo"],
        ubicacion=fila["ubicacion"],
        tamano=fila["tamano"],
        tarifa_hora=fila["tarifa_hora"],
    )


def eliminar(espacio_id: int) -> bool:
    """Elimina un espacio y devuelve si existía."""
    with conectar() as conn:
        fila = conn.execute(
            "DELETE FROM espacios WHERE id = %s RETURNING id",
            (espacio_id,),
        ).fetchone()

    if fila is None:
        return False
    return True
