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

# Todas las rutas de este archivo comienzan con /usuarios.
router = APIRouter(prefix="/usuarios", tags=["Usuarios"])


@router.post("/", response_model=UsuarioRespuesta, status_code=status.HTTP_201_CREATED)
def crear_usuario(datos: UsuarioCrear):
    # El esquema valida nombre, correo y contraseña antes de llamar al servicio.
    try:
        return usuario_service.crear(datos.nombre, datos.correo, datos.contrasena)
    # El correo es único; si ya existe respondemos con HTTP 409.
    except CorreoDuplicadoError as error:
        raise HTTPException(status_code=409, detail=str(error)) from error


@router.get("/", response_model=list[UsuarioRespuesta])
def listar_usuarios():
    # El esquema de respuesta evita que el hash de contraseña salga en la API.
    return usuario_service.listar()


@router.get("/{usuario_id}", response_model=UsuarioRespuesta)
def consultar_usuario(usuario_id: int):
    # Busca un usuario y traduce el caso inexistente a HTTP 404.
    try:
        return usuario_service.obtener(usuario_id)
    except UsuarioNoEncontradoError as error:
        raise HTTPException(status_code=404, detail="Usuario no encontrado") from error


@router.put("/{usuario_id}", response_model=UsuarioRespuesta)
def actualizar_usuario(usuario_id: int, datos: UsuarioActualizar):
    # PUT reemplaza los campos editables; todos son requeridos por el esquema.
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
    # El servicio indica si el usuario se pudo eliminar.
    try:
        usuario_service.eliminar(usuario_id)
    except UsuarioNoEncontradoError as error:
        raise HTTPException(status_code=404, detail="Usuario no encontrado") from error
    # 204 confirma que se eliminó sin devolver un cuerpo.
    return Response(status_code=status.HTTP_204_NO_CONTENT)
