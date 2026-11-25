"""Operaciones PostgreSQL para los usuarios."""

from typing import Optional

import psycopg

from app.database.conexion import conectar
from app.models.usuario import Usuario


def crear_tabla_usuarios(conn: psycopg.Connection) -> None:
    """Crea la tabla independiente de usuarios si todavía no existe."""
    conn.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            nombre VARCHAR(150) NOT NULL,
            correo VARCHAR(320) NOT NULL UNIQUE,
            contrasena_hash TEXT NOT NULL
        )
        """)


def crear(nombre: str, correo: str, contrasena_hash: str) -> Usuario:
    with conectar() as conn:
        fila = conn.execute(
            """
            INSERT INTO usuarios (nombre, correo, contrasena_hash)
            VALUES (%s, %s, %s)
            RETURNING id, nombre, correo, contrasena_hash
            """,
            (nombre, correo, contrasena_hash),
        ).fetchone()
    return Usuario(**fila)


def listar() -> list[Usuario]:
    with conectar() as conn:
        filas = conn.execute(
            """
            SELECT id, nombre, correo, contrasena_hash
            FROM usuarios
            ORDER BY id
            """
        ).fetchall()
    return [Usuario(**fila) for fila in filas]


def obtener(usuario_id: int) -> Optional[Usuario]:
    with conectar() as conn:
        fila = conn.execute(
            """
            SELECT id, nombre, correo, contrasena_hash
            FROM usuarios
            WHERE id = %s
            """,
            (usuario_id,),
        ).fetchone()
    return Usuario(**fila) if fila else None


def actualizar(
    usuario_id: int, nombre: str, correo: str, contrasena_hash: str
) -> Optional[Usuario]:
    with conectar() as conn:
        fila = conn.execute(
            """
            UPDATE usuarios
            SET nombre = %s, correo = %s, contrasena_hash = %s
            WHERE id = %s
            RETURNING id, nombre, correo, contrasena_hash
            """,
            (nombre, correo, contrasena_hash, usuario_id),
        ).fetchone()
    return Usuario(**fila) if fila else None


def eliminar(usuario_id: int) -> bool:
    with conectar() as conn:
        fila = conn.execute(
            "DELETE FROM usuarios WHERE id = %s RETURNING id",
            (usuario_id,),
        ).fetchone()
    return fila is not None
