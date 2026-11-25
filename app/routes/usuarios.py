"""Endpoints REST del CRUD independiente de usuarios."""

from fastapi import APIRouter, HTTPException, Response, status

from app.schemas.usuario_schema import (
    UsuarioActualizar,
    UsuarioCrear,
    UsuarioRespuesta,
)
from app.services import usuario_service
from app.services.usuario_service import (
    CorreoDuplicadoError,
    UsuarioNoEncontradoError,
)

router = APIRouter(prefix="/usuarios", tags=["Usuarios"])


@router.post("/", response_model=UsuarioRespuesta, status_code=status.HTTP_201_CREATED)
def crear_usuario(datos: UsuarioCrear):
    try:
        return usuario_service.crear(datos.nombre, datos.correo, datos.contrasena)
    except CorreoDuplicadoError as error:
        raise HTTPException(status_code=409, detail=str(error)) from error


@router.get("/", response_model=list[UsuarioRespuesta])
def listar_usuarios():
    return usuario_service.listar()


@router.get("/{usuario_id}", response_model=UsuarioRespuesta)
def consultar_usuario(usuario_id: int):
    try:
        return usuario_service.obtener(usuario_id)
    except UsuarioNoEncontradoError as error:
        raise HTTPException(status_code=404, detail="Usuario no encontrado") from error


@router.put("/{usuario_id}", response_model=UsuarioRespuesta)
def actualizar_usuario(usuario_id: int, datos: UsuarioActualizar):
    try:
        return usuario_service.actualizar(
            usuario_id, datos.nombre, datos.correo, datos.contrasena
        )
    except CorreoDuplicadoError as error:
        raise HTTPException(status_code=409, detail=str(error)) from error
    except UsuarioNoEncontradoError as error:
        raise HTTPException(status_code=404, detail="Usuario no encontrado") from error


@router.delete("/{usuario_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_usuario(usuario_id: int):
    try:
        usuario_service.eliminar(usuario_id)
    except UsuarioNoEncontradoError as error:
        raise HTTPException(status_code=404, detail="Usuario no encontrado") from error
    return Response(status_code=status.HTTP_204_NO_CONTENT)
