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

# Todas las rutas de este archivo comienzan con /espacios.
router = APIRouter(prefix="/espacios", tags=["Espacios"])


@router.post("", response_model=EspacioRespuesta, status_code=status.HTTP_201_CREATED)
def crear_espacio(datos: EspacioCrear):
    # El esquema revisa los datos antes de que lleguen al servicio.
    try:
        return espacio_service.crear(datos.model_dump())
    # Un número repetido se informa como conflicto HTTP 409.
    except NumeroEspacioDuplicadoError as error:
        raise HTTPException(status_code=409, detail=str(error)) from error


@router.get("", response_model=list[EspacioRespuesta])
def listar_espacios(
    # FastAPI valida que el filtro sea uno de los valores permitidos.
    tipo_vehiculo: Optional[TipoVehiculo] = Query(
        None,
        description=(
            "Filtra por tipo de vehículo permitido "
            "(carro, moto, bicicleta, camion)"
        ),
    )
):
    # Si hay filtro, se pasa su texto al servicio; si no, se consultan todos.
    return espacio_service.listar(tipo_vehiculo.value if tipo_vehiculo else None)


@router.get("/{espacio_id}", response_model=EspacioRespuesta)
def consultar_espacio(espacio_id: int):
    # El servicio busca el ID y lanza un error si no existe.
    try:
        return espacio_service.obtener(espacio_id)
    # Ese error se convierte en una respuesta HTTP 404.
    except EspacioNoEncontradoError as error:
        raise HTTPException(
            status_code=404, detail=f"No existe el espacio con id {espacio_id}"
        ) from error


@router.put("/{espacio_id}", response_model=EspacioRespuesta)
def actualizar_espacio(espacio_id: int, datos: EspacioActualizar):
    # exclude_none=True permite actualizar solo los campos enviados.
    try:
        return espacio_service.actualizar(
            espacio_id, datos.model_dump(exclude_none=True)
        )
    # Se informa si el ID no existe o si el número nuevo ya está ocupado.
    except EspacioNoEncontradoError as error:
        raise HTTPException(
            status_code=404, detail=f"No existe el espacio con id {espacio_id}"
        ) from error
    except NumeroEspacioDuplicadoError as error:
        raise HTTPException(status_code=409, detail=str(error)) from error


@router.delete("/{espacio_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_espacio(espacio_id: int):
    # El servicio borra el espacio o indica que no encontró ese ID.
    try:
        espacio_service.eliminar(espacio_id)
    except EspacioNoEncontradoError as error:
        raise HTTPException(
            status_code=404, detail=f"No existe el espacio con id {espacio_id}"
        ) from error
    # 204 significa que se eliminó correctamente y no se devuelve contenido.
    return Response(status_code=status.HTTP_204_NO_CONTENT)
