"""Endpoints HTTP del CRUD de espacios del parqueadero."""

from typing import Optional

from fastapi import APIRouter, HTTPException, Query, Response, status

from app.schemas.espacio_schema import (
    EspacioActualizar,
    EspacioCrear,
    EspacioRespuesta,
    TipoVehiculo,
)
from app.services import espacio_service
from app.services.espacio_service import (
    EspacioNoEncontradoError,
    NumeroEspacioDuplicadoError,
)

router = APIRouter(prefix="/espacios", tags=["Espacios"])


@router.post("", response_model=EspacioRespuesta, status_code=status.HTTP_201_CREATED)
def crear_espacio(datos: EspacioCrear):
    try:
        return espacio_service.crear(datos.model_dump())
    except NumeroEspacioDuplicadoError as error:
        raise HTTPException(status_code=409, detail=str(error)) from error


@router.get("", response_model=list[EspacioRespuesta])
def listar_espacios(
    tipo_vehiculo: Optional[TipoVehiculo] = Query(
        None,
        description=(
            "Filtra por tipo de vehículo permitido "
            "(carro, moto, bicicleta, camion)"
        ),
    )
):
    return espacio_service.listar(tipo_vehiculo.value if tipo_vehiculo else None)


@router.get("/{espacio_id}", response_model=EspacioRespuesta)
def consultar_espacio(espacio_id: int):
    try:
        return espacio_service.obtener(espacio_id)
    except EspacioNoEncontradoError as error:
        raise HTTPException(
            status_code=404, detail=f"No existe el espacio con id {espacio_id}"
        ) from error


@router.put("/{espacio_id}", response_model=EspacioRespuesta)
def actualizar_espacio(espacio_id: int, datos: EspacioActualizar):
    try:
        return espacio_service.actualizar(
            espacio_id, datos.model_dump(exclude_none=True)
        )
    except EspacioNoEncontradoError as error:
        raise HTTPException(
            status_code=404, detail=f"No existe el espacio con id {espacio_id}"
        ) from error
    except NumeroEspacioDuplicadoError as error:
        raise HTTPException(status_code=409, detail=str(error)) from error


@router.delete("/{espacio_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_espacio(espacio_id: int):
    try:
        espacio_service.eliminar(espacio_id)
    except EspacioNoEncontradoError as error:
        raise HTTPException(
            status_code=404, detail=f"No existe el espacio con id {espacio_id}"
        ) from error
    return Response(status_code=status.HTTP_204_NO_CONTENT)
