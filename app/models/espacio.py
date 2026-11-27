"""Representación interna de un espacio almacenado en PostgreSQL."""

from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class Espacio:
    # Identificador que asigna PostgreSQL.
    id: int
    # Código legible que identifica el espacio en el parqueadero.
    numero_espacio: str
    # Categoría de vehículo que puede ocuparlo.
    tipo_vehiculo: str
    # Lugar físico donde se encuentra.
    ubicacion: str
    # Tamaño permitido para el espacio.
    tamano: str
    # Precio que se cobra por hora.
    tarifa_hora: Decimal
