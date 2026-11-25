import sqlite3

# Nombre del archivo de la base de datos local
DB_NAME = "inventario.db"


def conectar_bd():
    """
    Establece y devuelve una conexión con la base de datos SQLite.
    Si el archivo 'inventario.db' no existe, SQLite lo crea automáticamente.
    """
    conexion = sqlite3.connect(DB_NAME)
    # Permite acceder a las columnas por nombre (ej. fila["nombre"])
    conexion.row_factory = sqlite3.Row
    return conexion


def inicializar_bd():
    """
    Crea la tabla 'productos' en la base de datos si aún no existe.
    """
    conexion = None
    try:
        conexion = conectar_bd()
        cursor = conexion.cursor()

        query_crear_tabla = """
        CREATE TABLE IF NOT EXISTS productos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            descripcion TEXT,
            cantidad INTEGER NOT NULL,
            precio REAL NOT NULL,
            categoria TEXT
        );
        """

        cursor.execute(query_crear_tabla)
        conexion.commit()

    except sqlite3.Error as error:
        if conexion:
            conexion.rollback()
        print(f"[Error BD] No se pudo inicializar la base de datos: {error}")

    finally:
        if conexion:
            conexion.close()


# ==============================================================================
# OPERACIONES CRUD, BÚSQUEDAS Y REPORTES
# ==============================================================================


def registrar_producto(nombre, descripcion, cantidad, precio, categoria):
    """
    Inserta un nuevo producto en la tabla 'productos'.
    Devuelve True si el registro fue exitoso, o False en caso de error.
    """
    conexion = None
    try:
        conexion = conectar_bd()
        cursor = conexion.cursor()

        # Usamos '?' como marcadores de posición para prevenir inyección SQL
        query = """
        INSERT INTO productos (nombre, descripcion, cantidad, precio, categoria)
        VALUES (?, ?, ?, ?, ?);
        """
        cursor.execute(query, (nombre, descripcion, cantidad, precio, categoria))
        conexion.commit()
        return True

    except sqlite3.Error as error:
        if conexion:
            conexion.rollback()
        print(f"[Error BD] No se pudo registrar el producto: {error}")
        return False

    finally:
        if conexion:
            conexion.close()


def obtener_todos_los_productos():
    """
    Recupera todos los productos registrados ordenados por ID ascendente.
    Devuelve una lista de filas (sqlite3.Row).
    """
    conexion = None
    try:
        conexion = conectar_bd()
        cursor = conexion.cursor()

        cursor.execute("SELECT * FROM productos ORDER BY id ASC;")
        return cursor.fetchall()

    except sqlite3.Error as error:
        print(f"[Error BD] No se pudieron obtener los productos: {error}")
        return []

    finally:
        if conexion:
            conexion.close()


def buscar_producto_por_id(producto_id):
    """
    Busca un único producto según su ID.
    Devuelve la fila del producto si existe, o None si no se encuentra.
    """
    conexion = None
    try:
        conexion = conectar_bd()
        cursor = conexion.cursor()

        cursor.execute("SELECT * FROM productos WHERE id = ?;", (producto_id,))
        return cursor.fetchone()

    except sqlite3.Error as error:
        print(f"[Error BD] Error al buscar producto por ID: {error}")
        return None

    finally:
        if conexion:
            conexion.close()


def buscar_productos_por_campo(campo, valor):
    """
    Funcionalidad opcional: Busca productos por 'nombre' o 'categoria'
    utilizando coincidencias parciales (LIKE).
    """
    # Validamos el nombre de la columna para evitar inyección SQL en el identificador
    if campo not in ("nombre", "categoria"):
        return []

    conexion = None
    try:
        conexion = conectar_bd()
        cursor = conexion.cursor()

        # Agregamos '%' antes y después para buscar coincidencias en cualquier parte del texto
        patron = f"%{valor}%"
        query = f"SELECT * FROM productos WHERE {campo} LIKE ? ORDER BY id ASC;"
        cursor.execute(query, (patron,))
        return cursor.fetchall()

    except sqlite3.Error as error:
        print(f"[Error BD] Error al buscar por {campo}: {error}")
        return []

    finally:
        if conexion:
            conexion.close()


def actualizar_producto(producto_id, nombre, descripcion, cantidad, precio, categoria):
    """
    Actualiza todos los datos de un producto existente identificado por su ID.
    Devuelve True si se actualizó al menos un registro, False en caso contrario.
    """
    conexion = None
    try:
        conexion = conectar_bd()
        cursor = conexion.cursor()

        query = """
        UPDATE productos
        SET nombre = ?,
            descripcion = ?,
            cantidad = ?,
            precio = ?,
            categoria = ?
        WHERE id = ?;
        """
        cursor.execute(
            query, (nombre, descripcion, cantidad, precio, categoria, producto_id)
        )
        conexion.commit()

        # rowcount indica cuántas filas fueron afectadas por el UPDATE
        return cursor.rowcount > 0

    except sqlite3.Error as error:
        if conexion:
            conexion.rollback()
        print(f"[Error BD] No se pudo actualizar el producto: {error}")
        return False

    finally:
        if conexion:
            conexion.close()


def eliminar_producto(producto_id):
    """
    Elimina un producto de la base de datos según su ID.
    Devuelve True si se eliminó el registro, False si no existía o hubo error.
    """
    conexion = None
    try:
        conexion = conectar_bd()
        cursor = conexion.cursor()

        cursor.execute("DELETE FROM productos WHERE id = ?;", (producto_id,))
        conexion.commit()

        return cursor.rowcount > 0

    except sqlite3.Error as error:
        if conexion:
            conexion.rollback()
        print(f"[Error BD] No se pudo eliminar el producto: {error}")
        return False

    finally:
        if conexion:
            conexion.close()


def reporte_bajo_stock(limite):
    """
    Devuelve una lista de productos cuya cantidad es menor o igual al límite indicado.
    Ordena los resultados de menor a mayor stock para priorizar los más críticos.
    """
    conexion = None
    try:
        conexion = conectar_bd()
        cursor = conexion.cursor()

        query = """
        SELECT * FROM productos
        WHERE cantidad <= ?
        ORDER BY cantidad ASC, id ASC;
        """
        cursor.execute(query, (limite,))
        return cursor.fetchall()

    except sqlite3.Error as error:
        print(f"[Error BD] Error al generar el reporte de bajo stock: {error}")
        return []

    finally:
        if conexion:
            conexion.close()
