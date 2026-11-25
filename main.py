import database as db

# Intentamos importar colorama para mejorar la experiencia visual en la terminal.
# Si no está instalado en el entorno, definimos constantes vacías para que el
# programa siga funcionando sin errores.
try:
    from colorama import Fore, Style, init

    init(autoreset=True)
except ImportError:

    class _SinColor:
        def __getattr__(self, _):
            return ""

    Fore = Style = _SinColor()


# ==============================================================================
# FUNCIONES AUXILIARES DE ENTRADA Y VISUALIZACIÓN
# ==============================================================================


def pedir_texto_obligatorio(mensaje):
    """Solicita un texto al usuario y repite hasta que no esté vacío."""
    while True:
        valor = input(mensaje).strip()
        if valor:
            return valor
        print(f"{Fore.RED}Este campo es obligatorio. Intenta nuevamente.")


def pedir_entero(mensaje, permitir_cero=True):
    """Solicita un número entero válido (>= 0 o > 0 según corresponda)."""
    minimo = 0 if permitir_cero else 1
    while True:
        entrada = input(mensaje).strip()
        try:
            numero = int(entrada)
            if numero >= minimo:
                return numero
            print(f"{Fore.RED}El valor debe ser mayor o igual a {minimo}.")
        except ValueError:
            print(f"{Fore.RED}Entrada inválida. Ingresa un número entero.")


def pedir_flotante(mensaje):
    """Solicita un número decimal (precio) válido mayor o igual a 0."""
    while True:
        entrada = input(mensaje).strip().replace(",", ".")
        try:
            numero = float(entrada)
            if numero >= 0:
                return numero
            print(f"{Fore.RED}El precio no puede ser negativo.")
        except ValueError:
            print(f"{Fore.RED}Entrada inválida. Ingresa un valor numérico.")


def mostrar_tabla_productos(productos):
    """Imprime una lista de productos en formato de tabla alineada."""
    if not productos:
        print(f"{Fore.YELLOW}No se encontraron productos para mostrar.")
        return

    encabezado = (
        f"{'ID':<5} | {'Nombre':<20} | {'Categoría':<15} | "
        f"{'Cant.':<7} | {'Precio':<10} | {'Descripción'}"
    )
    print(f"\n{Fore.CYAN}{Style.BRIGHT}{encabezado}")
    print(f"{Fore.CYAN}{'-' * 85}")

    for prod in productos:
        # Recortamos textos muy largos solo para mantener la alineación visual
        nombre = (
            prod["nombre"][:18] + ".."
            if len(prod["nombre"]) > 20
            else prod["nombre"]
        )
        categoria = prod["categoria"] or "-"
        categoria = categoria[:13] + ".." if len(categoria) > 15 else categoria
        descripcion = prod["descripcion"] or "-"

        fila = (
            f"{prod['id']:<5} | {nombre:<20} | {categoria:<15} | "
            f"{prod['cantidad']:<7} | ${prod['precio']:<9.2f} | {descripcion}"
        )
        print(fila)
    print()


# ==============================================================================
# OPCIONES DEL MENÚ PRINCIPAL
# ==============================================================================


def opcion_registrar():
    """Flujo para dar de alta un nuevo producto en el inventario."""
    print(f"\n{Fore.CYAN}{Style.BRIGHT}--- REGISTRAR NUEVO PRODUCTO ---")
    nombre = pedir_texto_obligatorio("Nombre del producto: ")
    descripcion = input("Descripción (opcional): ").strip()
    cantidad = pedir_entero("Cantidad inicial: ", permitir_cero=True)
    precio = pedir_flotante("Precio unitario: ")
    categoria = input("Categoría (opcional): ").strip()

    if db.registrar_producto(nombre, descripcion, cantidad, precio, categoria):
        print(f"{Fore.GREEN}Producto '{nombre}' registrado correctamente.")
    else:
        print(f"{Fore.RED}No se pudo registrar el producto.")


def opcion_visualizar():
    """Muestra todos los productos cargados en la base de datos."""
    print(f"\n{Fore.CYAN}{Style.BRIGHT}--- LISTADO DE PRODUCTOS ---")
    productos = db.obtener_todos_los_productos()
    mostrar_tabla_productos(productos)


def opcion_actualizar():
    """Permite buscar un producto por ID y modificar sus campos."""
    print(f"\n{Fore.CYAN}{Style.BRIGHT}--- ACTUALIZAR PRODUCTO ---")
    producto_id = pedir_entero(
        "Ingresa el ID del producto a actualizar: ", permitir_cero=False
    )
    producto = db.buscar_producto_por_id(producto_id)

    if not producto:
        print(f"{Fore.YELLOW}No existe ningún producto con ID {producto_id}.")
        return

    print(f"\nEditando: {Style.BRIGHT}{producto['nombre']}")
    print(f"{Fore.YELLOW}(Presiona Enter sin escribir nada para mantener el valor actual)\n")

    # Solicitamos cada campo; si queda vacío, conservamos el valor original
    nuevo_nombre = (
        input(f"Nombre [{producto['nombre']}]: ").strip() or producto["nombre"]
    )

    desc_actual = producto["descripcion"] or ""
    nueva_desc = input(f"Descripción [{desc_actual}]: ").strip()
    if nueva_desc == "":
        nueva_desc = desc_actual

    # Validación opcional para cantidad
    while True:
        cant_input = input(f"Cantidad [{producto['cantidad']}]: ").strip()
        if cant_input == "":
            nueva_cantidad = producto["cantidad"]
            break
        try:
            nueva_cantidad = int(cant_input)
            if nueva_cantidad >= 0:
                break
            print(f"{Fore.RED}La cantidad debe ser mayor o igual a 0.")
        except ValueError:
            print(f"{Fore.RED}Ingresa un número entero válido.")

    # Validación opcional para precio
    while True:
        precio_input = (
            input(f"Precio [{producto['precio']:.2f}]: ").strip().replace(",", ".")
        )
        if precio_input == "":
            nuevo_precio = producto["precio"]
            break
        try:
            nuevo_precio = float(precio_input)
            if nuevo_precio >= 0:
                break
            print(f"{Fore.RED}El precio no puede ser negativo.")
        except ValueError:
            print(f"{Fore.RED}Ingresa un valor numérico válido.")

    cat_actual = producto["categoria"] or ""
    nueva_cat = input(f"Categoría [{cat_actual}]: ").strip()
    if nueva_cat == "":
        nueva_cat = cat_actual

    if db.actualizar_producto(
        producto_id, nuevo_nombre, nueva_desc, nueva_cantidad, nuevo_precio, nueva_cat
    ):
        print(f"{Fore.GREEN}Producto ID {producto_id} actualizado con éxito.")
    else:
        print(f"{Fore.RED}Ocurrió un error al actualizar el producto.")


def opcion_eliminar():
    """Elimina un producto previo aviso y confirmación por parte del usuario."""
    print(f"\n{Fore.CYAN}{Style.BRIGHT}--- ELIMINAR PRODUCTO ---")
    producto_id = pedir_entero(
        "Ingresa el ID del producto a eliminar: ", permitir_cero=False
    )
    producto = db.buscar_producto_por_id(producto_id)

    if not producto:
        print(f"{Fore.YELLOW}No existe ningún producto con ID {producto_id}.")
        return

    mostrar_tabla_productos([producto])
    confirmacion = (
        input(f"{Fore.YELLOW}¿Seguro que deseas eliminar este producto? (s/n): ")
        .strip()
        .lower()
    )

    if confirmacion == "s":
        if db.eliminar_producto(producto_id):
            print(f"{Fore.GREEN}Producto eliminado correctamente.")
        else:
            print(f"{Fore.RED}No se pudo eliminar el producto.")
    else:
        print(f"{Fore.CYAN}Operación cancelada.")


def opcion_buscar():
    """Submenú de búsqueda por ID (obligatoria), nombre o categoría (opcionales)."""
    print(f"\n{Fore.CYAN}{Style.BRIGHT}--- BUSCAR PRODUCTOS ---")
    print("1. Buscar por ID")
    print("2. Buscar por Nombre")
    print("3. Buscar por Categoría")

    criterio = input("Elige un criterio de búsqueda (1-3): ").strip()

    if criterio == "1":
        producto_id = pedir_entero("Ingresa el ID a buscar: ", permitir_cero=False)
        producto = db.buscar_producto_por_id(producto_id)
        mostrar_tabla_productos([producto] if producto else [])
    elif criterio == "2":
        texto = pedir_texto_obligatorio("Ingresa el nombre (o parte del nombre): ")
        resultados = db.buscar_productos_por_campo("nombre", texto)
        mostrar_tabla_productos(resultados)
    elif criterio == "3":
        texto = pedir_texto_obligatorio("Ingresa la categoría a buscar: ")
        resultados = db.buscar_productos_por_campo("categoria", texto)
        mostrar_tabla_productos(resultados)
    else:
        print(f"{Fore.RED}Opción de búsqueda no válida.")


def opcion_reporte_bajo_stock():
    """Genera un reporte con los productos cuyo stock sea <= al límite ingresado."""
    print(f"\n{Fore.CYAN}{Style.BRIGHT}--- REPORTE DE BAJO STOCK ---")
    limite = pedir_entero(
        "Mostrar productos con cantidad igual o inferior a: ", permitir_cero=True
    )
    productos = db.reporte_bajo_stock(limite)

    if productos:
        print(
            f"{Fore.YELLOW}Se encontraron {len(productos)} producto(s) con stock <= {limite}:"
        )
        mostrar_tabla_productos(productos)
    else:
        print(f"{Fore.GREEN}No hay productos con stock igual o inferior a {limite}.")


# ==============================================================================
# BUCLE PRINCIPAL DE LA APLICACIÓN
# ==============================================================================


def mostrar_menu():
    """Imprime las opciones disponibles en la terminal."""
    print(f"{Fore.BLUE}{Style.BRIGHT}=========================================")
    print(f"{Fore.BLUE}{Style.BRIGHT}     SISTEMA DE GESTIÓN DE INVENTARIO    ")
    print(f"{Fore.BLUE}{Style.BRIGHT}=========================================")
    print("1. Registrar nuevo producto")
    print("2. Visualizar todos los productos")
    print("3. Actualizar producto (por ID)")
    print("4. Eliminar producto (por ID)")
    print("5. Buscar producto (ID, Nombre o Categoría)")
    print("6. Reporte de bajo stock")
    print("7. Salir")
    print(f"{Fore.BLUE}-----------------------------------------")


def main():
    """Punto de entrada de la aplicación."""
    # Aseguramos que la base de datos y la tabla existan antes de iniciar el menú
    db.inicializar_bd()

    while True:
        mostrar_menu()
        opcion = input("Selecciona una opción (1-7): ").strip()

        if opcion == "1":
            opcion_registrar()
        elif opcion == "2":
            opcion_visualizar()
        elif opcion == "3":
            opcion_actualizar()
        elif opcion == "4":
            opcion_eliminar()
        elif opcion == "5":
            opcion_buscar()
        elif opcion == "6":
            opcion_reporte_bajo_stock()
        elif opcion == "7":
            print(f"\n{Fore.CYAN}Saliendo del sistema. ¡Hasta luego!")
            break
        else:
            print(f"{Fore.RED}Opción inválida. Por favor, elige un número del 1 al 7.\n")


if __name__ == "__main__":
    main()
