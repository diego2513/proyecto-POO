DIAGRAMA DE CLASES 

classDiagram
direction TB
    class Producto {
	    +codigo: str
	    +nombre: str
	    +precio: float
	    +cantidad: int
	    +unidad_medida: str
	    +familia: str
	    +ubicacion: str
	    +fecha_ingreso: date
	    +fecha_vencimiento:optional[date]
	    +agotado: Bool
	    +stock_minimo: int
	    +mostrar_info()
	    +actualizar_stock(cantidad)
	    +verificar_stock_minimo()
    }
    class Movimiento {
	    +tipo: str
	    +producto: Producto
	    +cantidad: int
	    +fecha: date
	    +usuario: str
	    +motivo: str
	    +mostrar_detalle()
    }
    class Ingrediente {
	    +proveedor: str
	    +mostrar_info()
	    +se_puede_usar()
    }
    class Productofinal {
	    +receta: list[Ingrediente]
	    +mostrar_info()
	    +aplicar_descuento()
	    +restablecer_precio()
	    +aplicar_promocion()
	    +restar_ingredientes()
    }
    class Inventario {
	    +producto:  list[Producto]
	    +movimientos: list[movimiento]
	    +conn: sqlite3.Connection
	    +cursor: sqlite3.Cursor
	    +__init__()
	    +database()
	    +agregar_producto(p: producto) bool
	    +cargar_productos_BD() None
    }
    class Interfaz {
	    +inventario: Inventario
	    + __init__()
	    +crear_interfaz()
	    +ejecutar()
	    +buscar_producto()
	    +registrar_movimiento()
	    +agregar_producto()
	    +ver_inventario()
	    +productos_por_vencer()
	    +generar_alertas()
	    +consultar_movimientos()
    }
    class sistema {
	    +inventario: Inventario
	    +__init__()
	    +cargar_datos()
	    +guardar_datos()
	    +iniciar_sesion()
	    +mostrar_menu_principal()
	    +registar_entrada()
	    +registar_salida()
	    +mostrar_inventario()
	    +genarar_informe()
	    +cargar_productos()
    }
    class Movimiento_2["Movimiento"] {
    }
    class Ingrediente_2["Ingrediente"] {
    }

	note for Producto "Clase Padre"

    Producto <|-- Ingrediente
    Producto <|-- Productofinal
    Producto -- Movimiento
    Producto --o Inventario
    Producto ..|> sistema
    Producto -- Interfaz
    Productofinal --* Ingrediente
    Movimiento --o Inventario
    Interfaz -- Inventario
    sistema --* Inventario
    sistema --* Movimiento_2
    sistema ..|> Ingrediente_2
