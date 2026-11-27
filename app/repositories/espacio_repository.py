"""Consultas que guardan y recuperan espacios desde PostgreSQL."""

# Optional permite indicar que un espacio puede no existir en la base de datos.
from typing import Optional

# psycopg proporciona el tipo de conexión usado al crear la tabla.
import psycopg

# conectar abre una conexión PostgreSQL usando la configuración del proyecto.
from app.database.conexion import conectar

# Espacio representa cada fila recuperada desde la tabla.
from app.models.espacio import Espacio


def crear_tabla_espacios(conn: psycopg.Connection) -> None:
    """Crea la tabla y sus reglas si todavía no existe."""
    # CREATE TABLE IF NOT EXISTS evita un error si la tabla ya fue creada.
    conn.execute("""
        CREATE TABLE IF NOT EXISTS espacios (
            -- Identificador automático y clave principal de cada espacio.
            id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            -- No puede estar vacío y no se puede repetir.
            numero_espacio VARCHAR(20) NOT NULL UNIQUE,
            -- Tipo de vehículo permitido en este espacio.
            tipo_vehiculo VARCHAR(20) NOT NULL,
            -- Lugar donde está ubicado el espacio.
            ubicacion VARCHAR(100) NOT NULL,
            -- Tamaño del espacio.
            tamano VARCHAR(20) NOT NULL,
            -- Tarifa por hora: debe ser mayor que cero.
            tarifa_hora NUMERIC(10, 2) NOT NULL CHECK (tarifa_hora > 0)
        )
        """)


def crear(datos: dict) -> Espacio:
    """Inserta un espacio nuevo y devuelve el registro creado."""
    # El bloque abre y cierra la conexión incluso si ocurre un error.
    with conectar() as conn:
        # INSERT guarda los campos recibidos.
        # RETURNING pide a PostgreSQL que devuelva la fila recién creada.
        fila = conn.execute(
            """
            INSERT INTO espacios (
                numero_espacio, tipo_vehiculo, ubicacion, tamano, tarifa_hora
            )
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id, numero_espacio, tipo_vehiculo, ubicacion, tamano, tarifa_hora
            """,
            # Los valores se pasan aparte del SQL para que psycopg los inserte
            # de forma segura y correcta.
            (
                datos["numero_espacio"],
                datos["tipo_vehiculo"],
                datos["ubicacion"],
                datos["tamano"],
                datos["tarifa_hora"],
            ),
        ).fetchone()

    # Convierte la fila de la base de datos en el modelo Espacio.
    return Espacio(
        id=fila["id"],
        numero_espacio=fila["numero_espacio"],
        tipo_vehiculo=fila["tipo_vehiculo"],
        ubicacion=fila["ubicacion"],
        tamano=fila["tamano"],
        tarifa_hora=fila["tarifa_hora"],
    )


def listar(tipo_vehiculo: Optional[str] = None) -> list[Espacio]:
    """Devuelve todos los espacios o solo los de un tipo de vehículo."""
    with conectar() as conn:
        # Si recibimos un tipo, agregamos una condición para filtrar resultados.
        if tipo_vehiculo:
            filas = conn.execute(
                """
                SELECT id, numero_espacio, tipo_vehiculo, ubicacion, tamano, tarifa_hora
                FROM espacios
                WHERE tipo_vehiculo = %s
                ORDER BY id
                """,
                # El valor del filtro se envía separado de la consulta SQL.
                (tipo_vehiculo,),
            ).fetchall()
        else:
            # Sin filtro, se consultan todos los espacios.
            filas = conn.execute(
                """
                SELECT id, numero_espacio, tipo_vehiculo, ubicacion, tamano, tarifa_hora
                FROM espacios
                ORDER BY id
                """
            ).fetchall()

    # Convertimos cada fila obtenida en un objeto Espacio.
    espacios = []
    for fila in filas:
        espacio = Espacio(
            id=fila["id"],
            numero_espacio=fila["numero_espacio"],
            tipo_vehiculo=fila["tipo_vehiculo"],
            ubicacion=fila["ubicacion"],
            tamano=fila["tamano"],
            tarifa_hora=fila["tarifa_hora"],
        )
        # Agregamos el objeto a la lista que devolverá la función.
        espacios.append(espacio)

    return espacios


def obtener(espacio_id: int) -> Optional[Espacio]:
    """Busca un espacio por su ID."""
    with conectar() as conn:
        # fetchone devuelve una fila o None cuando el ID no existe.
        fila = conn.execute(
            """
            SELECT id, numero_espacio, tipo_vehiculo, ubicacion, tamano, tarifa_hora
            FROM espacios
            WHERE id = %s
            """,
            (espacio_id,),
        ).fetchone()

    # La función informa que no hubo resultado; el servicio decide cómo
    # convertirlo en una respuesta HTTP 404.
    if fila is None:
        return None

    # Si encontramos la fila, devolvemos sus valores como un objeto Espacio.
    return Espacio(
        id=fila["id"],
        numero_espacio=fila["numero_espacio"],
        tipo_vehiculo=fila["tipo_vehiculo"],
        ubicacion=fila["ubicacion"],
        tamano=fila["tamano"],
        tarifa_hora=fila["tarifa_hora"],
    )


def actualizar(espacio_id: int, cambios: dict) -> Optional[Espacio]:
    """Actualiza solo los campos recibidos y deja intactos los demás."""
    with conectar() as conn:
        # Primero buscamos el registro para conocer los valores actuales.
        fila = conn.execute(
            """
            SELECT id, numero_espacio, tipo_vehiculo, ubicacion, tamano, tarifa_hora
            FROM espacios
            WHERE id = %s
            """,
            (espacio_id,),
        ).fetchone()

        # Si el ID no existe, no hay nada que actualizar.
        if fila is None:
            return None

        # Para cada campo usamos el nuevo valor si llegó en "cambios".
        # Si no llegó, conservamos el valor que acabamos de leer de la base.
        # UPDATE escribe el registro y RETURNING devuelve la versión actualizada.
        fila = conn.execute(
            """
            UPDATE espacios
            SET numero_espacio = %s,
                tipo_vehiculo = %s,
                ubicacion = %s,
                tamano = %s,
                tarifa_hora = %s
            WHERE id = %s
            RETURNING id, numero_espacio, tipo_vehiculo, ubicacion, tamano, tarifa_hora
            """,
            (
                # dict.get(campo, valor_actual) conserva el valor actual
                # cuando el campo no está incluido en el diccionario cambios.
                cambios.get("numero_espacio", fila["numero_espacio"]),
                cambios.get("tipo_vehiculo", fila["tipo_vehiculo"]),
                cambios.get("ubicacion", fila["ubicacion"]),
                cambios.get("tamano", fila["tamano"]),
                cambios.get("tarifa_hora", fila["tarifa_hora"]),
                espacio_id,
            ),
        ).fetchone()

    # Si no se obtuvo una fila actualizada, devolvemos None.
    if fila is None:
        return None

    # Convertimos la fila actualizada en el objeto que espera el servicio.
    return Espacio(
        id=fila["id"],
        numero_espacio=fila["numero_espacio"],
        tipo_vehiculo=fila["tipo_vehiculo"],
        ubicacion=fila["ubicacion"],
        tamano=fila["tamano"],
        tarifa_hora=fila["tarifa_hora"],
    )


def eliminar(espacio_id: int) -> bool:
    """Elimina por ID y devuelve True si había un registro para borrar."""
    with conectar() as conn:
        # DELETE elimina la fila; RETURNING devuelve su ID si se encontró.
        fila = conn.execute(
            "DELETE FROM espacios WHERE id = %s RETURNING id",
            (espacio_id,),
        ).fetchone()

    # Si no hubo fila, ese ID no existía.
    if fila is None:
        return False

    # Si sí hubo fila, la eliminación se realizó.
    return True
