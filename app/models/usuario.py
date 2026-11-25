"""Representación interna de un usuario almacenado en PostgreSQL."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Usuario:
    id: int
    nombre: str
    correo: str
    contrasena_hash: str
