"""Reglas de negocio para administrar espacios del parqueadero."""

from enum import Enum

from psycopg.errors import UniqueViolation

from app.models.espacio import Espacio
from app.repositories import espacio_repository


# Estos errores separan los problemas de negocio de los detalles de PostgreSQL.
class EspacioNoEncontradoError(Exception):
    """El espacio solicitado no existe."""


class NumeroEspacioDuplicadoError(Exception):
    """El número de espacio ya está asignado a otro registro."""


def _normalizar_enums(datos: dict) -> dict:
    # Los esquemas pueden entregar valores Enum; la base de datos guarda texto.
    return {
        campo: valor.value if isinstance(valor, Enum) else valor
        for campo, valor in datos.items()
    }


def crear(datos: dict) -> Espacio:
    # Convierte los Enum a texto y pide al repositorio guardar el registro.
    try:
        return espacio_repository.crear(_normalizar_enums(datos))
    # PostgreSQL usa UniqueViolation cuando se repite numero_espacio.
    except UniqueViolation as error:
        raise NumeroEspacioDuplicadoError(
            f"Ya existe el espacio '{datos['numero_espacio']}'"
        ) from error


def listar(tipo_vehiculo: str | None = None) -> list[Espacio]:
    # El repositorio decide si trae todo o aplica el filtro de tipo.
    return espacio_repository.listar(tipo_vehiculo)


def obtener(espacio_id: int) -> Espacio:
    # El repositorio devuelve None si no encuentra el ID.
    espacio = espacio_repository.obtener(espacio_id)
    if espacio is None:
        # La ruta traduce este error a una respuesta HTTP 404.
        raise EspacioNoEncontradoError
    return espacio


def actualizar(espacio_id: int, cambios: dict) -> Espacio:
    # Convierte los valores y delega la consulta de actualización al repositorio.
    try:
        espacio = espacio_repository.actualizar(
            espacio_id, _normalizar_enums(cambios)
        )
    except UniqueViolation as error:
        raise NumeroEspacioDuplicadoError(
            "Ya existe otro espacio con ese número"
        ) from error
    if espacio is None:
        # El ID no existía, por eso no se pudo actualizar.
        raise EspacioNoEncontradoError
    return espacio


def eliminar(espacio_id: int) -> None:
    # El repositorio devuelve False cuando no había un espacio con ese ID.
    if not espacio_repository.eliminar(espacio_id):
        raise EspacioNoEncontradoError
