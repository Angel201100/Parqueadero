"""Reglas de negocio para administrar usuarios."""

import hashlib
import secrets

from psycopg.errors import UniqueViolation

from app.models.usuario import Usuario
from app.repositories import usuario_repository

ITERACIONES_HASH = 600_000


class UsuarioNoEncontradoError(Exception):
    """El usuario solicitado no existe."""


class CorreoDuplicadoError(Exception):
    """El correo ya está registrado."""


def hash_contrasena(contrasena: str) -> str:
    """Genera un hash PBKDF2-SHA256 con sal aleatoria por contraseña."""
    sal = secrets.token_bytes(16)
    derivado = hashlib.pbkdf2_hmac(
        "sha256", contrasena.encode("utf-8"), sal, ITERACIONES_HASH
    )
    return f"pbkdf2_sha256${ITERACIONES_HASH}${sal.hex()}${derivado.hex()}"


def crear(nombre: str, correo: str, contrasena: str) -> Usuario:
    try:
        return usuario_repository.crear(
            nombre, correo.strip().lower(), hash_contrasena(contrasena)
        )
    except UniqueViolation as error:
        raise CorreoDuplicadoError("El correo ya está registrado") from error


def listar() -> list[Usuario]:
    return usuario_repository.listar()


def obtener(usuario_id: int) -> Usuario:
    usuario = usuario_repository.obtener(usuario_id)
    if usuario is None:
        raise UsuarioNoEncontradoError
    return usuario


def actualizar(
    usuario_id: int, nombre: str, correo: str, contrasena: str
) -> Usuario:
    try:
        usuario = usuario_repository.actualizar(
            usuario_id,
            nombre,
            correo.strip().lower(),
            hash_contrasena(contrasena),
        )
    except UniqueViolation as error:
        raise CorreoDuplicadoError("El correo ya está registrado") from error
    if usuario is None:
        raise UsuarioNoEncontradoError
    return usuario


def eliminar(usuario_id: int) -> None:
    if not usuario_repository.eliminar(usuario_id):
        raise UsuarioNoEncontradoError
