"""Pruebas de la API. Usa DATABASE_URL (idealmente una rama/base de pruebas de Neon)."""
from fastapi.testclient import TestClient
import main

with TestClient(main.app) as c:
    with main.conectar() as conn:
        conn.execute("TRUNCATE espacios RESTART IDENTITY")

    a = {"numero_espacio": "A-01", "tipo_vehiculo": "carro", "ubicacion": "Sótano 1",
         "tamano": "mediano", "tarifa_hora": 3500}
    m = {**a, "numero_espacio": "M-01", "tipo_vehiculo": "moto", "tamano": "pequeno", "tarifa_hora": 1500}
    r = c.post("/espacios", json=a); assert r.status_code == 201, r.text; id1 = r.json()["id"]
    assert c.post("/espacios", json=m).status_code == 201
    assert c.post("/espacios", json=a).status_code == 409
    assert c.post("/espacios", json={**a, "numero_espacio": "X", "tarifa_hora": -5}).status_code == 422
    assert len(c.get("/espacios").json()) == 2
    f = c.get("/espacios", params={"tipo_vehiculo": "moto"}).json()
    assert len(f) == 1 and f[0]["numero_espacio"] == "M-01"
    assert c.get("/espacios", params={"tipo_vehiculo": "avion"}).status_code == 422
    assert c.get(f"/espacios/{id1}").json()["numero_espacio"] == "A-01"
    assert c.get("/espacios/999").status_code == 404
    u = c.put(f"/espacios/{id1}", json={"tarifa_hora": 4000}).json()
    assert u["tarifa_hora"] == 4000 and u["ubicacion"] == "Sótano 1"
    assert c.put(f"/espacios/{id1}", json={"numero_espacio": "M-01"}).status_code == 409
    assert c.delete(f"/espacios/{id1}").status_code == 204
    assert c.get(f"/espacios/{id1}").status_code == 404
    with main.conectar() as conn:
        conn.execute("TRUNCATE espacios RESTART IDENTITY")
print("TODAS LAS PRUEBAS OK")
