"""Reglas de negocio para administrar usuarios."""

import hashlib
import secrets

from psycopg.errors import UniqueViolation

from app.models.usuario import Usuario
from app.repositories import usuario_repository

# Número de veces que PBKDF2 procesa la contraseña para hacer más costoso
# probar contraseñas adivinadas.
ITERACIONES_HASH = 600_000


# Errores propios del negocio que las rutas convierten en estados HTTP.
class UsuarioNoEncontradoError(Exception):
    """El usuario solicitado no existe."""


class CorreoDuplicadoError(Exception):
    """El correo ya está registrado."""


def hash_contrasena(contrasena: str) -> str:
    """Genera un hash PBKDF2-SHA256 con sal aleatoria por contraseña."""
    # Una sal distinta hace que dos contraseñas iguales tengan hashes diferentes.
    sal = secrets.token_bytes(16)
    # PBKDF2 deriva el hash sin guardar la contraseña original.
    derivado = hashlib.pbkdf2_hmac(
        "sha256", contrasena.encode("utf-8"), sal, ITERACIONES_HASH
    )
    return f"pbkdf2_sha256${ITERACIONES_HASH}${sal.hex()}${derivado.hex()}"


def crear(nombre: str, correo: str, contrasena: str) -> Usuario:
    # Normaliza el correo y guarda solo el hash de la contraseña.
    try:
        return usuario_repository.crear(
            nombre, correo.strip().lower(), hash_contrasena(contrasena)
        )
    except UniqueViolation as error:
        # La base tiene una restricción UNIQUE para evitar correos repetidos.
        raise CorreoDuplicadoError("El correo ya está registrado") from error


def listar() -> list[Usuario]:
    # Las respuestas HTTP filtran el hash mediante UsuarioRespuesta.
    return usuario_repository.listar()


def obtener(usuario_id: int) -> Usuario:
    # Si el repositorio no devuelve un usuario, se informa como error de negocio.
    usuario = usuario_repository.obtener(usuario_id)
    if usuario is None:
        raise UsuarioNoEncontradoError
    return usuario


def actualizar(
    usuario_id: int, nombre: str, correo: str, contrasena: str
) -> Usuario:
    # Se normaliza el correo y nunca se envía la contraseña sin hash al repositorio.
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
        # El repositorio devuelve None cuando no encontró el ID solicitado.
        raise UsuarioNoEncontradoError
    return usuario


def eliminar(usuario_id: int) -> None:
    # Si no se eliminó ninguna fila, el usuario no existía.
    if not usuario_repository.eliminar(usuario_id):
        raise UsuarioNoEncontradoError
