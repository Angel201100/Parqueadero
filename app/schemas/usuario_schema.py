"""Esquemas HTTP para crear, actualizar y consultar usuarios."""

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


# Datos comunes requeridos para identificar a un usuario.
class UsuarioBase(BaseModel):
    nombre: str = Field(min_length=1, max_length=150, examples=["Ana Pérez"])
    correo: EmailStr = Field(examples=["ana@example.com"])

    @field_validator("nombre")
    @classmethod
    def nombre_no_vacio(cls, valor: str) -> str:
        # Quita espacios al inicio y final y rechaza cadenas vacías o de espacios.
        valor = valor.strip()
        if not valor:
            raise ValueError("El nombre es obligatorio")
        return valor


class UsuarioCrear(UsuarioBase):
    # La contraseña se valida aquí; el servicio la convierte en hash.
    contrasena: str = Field(min_length=8, max_length=128)


class UsuarioActualizar(UsuarioCrear):
    """PUT reemplaza los datos editables del usuario y exige todos los campos."""


class UsuarioRespuesta(UsuarioBase):
    # El ID se genera en PostgreSQL y aparece en las respuestas.
    id: int

    # Permite crear este esquema desde el modelo interno Usuario.
    model_config = ConfigDict(from_attributes=True)
