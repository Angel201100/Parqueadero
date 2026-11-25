"""Conexiones a PostgreSQL configuradas mediante variables de entorno."""

import os

import psycopg
from psycopg.rows import dict_row


def conectar() -> psycopg.Connection:
    """Abre una conexión PostgreSQL usando ``DATABASE_URL``."""
    url = os.getenv("DATABASE_URL")
    if not url:
        raise RuntimeError(
            "Falta DATABASE_URL; consulta la sección de configuración del README."
        )
    return psycopg.connect(url, row_factory=dict_row, autocommit=True)
