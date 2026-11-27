"""Representación interna de un usuario almacenado en PostgreSQL."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Usuario:
    # Identificador que asigna PostgreSQL.
    id: int
    # Nombre completo de la persona.
    nombre: str
    # Dirección de correo única del usuario.
    correo: str
    # Hash de contraseña; nunca se guarda la contraseña original.
    contrasena_hash: str
