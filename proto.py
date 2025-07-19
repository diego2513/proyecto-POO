import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import sqlite3
from datetime import datetime, timedelta
import os

class RestaurantInventorySystem:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Inventario - Restaurante")
        self.root.geometry("1200x800")
        self.root.configure(bg='#f0f0f0')
        
        # Inicializar base de datos
        self.init_database()
        
        # Crear interfaz
        self.create_widgets()
        
        # Cargar datos
        self.load_inventory()
        
    def init_database(self):
        """Inicializar base de datos SQLite"""
        self.conn = sqlite3.connect('inventario_restaurante.db')
        self.cursor = self.conn.cursor()
        
        # Crear tabla si no existe
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS inventario (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                categoria TEXT NOT NULL,
                cantidad REAL NOT NULL,
                unidad TEXT NOT NULL,
                precio_unitario REAL NOT NULL,
                stock_minimo REAL NOT NULL,
                fecha_vencimiento TEXT,
                proveedor TEXT,
                fecha_actualizacion TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Insertar datos de ejemplo si la tabla está vacía
        self.cursor.execute('SELECT COUNT(*) FROM inventario')
        if self.cursor.fetchone()[0] == 0:
            datos_ejemplo = [
                ('Pollo', 'Carnes', 25.0, 'kg', 12000, 10.0, '2025-06-20', 'Avícola Central'),
                ('Arroz', 'Granos', 50.0, 'kg', 3500, 20.0, '2025-12-15', 'Distribuidora La Cosecha'),
                ('Tomate', 'Verduras', 8.0, 'kg', 4000, 15.0, '2025-06-18', 'Finca Verde'),
                ('Leche', 'Lácteos', 20.0, 'L', 2800, 10.0, '2025-06-22', 'Lácteos del Valle'),
                ('Aceite', 'Condimentos', 12.0, 'L', 8500, 5.0, '2026-01-15', 'Aceites Premium')
            ]
            
            self.cursor.executemany('''
                INSERT INTO inventario (nombre, categoria, cantidad, unidad, precio_unitario, 
                                      stock_minimo, fecha_vencimiento, proveedor)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', datos_ejemplo)
            
        self.conn.commit()
        
    def create_widgets(self):
        """Crear interfaz gráfica"""
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configurar grid
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # Título
        title_label = ttk.Label(main_frame, text="Sistema de Inventario - Restaurante", 
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Frame de estadísticas
        stats_frame = ttk.LabelFrame(main_frame, text="Estadísticas", padding="10")
        stats_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.stats_labels = {}
        stats_items = ['Total Items', 'Stock Bajo', 'Por Vencer', 'Valor Total']
        for i, item in enumerate(stats_items):
            ttk.Label(stats_frame, text=f"{item}:", font=('Arial', 10, 'bold')).grid(row=0, column=i*2, padx=(0, 5))
            self.stats_labels[item] = ttk.Label(stats_frame, text="0", foreground='blue')
            self.stats_labels[item].grid(row=0, column=i*2+1, padx=(0, 20))
        
        # Frame de controles
        controls_frame = ttk.Frame(main_frame)
        controls_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        controls_frame.columnconfigure(1, weight=1)
        controls_frame.rowconfigure(1, weight=1)
        
        # Botones de acción
        buttons_frame = ttk.Frame(controls_frame)
        buttons_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Button(buttons_frame, text="Agregar Producto", 
                  command=self.add_product).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(buttons_frame, text="Editar Producto", 
                  command=self.edit_product).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(buttons_frame, text="Eliminar Producto", 
                  command=self.delete_product).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(buttons_frame, text="Actualizar Stock", 
                  command=self.update_stock).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(buttons_frame, text="Ver Alertas", 
                  command=self.show_alerts).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(buttons_frame, text="Reporte", 
                  command=self.generate_report).pack(side=tk.LEFT, padx=(0, 5))
        
        # Frame de búsqueda
        search_frame = ttk.Frame(controls_frame)
        search_frame.grid(row=0, column=2, sticky=(tk.E), pady=(0, 10))
        
        ttk.Label(search_frame, text="Buscar:").pack(side=tk.LEFT, padx=(0, 5))
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.filter_items)
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=20)
        search_entry.pack(side=tk.LEFT)
        
        # Tabla de inventario
        tree_frame = ttk.Frame(controls_frame)
        tree_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S))
        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)
        
        # Crear Treeview con scrollbars
        self.tree = ttk.Treeview(tree_frame, columns=('ID', 'Nombre', 'Categoría', 'Cantidad', 
                                                     'Unidad', 'Precio Unit.', 'Stock Mín.', 
                                                     'Vencimiento', 'Proveedor', 'Estado'), 
                                show='headings', height=15)
        
        # Configurar columnas
        columns_config = {
            'ID': 50,
            'Nombre': 150,
            'Categoría': 100,
            'Cantidad': 80,
            'Unidad': 70,
            'Precio Unit.': 100,
            'Stock Mín.': 80,
            'Vencimiento': 100,
            'Proveedor': 150,
            'Estado': 100
        }
        
        for col, width in columns_config.items():
            self.tree.heading(col, text=col)
            self.tree.column(col, width=width, anchor=tk.CENTER if col in ['Cantidad', 'Precio Unit.', 'Stock Mín.'] else tk.W)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Grid scrollbars y tree
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        v_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        h_scrollbar.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
    def load_inventory(self):
        """Cargar inventario desde la base de datos"""
        # Limpiar tabla
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Obtener datos
        self.cursor.execute('''
            SELECT id, nombre, categoria, cantidad, unidad, precio_unitario, 
                   stock_minimo, fecha_vencimiento, proveedor
            FROM inventario ORDER BY nombre
        ''')
        
        items = self.cursor.fetchall()
        
        for item in items:
            estado = self.get_stock_status(item[3], item[6])  # cantidad, stock_minimo
            
            # Formatear precio
            precio_fmt = f"${item[5]:,.0f}"
            
            # Insertar en tabla
            item_id = self.tree.insert('', tk.END, values=(
                item[0], item[1], item[2], item[3], item[4], 
                precio_fmt, item[6], item[7], item[8], estado
            ))
            
            # Colorear según estado
            if estado == 'CRÍTICO':
                self.tree.item(item_id, tags=('critical',))
            elif estado == 'BAJO':
                self.tree.item(item_id, tags=('warning',))
        
        # Configurar colores
        self.tree.tag_configure('critical', background='#ffcccc')
        self.tree.tag_configure('warning', background='#fff3cd')
        
        # Actualizar estadísticas
        self.update_stats()
        
    def get_stock_status(self, cantidad, stock_minimo):
        """Determinar estado del stock"""
        if cantidad <= stock_minimo:
            return 'CRÍTICO'
        elif cantidad <= stock_minimo * 1.5:
            return 'BAJO'
        else:
            return 'NORMAL'
    
    def update_stats(self):
        """Actualizar estadísticas"""
        self.cursor.execute('SELECT COUNT(*) FROM inventario')
        total_items = self.cursor.fetchone()[0]
        
        self.cursor.execute('SELECT COUNT(*) FROM inventario WHERE cantidad <= stock_minimo')
        stock_bajo = self.cursor.fetchone()[0]
        
        # Items por vencer (próximos 7 días)
        fecha_limite = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')
        self.cursor.execute('SELECT COUNT(*) FROM inventario WHERE fecha_vencimiento <= ?', (fecha_limite,))
        por_vencer = self.cursor.fetchone()[0]
        
        # Valor total
        self.cursor.execute('SELECT SUM(cantidad * precio_unitario) FROM inventario')
        valor_total = self.cursor.fetchone()[0] or 0
        
        # Actualizar labels
        self.stats_labels['Total Items'].config(text=str(total_items))
        self.stats_labels['Stock Bajo'].config(text=str(stock_bajo), 
                                             foreground='red' if stock_bajo > 0 else 'blue')
        self.stats_labels['Por Vencer'].config(text=str(por_vencer), 
                                             foreground='orange' if por_vencer > 0 else 'blue')
        self.stats_labels['Valor Total'].config(text=f"${valor_total:,.0f}", foreground='green')
    
    def filter_items(self, *args):
        """Filtrar items según búsqueda"""
        search_term = self.search_var.get().lower()
        
        # Limpiar tabla
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Buscar en base de datos
        query = '''
            SELECT id, nombre, categoria, cantidad, unidad, precio_unitario, 
                   stock_minimo, fecha_vencimiento, proveedor
            FROM inventario 
            WHERE LOWER(nombre) LIKE ? OR LOWER(categoria) LIKE ? OR LOWER(proveedor) LIKE ?
            ORDER BY nombre
        '''
        
        self.cursor.execute(query, (f'%{search_term}%', f'%{search_term}%', f'%{search_term}%'))
        items = self.cursor.fetchall()
        
        for item in items:
            estado = self.get_stock_status(item[3], item[6])
            precio_fmt = f"${item[5]:,.0f}"
            
            item_id = self.tree.insert('', tk.END, values=(
                item[0], item[1], item[2], item[3], item[4], 
                precio_fmt, item[6], item[7], item[8], estado
            ))
            
            if estado == 'CRÍTICO':
                self.tree.item(item_id, tags=('critical',))
            elif estado == 'BAJO':
                self.tree.item(item_id, tags=('warning',))
    
    def add_product(self):
        """Agregar nuevo producto"""
        self.product_dialog()
    
    def edit_product(self):
        """Editar producto seleccionado"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "Selecciona un producto para editar")
            return
        
        item = self.tree.item(selection[0])
        product_id = item['values'][0]
        
        # Obtener datos completos del producto
        self.cursor.execute('SELECT * FROM inventario WHERE id = ?', (product_id,))
        product_data = self.cursor.fetchone()
        
        self.product_dialog(product_data)
    
    def delete_product(self):
        """Eliminar producto seleccionado"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "Selecciona un producto para eliminar")
            return
        
        item = self.tree.item(selection[0])
        product_id = item['values'][0]
        product_name = item['values'][1]
        
        if messagebox.askyesno("Confirmar", f"¿Eliminar el producto '{product_name}'?"):
            self.cursor.execute('DELETE FROM inventario WHERE id = ?', (product_id,))
            self.conn.commit()
            self.load_inventory()
            messagebox.showinfo("Éxito", "Producto eliminado correctamente")
    
    def update_stock(self):
        """Actualizar stock de producto seleccionado"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "Selecciona un producto para actualizar stock")
            return
        
        item = self.tree.item(selection[0])
        product_id = item['values'][0]
        product_name = item['values'][1]
        current_stock = item['values'][3]
        
        new_stock = simpledialog.askfloat("Actualizar Stock", 
                                         f"Stock actual de '{product_name}': {current_stock}\n"
                                         f"Ingresa la nueva cantidad:")
        
        if new_stock is not None:
            self.cursor.execute('UPDATE inventario SET cantidad = ? WHERE id = ?', 
                              (new_stock, product_id))
            self.conn.commit()
            self.load_inventory()
            messagebox.showinfo("Éxito", "Stock actualizado correctamente")
    
    def product_dialog(self, product_data=None):
        """Diálogo para agregar/editar producto"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Agregar Producto" if product_data is None else "Editar Producto")
        dialog.geometry("400x500")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Variables
        vars_dict = {
            'nombre': tk.StringVar(),
            'categoria': tk.StringVar(),
            'cantidad': tk.DoubleVar(),
            'unidad': tk.StringVar(),
            'precio_unitario': tk.DoubleVar(),
            'stock_minimo': tk.DoubleVar(),
            'fecha_vencimiento': tk.StringVar(),
            'proveedor': tk.StringVar()
        }
        
        # Si es edición, llenar con datos existentes
        if product_data:
            vars_dict['nombre'].set(product_data[1])
            vars_dict['categoria'].set(product_data[2])
            vars_dict['cantidad'].set(product_data[3])
            vars_dict['unidad'].set(product_data[4])
            vars_dict['precio_unitario'].set(product_data[5])
            vars_dict['stock_minimo'].set(product_data[6])
            vars_dict['fecha_vencimiento'].set(product_data[7])
            vars_dict['proveedor'].set(product_data[8])
        
        # Crear campos
        main_frame = ttk.Frame(dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        fields = [
            ('Nombre:', 'nombre', ttk.Entry),
            ('Categoría:', 'categoria', lambda parent, **kwargs: ttk.Combobox(parent, values=['Carnes', 'Verduras', 'Granos', 'Lácteos', 'Bebidas', 'Condimentos', 'Otros'], **kwargs)),
            ('Cantidad:', 'cantidad', ttk.Entry),
            ('Unidad:', 'unidad', lambda parent, **kwargs: ttk.Combobox(parent, values=['kg', 'g', 'L', 'ml', 'unidades', 'cajas'], **kwargs)),
            ('Precio Unitario:', 'precio_unitario', ttk.Entry),
            ('Stock Mínimo:', 'stock_minimo', ttk.Entry),
            ('Fecha Vencimiento (YYYY-MM-DD):', 'fecha_vencimiento', ttk.Entry),
            ('Proveedor:', 'proveedor', ttk.Entry)
        ]
        
        widgets = {}
        for i, (label, var_name, widget_class) in enumerate(fields):
            ttk.Label(main_frame, text=label).grid(row=i, column=0, sticky=tk.W, pady=5)
            
            widget = widget_class(main_frame, textvariable=vars_dict[var_name], width=30)
            widget.grid(row=i, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
            widgets[var_name] = widget
        
        # Botones
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=len(fields), column=0, columnspan=2, pady=20)
        
        def save_product():
            try:
                # Validar campos obligatorios
                if not vars_dict['nombre'].get() or not vars_dict['categoria'].get():
                    messagebox.showerror("Error", "Nombre y categoría son obligatorios")
                    return
                
                values = [
                    vars_dict['nombre'].get(),
                    vars_dict['categoria'].get(),
                    vars_dict['cantidad'].get(),
                    vars_dict['unidad'].get(),
                    vars_dict['precio_unitario'].get(),
                    vars_dict['stock_minimo'].get(),
                    vars_dict['fecha_vencimiento'].get(),
                    vars_dict['proveedor'].get()
                ]
                
                if product_data is None:  # Agregar
                    self.cursor.execute('''
                        INSERT INTO inventario (nombre, categoria, cantidad, unidad, precio_unitario, 
                                              stock_minimo, fecha_vencimiento, proveedor)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ''', values)
                    message = "Producto agregado correctamente"
                else:  # Editar
                    self.cursor.execute('''
                        UPDATE inventario SET nombre=?, categoria=?, cantidad=?, unidad=?, 
                                            precio_unitario=?, stock_minimo=?, fecha_vencimiento=?, proveedor=?
                        WHERE id=?
                    ''', values + [product_data[0]])
                    message = "Producto actualizado correctamente"
                
                self.conn.commit()
                self.load_inventory()
                dialog.destroy()
                messagebox.showinfo("Éxito", message)
                
            except Exception as e:
                messagebox.showerror("Error", f"Error al guardar: {str(e)}")
        
        ttk.Button(button_frame, text="Guardar", command=save_product).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancelar", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
        
        # Configurar grid
        main_frame.columnconfigure(1, weight=1)
    
    def show_alerts(self):
        """Mostrar ventana de alertas"""
        alert_window = tk.Toplevel(self.root)
        alert_window.title("Alertas de Inventario")
        alert_window.geometry("800x600")
        alert_window.transient(self.root)
        
        notebook = ttk.Notebook(alert_window)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Tab 1: Stock bajo
        stock_frame = ttk.Frame(notebook)
        notebook.add(stock_frame, text="Stock Bajo")
        
        ttk.Label(stock_frame, text="Productos con stock bajo:", font=('Arial', 12, 'bold')).pack(pady=10)
        
        stock_tree = ttk.Treeview(stock_frame, columns=('Nombre', 'Cantidad', 'Stock Mín.', 'Diferencia'), 
                                 show='headings', height=10)
        
        for col in ['Nombre', 'Cantidad', 'Stock Mín.', 'Diferencia']:
            stock_tree.heading(col, text=col)
            stock_tree.column(col, width=150, anchor=tk.CENTER)
        
        stock_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Cargar productos con stock bajo
        self.cursor.execute('''
            SELECT nombre, cantidad, stock_minimo 
            FROM inventario 
            WHERE cantidad <= stock_minimo
            ORDER BY (cantidad - stock_minimo)
        ''')
        
        for item in self.cursor.fetchall():
            diferencia = item[1] - item[2]
            stock_tree.insert('', tk.END, values=(item[0], item[1], item[2], f"{diferencia:.1f}"))
        
        # Tab 2: Próximos a vencer
        expiry_frame = ttk.Frame(notebook)
        notebook.add(expiry_frame, text="Próximos a Vencer")
        
        ttk.Label(expiry_frame, text="Productos que vencen en los próximos 7 días:", 
                 font=('Arial', 12, 'bold')).pack(pady=10)
        
        expiry_tree = ttk.Treeview(expiry_frame, columns=('Nombre', 'Cantidad', 'Vencimiento', 'Días'), 
                                  show='headings', height=10)
        
        for col in ['Nombre', 'Cantidad', 'Vencimiento', 'Días']:
            expiry_tree.heading(col, text=col)
            expiry_tree.column(col, width=150, anchor=tk.CENTER)
        
        expiry_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Cargar productos próximos a vencer
        fecha_limite = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')
        self.cursor.execute('''
            SELECT nombre, cantidad, fecha_vencimiento 
            FROM inventario 
            WHERE fecha_vencimiento <= ?
            ORDER BY fecha_vencimiento
        ''', (fecha_limite,))
        
        for item in self.cursor.fetchall():
            try:
                fecha_venc = datetime.strptime(item[2], '%Y-%m-%d')
                dias_restantes = (fecha_venc - datetime.now()).days
                expiry_tree.insert('', tk.END, values=(item[0], item[1], item[2], dias_restantes))
            except:
                expiry_tree.insert('', tk.END, values=(item[0], item[1], item[2], "N/A"))
    
    def generate_report(self):
        """Generar reporte de inventario"""
        report_window = tk.Toplevel(self.root)
        report_window.title("Reporte de Inventario")
        report_window.geometry("600x700")
        report_window.transient(self.root)
        
        # Crear widget de texto con scroll
        text_frame = ttk.Frame(report_window)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        text_widget = tk.Text(text_frame, wrap=tk.WORD, font=('Courier', 10))
        scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)
        
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Generar contenido del reporte
        report_content = self.generate_report_content()
        text_widget.insert(tk.END, report_content)
        text_widget.config(state=tk.DISABLED)
        
        # Botón para guardar reporte
        ttk.Button(report_window, text="Guardar Reporte", 
                  command=lambda: self.save_report(report_content)).pack(pady=10)
    
    def generate_report_content(self):
        """Generar contenido del reporte"""
        report = []
        report.append("="*60)
        report.append("REPORTE DE INVENTARIO - RESTAURANTE")
        report.append(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("="*60)
        report.append("")
        
        # Estadísticas generales
        self.cursor.execute('SELECT COUNT(*) FROM inventario')
        total_items = self.cursor.fetchone()[0]
        
        self.cursor.execute('SELECT SUM(cantidad * precio_unitario) FROM inventario')
        valor_total = self.cursor.fetchone()[0] or 0
        
        self.cursor.execute('SELECT COUNT(*) FROM inventario WHERE cantidad <= stock_minimo')
        stock_bajo = self.cursor.fetchone()[0]
        
        report.append("RESUMEN EJECUTIVO:")
        report.append(f"• Total de productos: {total_items}")
        report.append(f"• Valor total del inventario: ${valor_total:,.0f}")
        report.append(f"• Productos con stock bajo: {stock_bajo}")
        report.append("")
        
        # Inventario por categoría
        report.append("INVENTARIO POR CATEGORÍA:")
        report.append("-" * 40)
        
        self.cursor.execute('''
            SELECT categoria, COUNT(*), SUM(cantidad * precio_unitario)
            FROM inventario 
            GROUP BY categoria 
            ORDER BY categoria
        ''')
        
        for cat, count, value in self.cursor.fetchall():
            report.append(f"{cat:15} | {count:3} items | ${value:>10,.0f}")
        
        report.append("")
        
        # Productos con stock crítico
        report.append("PRODUCTOS CON STOCK CRÍTICO:")
        report.append("-" * 50)
        
        self.cursor.execute('''
            SELECT nombre, cantidad, stock_minimo, unidad
            FROM inventario 
            WHERE cantidad <= stock_minimo
            ORDER BY (cantidad - stock_minimo)
        ''')
        
        critical_items = self.cursor.fetchall()
        if critical_items:
            for nombre, cantidad, stock_min, unidad in critical_items:
                report.append(f"• {nombre}: {cantidad} {unidad} (mín: {stock_min} {unidad})")
        else:
            report.append("• No hay productos con stock crítico")
        
        report.append("")
        
        # Inventario completo
        report.append("INVENTARIO COMPLETO:")
        report.append("-" * 80)
        report.append(f"{'Producto':<20} {'Cat.':<12} {'Cant.':<8} {'Unidad':<8} {'Precio':<12} {'Total':<12}")
        report.append("-" * 80)
        
        self.cursor.execute('''
            SELECT nombre, categoria, cantidad, unidad, precio_unitario
            FROM inventario 
            ORDER BY categoria, nombre
        ''')
        
        for nombre, categoria, cantidad, unidad, precio in self.cursor.fetchall():
            total_item = cantidad * precio
            report.append(f"{nombre[:19]:<20} {categoria[:11]:<12} {cantidad:<8.1f} {unidad:<8} ${precio:<11,.0f} ${total_item:<11,.0f}")
        
        return "\n".join(report)
    
    def save_report(self, content):
        """Guardar reporte en archivo"""
        try:
            filename = f"reporte_inventario_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(content)
            messagebox.showinfo("Éxito", f"Reporte guardado como: {filename}")
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar el reporte: {str(e)}")
    
    def __del__(self):
        """Cerrar conexión a la base de datos"""
        if hasattr(self, 'conn'):
            self.conn.close()

class InventoryAPI:
    """Clase para operaciones programáticas del inventario"""
    
    def __init__(self, db_path='inventario_restaurante.db'):
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
    
    def agregar_producto(self, nombre, categoria, cantidad, unidad, precio_unitario, 
                        stock_minimo, fecha_vencimiento=None, proveedor=None):
        """Agregar producto al inventario"""
        try:
            self.cursor.execute('''
                INSERT INTO inventario (nombre, categoria, cantidad, unidad, precio_unitario, 
                                      stock_minimo, fecha_vencimiento, proveedor)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (nombre, categoria, cantidad, unidad, precio_unitario, 
                  stock_minimo, fecha_vencimiento, proveedor))
            self.conn.commit()
            return True, "Producto agregado exitosamente"
        except Exception as e:
            return False, str(e)
    
    def actualizar_stock(self, nombre, nueva_cantidad):
        """Actualizar stock de un producto"""
        try:
            self.cursor.execute('''
                UPDATE inventario SET cantidad = ? WHERE nombre = ?
            ''', (nueva_cantidad, nombre))
            
            if self.cursor.rowcount > 0:
                self.conn.commit()
                return True, f"Stock de {nombre} actualizado a {nueva_cantidad}"
            else:
                return False, f"Producto {nombre} no encontrado"
        except Exception as e:
            return False, str(e)
    
    def reducir_stock(self, nombre, cantidad_usar):
        """Reducir stock cuando se usa un producto"""
        try:
            # Obtener stock actual
            self.cursor.execute('SELECT cantidad FROM inventario WHERE nombre = ?', (nombre,))
            result = self.cursor.fetchone()
            
            if not result:
                return False, f"Producto {nombre} no encontrado"
            
            stock_actual = result[0]
            
            if stock_actual < cantidad_usar:
                return False, f"Stock insuficiente. Disponible: {stock_actual}, Solicitado: {cantidad_usar}"
            
            nuevo_stock = stock_actual - cantidad_usar
            self.cursor.execute('UPDATE inventario SET cantidad = ? WHERE nombre = ?', 
                              (nuevo_stock, nombre))
            self.conn.commit()
            
            return True, f"Stock reducido. Nuevo stock de {nombre}: {nuevo_stock}"
            
        except Exception as e:
            return False, str(e)
    
    def obtener_producto(self, nombre):
        """Obtener información de un producto"""
        try:
            self.cursor.execute('''
                SELECT * FROM inventario WHERE nombre = ?
            ''', (nombre,))
            
            result = self.cursor.fetchone()
            if result:
                columns = ['id', 'nombre', 'categoria', 'cantidad', 'unidad', 
                          'precio_unitario', 'stock_minimo', 'fecha_vencimiento', 
                          'proveedor', 'fecha_actualizacion']
                return True, dict(zip(columns, result))
            else:
                return False, f"Producto {nombre} no encontrado"
                
        except Exception as e:
            return False, str(e)
    
    def listar_productos_bajo_stock(self):
        """Obtener productos con stock bajo"""
        try:
            self.cursor.execute('''
                SELECT nombre, cantidad, stock_minimo, unidad
                FROM inventario 
                WHERE cantidad <= stock_minimo
                ORDER BY (cantidad - stock_minimo)
            ''')
            
            productos = []
            for row in self.cursor.fetchall():
                productos.append({
                    'nombre': row[0],
                    'cantidad': row[1],
                    'stock_minimo': row[2],
                    'unidad': row[3],
                    'diferencia': row[1] - row[2]
                })
            
            return True, productos
            
        except Exception as e:
            return False, str(e)
    
    def valor_total_inventario(self):
        """Calcular valor total del inventario"""
        try:
            self.cursor.execute('SELECT SUM(cantidad * precio_unitario) FROM inventario')
            valor = self.cursor.fetchone()[0] or 0
            return True, valor
        except Exception as e:
            return False, str(e)
    
    def close(self):
        """Cerrar conexión"""
        self.conn.close()

# Funciones de utilidad para integración con otros sistemas
def crear_receta(nombre_receta, ingredientes_dict):
    """
    Crear una receta y verificar disponibilidad de ingredientes
    
    Args:
        nombre_receta (str): Nombre de la receta
        ingredientes_dict (dict): {'ingrediente': cantidad_necesaria}
    
    Returns:
        tuple: (bool, str, dict) - (éxito, mensaje, ingredientes_faltantes)
    """
    api = InventoryAPI()
    ingredientes_faltantes = {}
    
    try:
        for ingrediente, cantidad_necesaria in ingredientes_dict.items():
            success, producto = api.obtener_producto(ingrediente)
            
            if not success:
                ingredientes_faltantes[ingrediente] = f"Producto no encontrado"
                continue
            
            if producto['cantidad'] < cantidad_necesaria:
                ingredientes_faltantes[ingrediente] = {
                    'disponible': producto['cantidad'],
                    'necesario': cantidad_necesaria,
                    'faltante': cantidad_necesaria - producto['cantidad']
                }
        
        if ingredientes_faltantes:
            return False, f"Ingredientes insuficientes para {nombre_receta}", ingredientes_faltantes
        else:
            return True, f"Todos los ingredientes disponibles para {nombre_receta}", {}
            
    except Exception as e:
        return False, str(e), {}
    finally:
        api.close()

def procesar_venta(items_vendidos):
    """
    Procesar una venta reduciendo el stock correspondiente
    
    Args:
        items_vendidos (dict): {'producto': cantidad_vendida}
    
    Returns:
        tuple: (bool, str, list) - (éxito, mensaje, errores)
    """
    api = InventoryAPI()
    errores = []
    
    try:
        for producto, cantidad in items_vendidos.items():
            success, mensaje = api.reducir_stock(producto, cantidad)
            if not success:
                errores.append(f"{producto}: {mensaje}")
        
        if errores:
            return False, "Errores en el procesamiento de la venta", errores
        else:
            return True, "Venta procesada correctamente", []
            
    except Exception as e:
        return False, str(e), []
    finally:
        api.close()

def generar_lista_compras(dias_cobertura=7):
    """
    Generar lista de compras basada en stock mínimo y días de cobertura
    
    Args:
        dias_cobertura (int): Días de cobertura deseados
    
    Returns:
        tuple: (bool, str, list) - (éxito, mensaje, lista_compras)
    """
    api = InventoryAPI()
    lista_compras = []
    
    try:
        success, productos_bajo_stock = api.listar_productos_bajo_stock()
        
        if not success:
            return False, productos_bajo_stock, []
        
        for producto in productos_bajo_stock:
            cantidad_comprar = (producto['stock_minimo'] * 2) - producto['cantidad']
            if cantidad_comprar > 0:
                lista_compras.append({
                    'producto': producto['nombre'],
                    'cantidad_actual': producto['cantidad'],
                    'cantidad_comprar': cantidad_comprar,
                    'unidad': producto['unidad']
                })
        
        return True, f"Lista de compras generada con {len(lista_compras)} productos", lista_compras
        
    except Exception as e:
        return False, str(e), []
    finally:
        api.close()

# Ejemplo de uso del sistema
if __name__ == "__main__":
    # Crear la aplicación GUI
    root = tk.Tk()
    app = RestaurantInventorySystem(root)
    
    # Ejemplo de uso de la API programática
    print("=== Ejemplo de uso de la API ===")
    
    # Crear instancia de la API
    api = InventoryAPI()
    
    # Verificar un producto
    success, producto = api.obtener_producto("Pollo")
    if success:
        print(f"Producto encontrado: {producto['nombre']} - Stock: {producto['cantidad']} {producto['unidad']}")
    
    # Simular uso de ingredientes para una receta
    receta_pollo_arroz = {
        "Pollo": 2.0,
        "Arroz": 1.5,
        "Aceite": 0.1
    }
    
    success, mensaje, faltantes = crear_receta("Pollo con Arroz", receta_pollo_arroz)
    print(f"Receta: {mensaje}")
    if faltantes:
        print("Ingredientes faltantes:", faltantes)
    
    # Generar lista de compras
    success, mensaje, lista = generar_lista_compras()
    print(f"Lista de compras: {mensaje}")
    for item in lista:
        print(f"- {item['producto']}: comprar {item['cantidad_comprar']} {item['unidad']}")
    
    # Cerrar API
    api.close()
    
    # Iniciar la interfaz gráfica
    root.mainloop()