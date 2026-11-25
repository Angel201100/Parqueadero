"""Reglas de negocio para administrar espacios del parqueadero."""

from enum import Enum

from psycopg.errors import UniqueViolation

from app.models.espacio import Espacio
from app.repositories import espacio_repository


class EspacioNoEncontradoError(Exception):
    """El espacio solicitado no existe."""


class NumeroEspacioDuplicadoError(Exception):
    """El número de espacio ya está asignado a otro registro."""


def _normalizar_enums(datos: dict) -> dict:
    return {
        campo: valor.value if isinstance(valor, Enum) else valor
        for campo, valor in datos.items()
    }


def crear(datos: dict) -> Espacio:
    try:
        return espacio_repository.crear(_normalizar_enums(datos))
    except UniqueViolation as error:
        raise NumeroEspacioDuplicadoError(
            f"Ya existe el espacio '{datos['numero_espacio']}'"
        ) from error


def listar(tipo_vehiculo: str | None = None) -> list[Espacio]:
    return espacio_repository.listar(tipo_vehiculo)


def obtener(espacio_id: int) -> Espacio:
    espacio = espacio_repository.obtener(espacio_id)
    if espacio is None:
        raise EspacioNoEncontradoError
    return espacio


def actualizar(espacio_id: int, cambios: dict) -> Espacio:
    try:
        espacio = espacio_repository.actualizar(
            espacio_id, _normalizar_enums(cambios)
        )
    except UniqueViolation as error:
        raise NumeroEspacioDuplicadoError(
            "Ya existe otro espacio con ese número"
        ) from error
    if espacio is None:
        raise EspacioNoEncontradoError
    return espacio


def eliminar(espacio_id: int) -> None:
    if not espacio_repository.eliminar(espacio_id):
        raise EspacioNoEncontradoError
