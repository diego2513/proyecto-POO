from datetime import date 
from typing import Optional
import sqlite3
import tkinter
from tkinter import ttk, messagebox
#from modelos.producto import Producto 

class Producto:
    def __init__(self, codigo:str, nombre: str, precio:float, cantidad:int, unidad_medida:str, familia:str, ubicacion:str, fecha_ingreso:date, fecha_vencimiento:Optional[date], agotado:bool, stock_minimo: int = 5):
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
    def actualizar_stock(self, cantidad:int):
        self.cantidad += cantidad
        if self.cantidad <= 0:
            self.cantidad = 0
            self.agotado= True
        else:
            self.agotado = False

    def verificar_stock_minimo(self)-> bool:
        return self.cantidad <= self.stock_minimo

class Ingrediente(Producto):
    def __init__(self, codigo, nombre, precio, cantidad, unidad_medid, familia, ubicacion, fecha_ingreso, fecha_vencimiento, agotado, stock_minimo, proveedor:str, es_refrigerado:bool ):
        super().__init__(codigo, nombre, precio, cantidad, unidad_medid, familia, ubicacion, fecha_ingreso, fecha_vencimiento, agotado,stock_minimo)
        self.proveedor= proveedor
        self.es_refrigerado= es_refrigerado

    def mostrar_info(self)-> str:
         info_base = super().mostrar_info()
         info_nueva = (
        f"\nProveedor: {self.proveedor}\n"
        f"Requiere refrigeración: {'Sí' if self.es_refrigerado else 'No'}")
         return info_base + info_nueva

    def requiere_refrigerar(self)-> bool:
        return self.es_refrigerado
    
    def se_puede_usar(self) -> bool:
        if self.fecha_vencimiento is None:
            return True
        return self.fecha_vencimiento >= date.today()

class Bebida(Producto):
    def __init__(self, codigo, nombre, precio, cantidad, unidad_medid, familia, ubicacion, fecha_ingreso, fecha_vencimiento, agotado,stock_minimo, es_alcoholica:bool):
        super().__init__(codigo, nombre, precio, cantidad, unidad_medid, familia, ubicacion, fecha_ingreso, fecha_vencimiento, agotado, stock_minimo)
        self.es_alcoholica= es_alcoholica

    def mostrar_info(self)-> str:
        info_base= super().mostrar_info()
        info_nueva= f"\nAlcohólica: {'Sí' if self.es_alcoholica else 'No'}"
        return info_base + info_nueva
    
class Empaque(Producto):
    def __init__(self, codigo, nombre, precio, cantidad, unidad_medid, familia, ubicacion, fecha_ingreso, fecha_vencimiento, agotado, stock_minimo, material:str):
        super().__init__(codigo, nombre, precio, cantidad, unidad_medid, familia, ubicacion, fecha_ingreso, fecha_vencimiento, agotado, stock_minimo)
        self.material= material

    def mostrar_info(self)-> str:
        info_base= super().mostrar_info()
        info_nueva= f"\nMaterial: {self.material}"
        return info_base + info_nueva

class Utencilio(Producto):
    def __init__(self, codigo, nombre, precio, cantidad, unidad_medid, familia, ubicacion, fecha_ingreso, fecha_vencimiento, agotado, stock_minimo, tipo:str):
        super().__init__(codigo, nombre, precio, cantidad, unidad_medid, familia, ubicacion, fecha_ingreso, fecha_vencimiento, agotado, stock_minimo)
        self.tipo= tipo

    def mostrar_info(self)-> str:
        info_base= super().mostrar_info()
        info_nueva= f"\nTipo: {self.tipo}"
        return info_base + info_nueva
       
class Aperitivos(Producto):
    def __init__(self, codigo, nombre, precio, cantidad, unidad_medid, familia, ubicacion, fecha_ingreso, fecha_vencimiento, agotado, stock_minimo, tipo:str):
        super().__init__(codigo, nombre, precio, cantidad, unidad_medid, familia, ubicacion, fecha_ingreso, fecha_vencimiento, agotado, stock_minimo)
        self.tipo= tipo

    def mostrar_info(self)-> str:
        info_base= super().mostrar_info()
        info_nueva= f"\nTipo: {self.tipo}"
        return info_base + info_nueva

class Postres(Producto):
    def __init__(self, codigo, nombre, precio, cantidad, unidad_medid, familia, ubicacion, fecha_ingreso, fecha_vencimiento, agotado, stock_minimo, tipo_postre:str):
        super().__init__(codigo, nombre, precio, cantidad, unidad_medid, familia, ubicacion, fecha_ingreso, fecha_vencimiento, agotado, stock_minimo)
        self.tipo_postre= tipo_postre

    def mostrar_info(self)-> str:
        info_base= super().mostrar_info()
        info_nueva= f"\Postre: {self.tipo_postre}"
        return info_base + info_nueva
 
class Productoslimpieza(Producto):
    def __init__(self, codigo, nombre, precio, cantidad, unidad_medid, familia, ubicacion, fecha_ingreso, fecha_vencimiento, agotado, stock_minimo, uso:str):
        super().__init__(codigo, nombre, precio, cantidad, unidad_medid, familia, ubicacion, fecha_ingreso, fecha_vencimiento, agotado, stock_minimo)
        self.uso= uso

    def mostrar_info(self)-> str:
        info_base= super().mostrar_info()
        info_nueva= f"\n Tipo de uso: {self.uso}"
        return info_base + info_nueva

class Productofinal(Producto):
    def __init__(self, codigo, nombre, precio, cantidad, unidad_medid, familia, ubicacion, fecha_ingreso, fecha_vencimiento, agotado, stock_minimo, receta: list[Ingrediente]):
        super().__init__(codigo, nombre, precio, cantidad, unidad_medid, familia, ubicacion, fecha_ingreso, fecha_vencimiento, agotado, stock_minimo)
        self.receta= receta 
        pass 

class Movimiento:
    def __init__(self, tipo: str, producto: Producto, cantidad:int, fecha, usuario:str, motivo:str):
        pass
    def mostrar_detalle(self)-> str:
        pass 
class Inventario:                               #def inventario en sqlite
    def __init__(self):
        self.productos:list[Producto]=[]
        self.movimientos:list[Movimiento]= []

    def database(self):                                 #def inventario en sqlite
        self.conn = sqlite3.connect('BOD.db')
        self.cursor = self.conn.cursor()

        self.cursor.execute(
            """CREATE TABLE IF NOT EXISTS BOD(
            codigo INTEGER,
            name TEXT,
            precio INTEGER,
            cantidad INTEGER,
            medida TEXT,
            fechaingreso TEXT
            )"""
        )
        self.conn.commit()
        
        datos_ejemplo = [
                ('1234', 'Carne de Hmaburguesa', 5000, 250, 'kg', '2025-06-20'),
                ('2234', 'Salchicha', 4000, 150, 'Unidad', '2025-12-15'),
                ('2224', 'Soda', 200, 2000, 'L', '2025-06-18'),
                ('2222', 'Pan', 200, 2000, 'Unidad', '2025-06-22'),
                ('1233', 'Salsa', 200, 1200, 'Unidad', '2026-01-15')
            ]
            
        self.cursor.executemany('''
            INSERT INTO BOD (codigo, name, precio, cantidad, medida, fechaingreso)
            VALUES (?, ?, ?, ?, ?, ?)
            ''', datos_ejemplo)
        self.conn.commit()
        

    def agregar_producto(self, codigo, nombre, precio, cantidad, medida, fecha):
        """Método para agregar un producto a la base de datos"""
        try:
            if not self.conn:
                self.database()
            
            # Verificar si el producto ya existe
            self.cursor.execute("SELECT codigo FROM BOD WHERE codigo = ?", (codigo,))
            if self.cursor.fetchone():
                return False  # El producto ya existe
            
            # Insertar el nuevo producto
            self.cursor.execute('''
                INSERT INTO BOD (codigo, name, precio, cantidad, medida, fechaingreso)
                VALUES (?, ?, ?, ?, ?, ?)
                ''', (codigo, nombre, precio, cantidad, medida, fecha))
            
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error de base de datos: {e}")
            return False
        except Exception as e:
            print(f"Error: {e}")
            return False
        
        

class Interfaz:                                                    #INTERFAZZZZZZZZZZZZZZZZZZZZZZZZZZZ
    def __init__(self):
        self.inventario = Inventario()
        self.inventario.database() 

        self.root = tkinter.Tk()
        self.root.title("PYTHUNAL")
        self.root.geometry("500x500")
        
        self.crear_interfaz()
    
    def crear_interfaz(self):
        titulo = tkinter.Label(self.root, text="Añadir producto al inventario", 
                         font=("times new roman", 18, "bold"))
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
    def productos_porv_vencer(self) -> list[Producto]:
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


app = Interfaz()
app.ejecutar()
i = Inventario()
i.database()
