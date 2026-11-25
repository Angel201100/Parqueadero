"""Pruebas unitarias del CRUD de usuarios sin conexión a PostgreSQL."""

from decimal import Decimal
import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

import main
from app.models.espacio import Espacio
from app.models.usuario import Usuario
from app.services import usuario_service
from app.services.usuario_service import CorreoDuplicadoError


class UsuariosApiTests(unittest.TestCase):
    def setUp(self):
        self.cliente = TestClient(main.app)
        self.usuario = Usuario(
            id=1,
            nombre="Ana Pérez",
            correo="ana@example.com",
            contrasena_hash="pbkdf2_sha256$test",
        )

    def test_openapi_expone_operaciones_crud_de_usuarios(self):
        paths = main.app.openapi()["paths"]
        self.assertIn("/usuarios/", paths)
        self.assertEqual(
            {"get", "post"},
            set(paths["/usuarios/"]),
        )
        self.assertEqual(
            {"get", "put", "delete"},
            set(paths["/usuarios/{usuario_id}"]),
        )
        self.assertIn("/espacios", paths)
        self.assertEqual(
            {"get", "post"},
            set(paths["/espacios"]),
        )

    @patch("app.services.usuario_service.usuario_repository.crear")
    def test_crear_responde_sin_exponer_hash(self, crear):
        crear.return_value = self.usuario
        respuesta = self.cliente.post(
            "/usuarios/",
            json={
                "nombre": "Ana Pérez",
                "correo": "ana@example.com",
                "contrasena": "secreto-seguro",
            },
        )

        self.assertEqual(201, respuesta.status_code)
        self.assertEqual(
            {"id": 1, "nombre": "Ana Pérez", "correo": "ana@example.com"},
            respuesta.json(),
        )
        self.assertNotIn("contrasena", respuesta.json())
        self.assertNotIn("contrasena_hash", respuesta.json())
        crear.assert_called_once()
        self.assertNotEqual("secreto-seguro", crear.call_args.args[2])

    @patch("app.services.espacio_service.espacio_repository.listar")
    def test_listado_espacios_conserva_filtro_existente(self, listar):
        listar.return_value = [
            Espacio(
                id=1,
                numero_espacio="M-01",
                tipo_vehiculo="moto",
                ubicacion="Nivel 1",
                tamano="pequeno",
                tarifa_hora=Decimal("1500.00"),
            )
        ]

        respuesta = self.cliente.get(
            "/espacios", params={"tipo_vehiculo": "moto"}
        )

        self.assertEqual(200, respuesta.status_code)
        self.assertEqual("M-01", respuesta.json()[0]["numero_espacio"])
        listar.assert_called_once_with("moto")

    def test_rechaza_correo_invalido_y_campos_obligatorios(self):
        datos = {
            "nombre": "Ana Pérez",
            "correo": "no-es-correo",
            "contrasena": "12345678",
        }
        self.assertEqual(422, self.cliente.post("/usuarios/", json=datos).status_code)
        del datos["contrasena"]
        self.assertEqual(422, self.cliente.post("/usuarios/", json=datos).status_code)

    @patch("app.services.usuario_service.usuario_repository.crear")
    def test_correo_duplicado_responde_409(self, crear):
        crear.side_effect = CorreoDuplicadoError("El correo ya está registrado")
        respuesta = self.cliente.post(
            "/usuarios/",
            json={
                "nombre": "Ana Pérez",
                "correo": "ana@example.com",
                "contrasena": "secreto-seguro",
            },
        )

        self.assertEqual(409, respuesta.status_code)

    @patch("app.services.usuario_service.usuario_repository.listar")
    def test_listado_no_expone_contrasenas(self, listar):
        listar.return_value = [self.usuario]
        respuesta = self.cliente.get("/usuarios/")

        self.assertEqual(200, respuesta.status_code)
        self.assertEqual(
            [{"id": 1, "nombre": "Ana Pérez", "correo": "ana@example.com"}],
            respuesta.json(),
        )

    @patch("app.services.usuario_service.usuario_repository.obtener")
    def test_consultar_usuario_inexistente_responde_404(self, obtener):
        obtener.return_value = None

        respuesta = self.cliente.get("/usuarios/999")

        self.assertEqual(404, respuesta.status_code)

    @patch("app.services.usuario_service.usuario_repository.actualizar")
    def test_actualizar_usuario_responde_sin_hash(self, actualizar):
        actualizar.return_value = self.usuario
        respuesta = self.cliente.put(
            "/usuarios/1",
            json={
                "nombre": "Ana Pérez",
                "correo": "ana@example.com",
                "contrasena": "nueva-clave-segura",
            },
        )

        self.assertEqual(200, respuesta.status_code)
        self.assertNotIn("contrasena_hash", respuesta.json())
        self.assertNotEqual("nueva-clave-segura", actualizar.call_args.args[3])

    @patch("app.services.usuario_service.usuario_repository.eliminar")
    def test_eliminar_usuario_responde_204(self, eliminar):
        eliminar.return_value = True

        respuesta = self.cliente.delete("/usuarios/1")

        self.assertEqual(204, respuesta.status_code)
        self.assertEqual(b"", respuesta.content)

    def test_hash_usa_sal_aleatoria_y_no_conserva_texto_plano(self):
        primero = usuario_service.hash_contrasena("secreto-seguro")
        segundo = usuario_service.hash_contrasena("secreto-seguro")

        self.assertTrue(primero.startswith("pbkdf2_sha256$600000$"))
        self.assertNotEqual(primero, segundo)
        self.assertNotIn("secreto-seguro", primero)


if __name__ == "__main__":
    unittest.main()
