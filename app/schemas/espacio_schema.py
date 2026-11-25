"""Esquemas de validación y respuesta para los espacios del parqueadero."""

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class TipoVehiculo(str, Enum):
    carro = "carro"
    moto = "moto"
    bicicleta = "bicicleta"
    camion = "camion"


class Tamano(str, Enum):
    pequeno = "pequeno"
    mediano = "mediano"
    grande = "grande"


class EspacioBase(BaseModel):
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

    numero_espacio: Optional[str] = Field(None, min_length=1, max_length=20)
    tipo_vehiculo: Optional[TipoVehiculo] = None
    ubicacion: Optional[str] = Field(None, min_length=1, max_length=100)
    tamano: Optional[Tamano] = None
    tarifa_hora: Optional[float] = Field(None, gt=0)


class EspacioRespuesta(EspacioBase):
    id: int
