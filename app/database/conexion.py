"""Conexiones a PostgreSQL configuradas mediante variables de entorno."""

import os

import psycopg
from psycopg.rows import dict_row


def conectar() -> psycopg.Connection:
    """Abre una conexión PostgreSQL usando ``DATABASE_URL``."""
    # DATABASE_URL contiene la dirección y credenciales de PostgreSQL.
    url = os.getenv("DATABASE_URL")
    if not url:
        raise RuntimeError(
            "Falta DATABASE_URL; consulta la sección de configuración del README."
        )
    # dict_row permite acceder a cada columna por su nombre, por ejemplo fila["id"].
    # autocommit guarda cada consulta sin necesitar conn.commit() explícito.
    return psycopg.connect(url, row_factory=dict_row, autocommit=True)
