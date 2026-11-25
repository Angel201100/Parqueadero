"""Representación interna de un espacio almacenado en PostgreSQL."""

from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class Espacio:
    id: int
    numero_espacio: str
    tipo_vehiculo: str
    ubicacion: str
    tamano: str
    tarifa_hora: Decimal
