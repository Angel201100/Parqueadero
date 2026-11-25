"""Pruebas de integración para la API de espacios.

Estas pruebas se conectan a la base indicada por ``DATABASE_URL`` y vacían la
tabla ``espacios`` al comenzar y terminar. Usa únicamente una base desechable
o una rama de pruebas; nunca ejecutes este archivo contra datos de producción.
"""

from fastapi.testclient import TestClient

import main


def vaciar_espacios() -> None:
    """Deja la tabla sin registros y reinicia el contador de IDs.

    Solo debe utilizarse desde esta prueba de integración, contra una base
    desechable, ya que TRUNCATE elimina todos los espacios existentes.
    """
    with main.conectar() as conn:
        conn.execute("TRUNCATE espacios RESTART IDENTITY")


def ejecutar_pruebas() -> None:
    """Comprueba los flujos principales de creación, consulta y mantenimiento."""
    # TestClient ejecuta el ciclo de vida de FastAPI, incluida la creación de la tabla.
    with TestClient(main.app) as cliente:
        vaciar_espacios()

        carro = {
            "numero_espacio": "A-01",
            "tipo_vehiculo": "carro",
            "ubicacion": "Sótano 1",
            "tamano": "mediano",
            "tarifa_hora": 3500,
        }
        moto = {
            **carro,
            "numero_espacio": "M-01",
            "tipo_vehiculo": "moto",
            "tamano": "pequeno",
            "tarifa_hora": 1500,
        }

        try:
            # Crear registros y verificar los conflictos y datos inválidos.
            respuesta = cliente.post("/espacios", json=carro)
            assert respuesta.status_code == 201, respuesta.text
            espacio_id = respuesta.json()["id"]
            assert cliente.post("/espacios", json=moto).status_code == 201
            assert cliente.post("/espacios", json=carro).status_code == 409
            tarifa_invalida = {**carro, "numero_espacio": "X", "tarifa_hora": -5}
            assert cliente.post("/espacios", json=tarifa_invalida).status_code == 422

            # Consultar la colección completa y aplicar un filtro válido o inválido.
            assert len(cliente.get("/espacios").json()) == 2
            filtrados = cliente.get("/espacios", params={"tipo_vehiculo": "moto"}).json()
            assert len(filtrados) == 1 and filtrados[0]["numero_espacio"] == "M-01"
            assert cliente.get(
                "/espacios", params={"tipo_vehiculo": "avion"}
            ).status_code == 422

            # Consultar un registro existente e identificar IDs inexistentes.
            assert cliente.get(f"/espacios/{espacio_id}").json()["numero_espacio"] == "A-01"
            assert cliente.get("/espacios/999").status_code == 404

            # Actualizar parcialmente, comprobar conflictos y eliminar el registro.
            actualizacion = cliente.put(
                f"/espacios/{espacio_id}", json={"tarifa_hora": 4000}
            ).json()
            assert actualizacion["tarifa_hora"] == 4000
            assert actualizacion["ubicacion"] == "Sótano 1"
            assert cliente.put(
                f"/espacios/{espacio_id}", json={"numero_espacio": "M-01"}
            ).status_code == 409
            assert cliente.delete(f"/espacios/{espacio_id}").status_code == 204
            assert cliente.get(f"/espacios/{espacio_id}").status_code == 404
        finally:
            # También limpia los datos de prueba si falla una aserción.
            vaciar_espacios()

    print("TODAS LAS PRUEBAS OK")


if __name__ == "__main__":
    ejecutar_pruebas()
