"""Consultas sencillas a la tabla de usuarios en PostgreSQL."""

from typing import Optional

import psycopg

from app.database.conexion import conectar
from app.models.usuario import Usuario


def crear_tabla_usuarios(conn: psycopg.Connection) -> None:
    """Crea la tabla de usuarios si todavía no existe."""
    conn.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            nombre VARCHAR(150) NOT NULL,
            correo VARCHAR(320) NOT NULL UNIQUE,
            contrasena_hash TEXT NOT NULL
        )
        """)


def crear(nombre: str, correo: str, contrasena_hash: str) -> Usuario:
    """Guarda un usuario nuevo y devuelve sus datos."""
    with conectar() as conn:
        fila = conn.execute(
            """
            INSERT INTO usuarios (nombre, correo, contrasena_hash)
            VALUES (%s, %s, %s)
            RETURNING id, nombre, correo, contrasena_hash
            """,
            (nombre, correo, contrasena_hash),
        ).fetchone()

    return Usuario(
        id=fila["id"],
        nombre=fila["nombre"],
        correo=fila["correo"],
        contrasena_hash=fila["contrasena_hash"],
    )


def listar() -> list[Usuario]:
    """Devuelve todos los usuarios ordenados por ID."""
    with conectar() as conn:
        filas = conn.execute(
            """
            SELECT id, nombre, correo, contrasena_hash
            FROM usuarios
            ORDER BY id
            """
        ).fetchall()

    usuarios = []
    for fila in filas:
        usuario = Usuario(
            id=fila["id"],
            nombre=fila["nombre"],
            correo=fila["correo"],
            contrasena_hash=fila["contrasena_hash"],
        )
        usuarios.append(usuario)

    return usuarios


def obtener(usuario_id: int) -> Optional[Usuario]:
    """Busca un usuario por su ID."""
    with conectar() as conn:
        fila = conn.execute(
            """
            SELECT id, nombre, correo, contrasena_hash
            FROM usuarios
            WHERE id = %s
            """,
            (usuario_id,),
        ).fetchone()

    if fila is None:
        return None

    return Usuario(
        id=fila["id"],
        nombre=fila["nombre"],
        correo=fila["correo"],
        contrasena_hash=fila["contrasena_hash"],
    )


def actualizar(
    usuario_id: int, nombre: str, correo: str, contrasena_hash: str
) -> Optional[Usuario]:
    """Actualiza los datos del usuario y devuelve el resultado."""
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

    if fila is None:
        return None

    return Usuario(
        id=fila["id"],
        nombre=fila["nombre"],
        correo=fila["correo"],
        contrasena_hash=fila["contrasena_hash"],
    )


def eliminar(usuario_id: int) -> bool:
    """Elimina un usuario y devuelve si existía."""
    with conectar() as conn:
        fila = conn.execute(
            "DELETE FROM usuarios WHERE id = %s RETURNING id",
            (usuario_id,),
        ).fetchone()

    if fila is None:
        return False
    return True
