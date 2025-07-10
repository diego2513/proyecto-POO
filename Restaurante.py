from datetime import date 
from typing import Optional
import sqlite3
import tkinter
from tkinter import ttk, messagebox
#from modelos.producto import Producto  Esto se pondrá en los módulos 
#from producto import Producto  

class Producto:
    def __init__(self, codigo:str, nombre: str, precio:float, cantidad:int, unidad_medida:str, familia:str, ubicacion:str, fecha_ingreso:date, fecha_vencimiento:Optional[date], agotado:bool, stock_minimo: int):
        self.codigo= codigo
        self.nombre= nombre
        self.precio= precio
        self.cantidad= cantidad
        self.unidad_medida= unidad_medida
        self.familia= familia
        self.ubicacion= ubicacion
        self.fecha_ingreso= fecha_ingreso
        self.fecha_vencimiento= fecha_vencimiento
        self.agotado= agotado
        self.stock_minimo= stock_minimo

    def mostrar_info(self):
          return (
            f"Producto: {self.nombre} ({self.codigo})\n"
            f"Cantidad: {self.cantidad} {self.unidad_medida}\n"
            f"Precio: ${self.precio:.2f}\n"
            f"Categoría: {self.familia}\n"
            f"Ubicación: {self.ubicacion}\n"
            f"Fecha ingreso: {self.fecha_ingreso}\n"
            f"Fecha vencimiento: {self.fecha_vencimiento or 'No Aplica'}\n"
            f"Stock minimo:{self.stock_minimo}\n"
            f"Agotado: {'Sí' if self.agotado else 'No'}"
        )
    def actualizar_stock(self, cantidad:int): # Modifica la cantidad disponible de un producto
        self.cantidad += cantidad
        if self.cantidad <= 0:
            self.cantidad = 0
            self.agotado= True
        else:
            self.agotado = False

    def verificar_stock_minimo(self)-> bool:  # Compara la cantidad total con el stock_minimo correspondiente al producto
        return self.cantidad <= self.stock_minimo

class Ingrediente(Producto): # Representa los insumos basicos para preparar productos finales
    def __init__(self, codigo, nombre, precio, cantidad, unidad_medida, familia, ubicacion, fecha_ingreso, fecha_vencimiento, agotado, stock_minimo):
        super().__init__(codigo, nombre, precio, cantidad, unidad_medida, familia, ubicacion, fecha_ingreso, fecha_vencimiento, agotado,stock_minimo)

    def dias_para_vencer(self)-> int | None:
        if self.fecha_vencimiento is None:
            return None
        return (self.fecha_vencimiento - date.today()).days
    
    
    def se_puede_usar(self) -> bool:  # Indica si el producto aun sirve o no 
        if self.fecha_vencimiento is None:
            return True
        return self.fecha_vencimiento >= date.today()
    
    def mostrar_info_detallada(self) -> str: # Muestra info detallada 
        dias = self.dias_para_vencer()
        estado = "útil" if self.se_puede_usar() else "No útil"
        if dias is None:
            texto = "No tiene fecha de vencimiento"
        elif dias > 0:
            texto = f"Faltan {dias} días para vencer"
        elif dias == 0:
            texto= "Vence Hoy"
        else:
            texto = f"Vencido hace {-dias} días"

        return (f"{self.mostrar_info()}\n"
                f"{texto}\n"
                f"Estado: {estado}")


class Productofinal(Producto):   #
    def __init__(self, codigo, nombre, precio, cantidad, unidad_medida, familia, ubicacion, fecha_ingreso, fecha_vencimiento, agotado, stock_minimo, receta: dict[Ingrediente, float]):
        super().__init__(codigo, nombre, precio, cantidad, unidad_medida, familia, ubicacion, fecha_ingreso, fecha_vencimiento, agotado, stock_minimo)
        self.receta= receta # Ahora es un diccionario: : Ingrediente → cantidad requerida 

    def cantidad_requerida(self) -> str: # Para indicar ingredientes con su cantidad requerida para un producto final
        if not self.receta:
            return " Este producto no tiene receta asignada"
        texto = "Receta:\n"
        for ingrediente, cantidad in self.receta.items():
            texto += f"- {ingrediente.nombre}: {cantidad} {ingrediente.unidad_medida}\n"
        return texto.strip()
    
    def mostrar_info(self) -> str:
        info_base = super().mostrar_info()
        return f"{info_base}\n{self.cantidad_requerida()}"

  

class Movimiento:                # Para registrar y rastrear salidas y entradas del inventario ( Qué, cuando, cuánto, quién, por qué)
    def __init__(self, tipo: str, producto: Producto, cantidad:int, fecha, usuario:str, motivo:str):
        self.tipo= tipo
        self.producto= producto
        self.cantidad= cantidad
        self.fecha= fecha
        self.usuario= usuario
        self.motivo= motivo 

    def mostrar_detalle(self)-> str:  # Indicará los detalles del movimiento
               return (
            f"Fecha: {self.fecha}\n"
            f"Tipo: {self.tipo.title()}\n"
            f"Producto: {self.producto.nombre} (Código: {self.producto.codigo})\n"
            f"Cantidad: {self.cantidad} {self.producto.unidad_medida}\n"
            f"Usuario: {self.usuario}\n"
            f"Motivo: {self.motivo}"
        )
    
    def __str__(self):   # Para leer el mensaje 
        return self.mostrar_detalle()

class Inventario:                               #def inventario en sqlite
    def __init__(self):
        self.productos:list[Producto]=[]
        self.movimientos:list[Movimiento]= [] 
        self.conn= None
        self.cursor= None

    def database(self):                                 #def inventario en sqlite
        self.conn = sqlite3.connect('BOD.db')
        self.cursor = self.conn.cursor()

        self.cursor.execute(
            """CREATE TABLE IF NOT EXISTS BOD(
            codigo TEXT PRIMARY KEY,
            nombre TEXT,
            precio REAL,
            cantidad INTEGER,
            unidad_medida TEXT,
            familia TEXT,
            ubicacion TEXT,
            fecha_ingreso TEXT,
            fecha_vencimiento TEXT,
            stock_minimo INTEGER,
            agotado INTEGER
            )"""
        )
        self.conn.commit()
        
    def agregar_producto(self, producto: Producto): # Para agregar producto a la base de datos y lista 
        try:
            if not self.conn:
                self.database()

            self.cursor.execute("SELECT codigo FROM BOD WHERE codigo = ?", (producto.codigo,))
            if self.cursor.fetchone():
                return False

            self.cursor.execute('''
            INSERT INTO BOD (
                codigo, nombre, precio, cantidad, unidad_medida, familia,
                ubicacion, fecha_ingreso, fecha_vencimiento,
                stock_minimo, agotado
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            producto.codigo,
            producto.nombre,
            producto.precio,
            producto.cantidad,
            producto.unidad_medida,
            producto.familia,
            producto.ubicacion,
            producto.fecha_ingreso.isoformat(),
            producto.fecha_vencimiento.isoformat() if producto.fecha_vencimiento else None,
            producto.stock_minimo,
            int(producto.agotado)
        ))
            self.conn.commit()
            self.productos.append(producto)
            return True
        except Exception as e:
            print(f"Error al agregar producto: {e}")
            return False
        
    def cargar_productos_BD(self):      # Para cargar productos desde la base de datos 
        if not self.conn:
            self.database()
        self.cursor.execute("SELECT * FROM BOD")
        filas = self.cursor.fetchall()

        for fila in filas:
            producto = Ingrediente(
            codigo=fila[0],
            nombre=fila[1],
            precio=fila[2],
            cantidad=fila[3],
            unidad_medida=fila[4],
            familia=fila[5],
            ubicacion=fila[6],
            fecha_ingreso=date.fromisoformat(fila[7]),
            fecha_vencimiento=date.fromisoformat(fila[8]) if fila[8] else None,
            agotado=bool(fila[11]),
            stock_minimo=fila[10],
            
        )
        self.productos.append(producto) 

    def registrar_movimientos(self, movimiento: Movimiento): # actualiza el stock del producto, guarda movimiento en la lista
        producto = movimiento.producto
        if movimiento.tipo == "entrada":
            producto.actualizar_stock(movimiento.cantidad)

        elif movimiento.tipo == "salida":
            if producto.cantidad < movimiento.cantidad:
                print(f"Error: No hay suficiente stock para retirar {movimiento.cantidad} unidades de {producto.nombre}.") # En caso de que no haya x cantidad de productos para una salida
                return False
            producto.actualizar_stock(-movimiento.cantidad)
        else:
            raise ValueError ("Tipo de movimiento invalido (entrada/salida)")
        
        self.movimientos.append(movimiento)
        return True

    def buscar_producto(self, codigo: str) -> Optional[Producto]:
        for producto in self.productos:
            if producto.codigo == codigo:
                return producto 
            return None  


    def ver_inventario(self): # Indica el inventario completo
        if not self.productos:
            return ("El inventario está vacío")
        return "\n\n".join([producto.mostrar_info() for producto in self.productos])
    
    def productos_por_vencer(self) -> list[Producto]: # indica una lista de productos proximos a vencer en 8 dias 
            proximos = []
            for producto in self.productos:
                if isinstance(producto, Ingrediente):
                    dias = producto.dias_para_vencer()
                    if dias is not None and 0 <= dias <= 8:
                        proximos.append(producto)
            return proximos

    def generar_alertas(self) -> list[str]: # Genera avisos sobre los productos que estan a punto de agotarse segun el stock minimo y los productos vencidos 
        avisos= []
        for producto in self.productos:
            if producto.verificar_stock_minimo():
                 avisos.append(f"¡Alerta!: {producto.nombre} ({producto.codigo}) está por agotarse.")
            if isinstance(producto, Ingrediente):
                if not producto.se_puede_usar():
                    avisos.append(f"¡Alerta!: {producto.nombre} ({producto.codigo}) está vencido.")
        return avisos


    def consultar_movimientos(self) -> list[Movimiento]: # Sencillamente, retorna la lista de movimientos guardados
        return self.movimientos

    def puede_prepararse(self, producto: Productofinal) -> bool:
        for ingrediente, cantidad_requerida in producto.receta.items():
            if ingrediente not in self.productos:
                return False
            if not ingrediente.se_puede_usar() or ingrediente.cantidad < cantidad_requerida:
                return False
        return True

    def usar_ingredientes(self, producto: Productofinal, usuario: str, motivo: str): # Resta los ingredientes empleados para un prroducto final y registra el movimiento
        if not self.puede_prepararse(producto):
            raise ValueError("No se puede preparar la orden: ingredientes insuficientes o vencidos.")
        for ingrediente, cantidad_requerida in producto.receta.items():
            ingrediente.actualizar_stock(-cantidad_requerida)
            movimiento = Movimiento("salida", ingrediente, cantidad_requerida, date.today(), usuario, motivo)
            self.registrar_movimientos(movimiento)

class Interfaz:              # Hay que corregir cositas                                      #INTERFAZZZZZZZZZZZZZZZZZZZZZZZZZZZ
    def __init__(self):
        self.inventario = Inventario()
        self.inventario.database() 

        self.root = tkinter.Tk()
        self.root.title("PYTHUNAL")
        self.root.geometry("500x400")
        
        self.crear_interfaz()
    
    def crear_interfaz(self):
        titulo = tkinter.Label(self.root, text="Añadir Producto al Inventario", 
                         font=("times new roman", 16, "bold"))
        titulo.pack(pady=10)

        frame_campos = tkinter.Frame(self.root)
        frame_campos.pack(pady=10, padx=20, fill="x")
        
        tkinter.Label(frame_campos, text="Código:").grid(row=0, column=0, sticky="w", pady=5)
        self.nty_codigo = tkinter.Entry(frame_campos, width=30)
        self.nty_codigo.grid(row=0, column=1, pady=5, padx=10)
        
        tkinter.Label(frame_campos, text="Nombre:").grid(row=1, column=0, sticky="w", pady=5)
        self.nty_name = tkinter.Entry(frame_campos, width=30)
        self.nty_name.grid(row=1, column=1, pady=5, padx=10)
        
        tkinter.Label(frame_campos, text="Precio:").grid(row=2, column=0, sticky="w", pady=5)
        self.nty_precio = tkinter.Entry(frame_campos, width=30)
        self.nty_precio.grid(row=2, column=1, pady=5, padx=10)
        
        tkinter.Label(frame_campos, text="Cantidad:").grid(row=3, column=0, sticky="w", pady=5)
        self.nty_cantidad = tkinter.Entry(frame_campos, width=30)
        self.nty_cantidad.grid(row=3, column=1, pady=5, padx=10)
        
        tkinter.Label(frame_campos, text="Medida:").grid(row=4, column=0, sticky="w", pady=5)
        self.nty_medida = tkinter.Entry(frame_campos, width=30)
        self.nty_medida.grid(row=4, column=1, pady=5, padx=10)
        
        tkinter.Label(frame_campos, text="Fecha Ingreso:").grid(row=5, column=0, sticky="w", pady=5)
        self.nty_fecha = tkinter.Entry(frame_campos, width=30)
        self.nty_fecha.grid(row=5, column=1, pady=5, padx=10)
        self.nty_fecha.insert(0, "2025-06-16")  
        
        frame_botones = tkinter.Frame(self.root)
        frame_botones.pack(pady=20)
        
        btn_agregar = tkinter.Button(frame_botones, text="Añadir Producto", 
                               command=self.agregar_producto, 
                               bg="#FF0015", fg="white", 
                               font=("Arial", 12, "bold"),
                               width=15)
        btn_agregar.pack(side="left", padx=10)
    def agregar_producto(self):
        """Función que se ejecuta al hacer clic en 'Añadir Producto'"""
        codigo = self.nty_codigo.get().strip()
        nombre = self.nty_name.get().strip()
        precio = self.nty_precio.get().strip()
        cantidad = self.nty_cantidad.get().strip()
        medida = self.nty_medida.get().strip()
        fecha = self.nty_fecha.get().strip()

        if not all([codigo, nombre, precio, cantidad, medida, fecha]):
            messagebox.showerror("Error", "Todos los campos son obligatorios")
            return

        try:
            precio = int(precio)
            cantidad = int(cantidad)
        except ValueError:
            messagebox.showerror("Error", "Precio y cantidad deben ser números")
            return
        
        if self.inventario.agregar_producto(codigo, nombre, precio, cantidad, medida, fecha):
            messagebox.showinfo("Éxito", "Producto agregado correctamente")
            self.nty_codigo.delete(0, tkinter.END)
            self.nty_name.delete(0, tkinter.END)
            self.nty_precio.delete(0, tkinter.END)
            self.nty_cantidad.delete(0, tkinter.END)
            self.nty_medida.delete(0, tkinter.END)
            self.nty_fecha.delete(0, tkinter.END)
            self.nty_fecha.insert(0, "2025-06-16") 
        else:
            messagebox.showerror("Error", "No se pudo agregar el producto")
        self.conn.close()
    
    def ejecutar(self):
        """Ejecutar la interfaz"""
        self.root.mainloop()

    def buscar_producto(self, codigo: str)-> Optional[Producto]:
        pass 
    def registrar_movimiento(self, movimiento: Movimiento):
        pass
    def ver_inventario(self)-> str:
        pass 
    def productos_por_vencer(self) -> list[Producto]:
        pass
    def generar_alertas(self)-> list[str]:
        pass
    def consultar_movimientos(self) -> list[Movimiento]: 
        pass
class sistema:
    def __init__(self):
        pass
    def cargar_datos(self):
        pass
    def Guardar_datos(self):
        pass
    def iniciar_sesion(self):
        pass
    def mostrar_menu_principal(self):
        pass
    def registar_entrada(self):
        pass
    def registar_salida(self):
        pass 
    def mostrar_inventario(self):
        pass
    def genarar_informe(self):
        pass
    def cargar_productos(self):
        pass


#app = Interfaz()
#app.ejecutar()
#i = Inventario()
#i.database()


