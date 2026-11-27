"""Esquemas de validación y respuesta para los espacios del parqueadero."""

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


# Tipos de vehículo válidos para crear, filtrar o actualizar un espacio.
class TipoVehiculo(str, Enum):
    carro = "carro"
    moto = "moto"
    bicicleta = "bicicleta"
    camion = "camion"


# Tamaños válidos aceptados por la API.
class Tamano(str, Enum):
    pequeno = "pequeno"
    mediano = "mediano"
    grande = "grande"


# Campos compartidos por las solicitudes de creación y las respuestas.
class EspacioBase(BaseModel):
    # Field define restricciones y ejemplos que aparecen en Swagger.
    numero_espacio: str = Field(..., min_length=1, max_length=20, examples=["A-01"])
    tipo_vehiculo: TipoVehiculo
    ubicacion: str = Field(
        ..., min_length=1, max_length=100, examples=["Sótano 1, zona norte"]
    )
    tamano: Tamano
    tarifa_hora: float = Field(..., gt=0, examples=[3500])


class EspacioCrear(EspacioBase):
    """Campos obligatorios para registrar un espacio."""


class EspacioActualizar(BaseModel):
    """Campos opcionales para actualizar parcialmente un espacio."""

    # None significa que el cliente no pidió cambiar ese campo.
    numero_espacio: Optional[str] = Field(None, min_length=1, max_length=20)
    tipo_vehiculo: Optional[TipoVehiculo] = None
    ubicacion: Optional[str] = Field(None, min_length=1, max_length=100)
    tamano: Optional[Tamano] = None
    tarifa_hora: Optional[float] = Field(None, gt=0)


class EspacioRespuesta(EspacioBase):
    # La base de datos asigna el ID al crear el espacio.
    id: int
