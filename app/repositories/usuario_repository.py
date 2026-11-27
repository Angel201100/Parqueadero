"""Consultas sencillas a la tabla de usuarios en PostgreSQL."""

from typing import Optional

import psycopg

# La función conectar abre la conexión usando DATABASE_URL.
from app.database.conexion import conectar

# Usuario es el objeto Python que representa cada fila recuperada.
from app.models.usuario import Usuario


def crear_tabla_usuarios(conn: psycopg.Connection) -> None:
    """Crea la tabla de usuarios si todavía no existe."""
    # UNIQUE evita almacenar dos usuarios con el mismo correo.
    # contrasena_hash guarda el resultado seguro, no la contraseña original.
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
        # INSERT agrega el usuario y RETURNING devuelve la fila creada.
        fila = conn.execute(
            """
            INSERT INTO usuarios (nombre, correo, contrasena_hash)
            VALUES (%s, %s, %s)
            RETURNING id, nombre, correo, contrasena_hash
            """,
            (nombre, correo, contrasena_hash),
        ).fetchone()

    # Creamos el objeto campo por campo para que sea fácil ver su contenido.
    return Usuario(
        id=fila["id"],
        nombre=fila["nombre"],
        correo=fila["correo"],
        contrasena_hash=fila["contrasena_hash"],
    )


def listar() -> list[Usuario]:
    """Devuelve todos los usuarios ordenados por ID."""
    with conectar() as conn:
        # ORDER BY mantiene siempre el mismo orden en la lista.
        filas = conn.execute(
            """
            SELECT id, nombre, correo, contrasena_hash
            FROM usuarios
            ORDER BY id
            """
        ).fetchall()

    # Convertimos cada fila de la consulta en un objeto Usuario.
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
        # fetchone devuelve una fila o None si no hay coincidencia.
        fila = conn.execute(
            """
            SELECT id, nombre, correo, contrasena_hash
            FROM usuarios
            WHERE id = %s
            """,
            (usuario_id,),
        ).fetchone()

    # None permite que el servicio responda que el usuario no existe.
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
        # UPDATE modifica los tres datos editables y RETURNING trae el resultado.
        fila = conn.execute(
            """
            UPDATE usuarios
            SET nombre = %s, correo = %s, contrasena_hash = %s
            WHERE id = %s
            RETURNING id, nombre, correo, contrasena_hash
            """,
            (nombre, correo, contrasena_hash, usuario_id),
        ).fetchone()

    # Si la consulta no modificó filas, ese ID no existe.
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
        # RETURNING permite saber si PostgreSQL encontró y borró el usuario.
        fila = conn.execute(
            "DELETE FROM usuarios WHERE id = %s RETURNING id",
            (usuario_id,),
        ).fetchone()

    # True significa que se borró una fila; False, que el ID no existía.
    if fila is None:
        return False
    return True
