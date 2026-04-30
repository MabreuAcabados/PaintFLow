#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
AnalistaPF - Sistema Integral de Administración de Fórmulas y Datos de Pintura
Módulos: Empleados, Fórmulas Normales, Fórmulas CCE, Colores
Funcionalidades: Consulta, Agregar, Editar, Inhabilitar
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, simpledialog
from PIL import Image, ImageTk
import psycopg2
from psycopg2 import sql
import psycopg2.extras
import sys
from datetime import datetime
import os

def obtener_ruta_absoluta(rel_path):
    """Obtiene ruta absoluta compatible con PyInstaller"""
    try:
        if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
            return os.path.join(sys._MEIPASS, rel_path)
        base_path = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(base_path, rel_path)
    except Exception:
        return rel_path

class AnalistaPF:
    """Sistema principal de administración de fórmulas de pintura"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Gestión de Tiendas")
        self.root.geometry("1400x900")
        
        # Cargar icono
        try:
            icono_path = obtener_ruta_absoluta("icono.ico")
            if os.path.exists(icono_path):
                self.root.iconbitmap(icono_path)
        except Exception as e:
            pass  # Si no existe el icono, continuar sin él
        
        self.conn = None
        self.cursor = None
        self.selected_item = None
        self.empleados_id_map = {}
        self.sucursales = []
        self.logo_image = None
        self.usuario_actual = None
        self.sucursal_actual = None
        
        self.setup_styles()
        self.create_main_interface()
        self.connect_database()
    
    def setup_styles(self):
        """Configurar estilos profesionales de la interfaz"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Colores profesionales
        colors = {
            'primary': '#2C3E50',      # Azul oscuro
            'secondary': '#3498DB',    # Azul claro
            'success': '#27AE60',      # Verde
            'warning': '#F39C12',      # Naranja
            'danger': '#E74C3C',       # Rojo
            'light_bg': '#ECF0F1',     # Gris claro
            'white': '#FFFFFF',
            'text': '#2C3E50'
        }
        
        # Frame styles
        style.configure('TFrame', background=colors['light_bg'])
        style.configure('Header.TFrame', background=colors['primary'], relief=tk.FLAT)
        style.configure('Card.TFrame', background=colors['white'], relief=tk.RIDGE, borderwidth=1)
        
        # Label styles
        style.configure('TLabel', background=colors['light_bg'], foreground=colors['text'], font=('Segoe UI', 9))
        style.configure('Header.TLabel', background=colors['primary'], foreground=colors['white'], font=('Segoe UI', 10, 'bold'))
        style.configure('Title.TLabel', background=colors['white'], foreground=colors['primary'], font=('Segoe UI', 12, 'bold'))
        style.configure('Subtitle.TLabel', background=colors['light_bg'], foreground=colors['secondary'], font=('Segoe UI', 10, 'bold'))
        
        # LabelFrame styles
        style.configure('TLabelframe', background=colors['light_bg'], foreground=colors['primary'], font=('Segoe UI', 9, 'bold'))
        style.configure('TLabelframe.Label', background=colors['light_bg'], foreground=colors['primary'], font=('Segoe UI', 9, 'bold'))
        
        # Button styles
        style.configure('TButton', font=('Segoe UI', 9), padding=6)
        style.map('TButton', foreground=[('pressed', colors['white']), ('active', colors['white'])])
        
        style.configure('Primary.TButton', font=('Segoe UI', 9, 'bold'), padding=8)
        style.map('Primary.TButton',
                 background=[('active', colors['secondary']), ('pressed', colors['primary'])],
                 foreground=[('active', colors['white']), ('pressed', colors['white'])])
        
        style.configure('Success.TButton', font=('Segoe UI', 9), padding=6)
        style.map('Success.TButton',
                 background=[('active', colors['success']), ('pressed', colors['success'])],
                 foreground=[('active', colors['white']), ('pressed', colors['white'])])
        
        # Notebook/Tab styles
        style.configure('TNotebook', background=colors['light_bg'], borderwidth=0)
        style.configure('TNotebook.Tab', padding=[15, 8], font=('Segoe UI', 9, 'bold'))
        style.map('TNotebook.Tab',
                 background=[('selected', colors['white']), ('active', colors['light_bg'])],
                 foreground=[('selected', colors['primary']), ('active', colors['text'])])
        
        # Entry style
        style.configure('TEntry', font=('Segoe UI', 9), padding=4, relief=tk.SOLID)
        
        # Combobox style
        style.configure('TCombobox', font=('Segoe UI', 9), padding=4)
        
        # Separator style
        style.configure('TSeparator', background=colors['primary'])
        
        # Treeview style
        style.configure('Treeview', font=('Segoe UI', 9), rowheight=24, background=colors['white'])
        style.configure('Treeview.Heading', font=('Segoe UI', 9, 'bold'), background=colors['secondary'], foreground=colors['white'])
        # Encabezados fijos sin cambios al pasar el mouse
        style.map('Treeview.Heading', background=[], foreground=[])
        style.map('Treeview', background=[('selected', colors['secondary'])])
    
    def create_main_interface(self):
        """Crear interfaz con tabs principales"""
        # Frame superior con logo y status (Header)
        top_frame = tk.Frame(self.root, bg='#2C3E50', height=70)
        top_frame.pack(fill=tk.X, padx=0, pady=0)
        top_frame.pack_propagate(False)
        
        # Contenedor interior con padding
        header_content = tk.Frame(top_frame, bg='#2C3E50')
        header_content.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)
        
        # Sección izquierda: Logo y título
        left_section = tk.Frame(header_content, bg='#2C3E50')
        left_section.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        try:
            logo_path = "logo.png"
            if os.path.exists(logo_path):
                img = Image.open(logo_path)
                img = img.resize((45, 45), Image.Resampling.LANCZOS)
                self.logo_image = ImageTk.PhotoImage(img)
                logo_label = tk.Label(left_section, image=self.logo_image, bg='#2C3E50')
                logo_label.pack(side=tk.LEFT, padx=(0, 12))
        except Exception as e:
            pass
        
        title_label = tk.Label(left_section, text="Gestión de Tiendas", 
                              font=("Segoe UI", 16, "bold"), fg="white", bg='#2C3E50')
        title_label.pack(side=tk.LEFT)
        
        # Sección derecha: Estado
        right_section = tk.Frame(header_content, bg='#2C3E50')
        right_section.pack(side=tk.RIGHT)
        
        status_icon = tk.Label(right_section, text="●", font=("Arial", 10), fg="#E74C3C", bg='#2C3E50')
        status_icon.pack(side=tk.LEFT, padx=(0, 5))
        
        self.status_label = tk.Label(right_section, text="Desconectado", 
                                     font=("Segoe UI", 9), fg="#ECF0F1", bg='#2C3E50')
        self.status_label.pack(side=tk.LEFT)
        
        # Separador visual
        separator = tk.Frame(self.root, bg='#3498DB', height=3)
        separator.pack(fill=tk.X, padx=0, pady=0)
        
        # Frame principal para los tabs
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Notebook (tabs)
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Crear tabs
        self.create_analisis_tab()
        self.create_empleados_tab()
        self.create_formulas_normales_tab()
        self.create_formulas_cce_tab()
    
    # ==================== TAB ANÁLISIS ====================
    def create_analisis_tab(self):
        """Tab de análisis general y búsquedas"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="📊 Análisis")
        
        # Frame de búsqueda
        search_frame = ttk.LabelFrame(tab, text="🔍 Búsqueda de Colores", padding=10)
        search_frame.pack(fill=tk.X, padx=10, pady=8)
        
        search_inner = ttk.Frame(search_frame)
        search_inner.pack(fill=tk.X)
        
        ttk.Label(search_inner, text="Código del Color:", font=("Segoe UI", 9, "bold")).pack(side=tk.LEFT, padx=(0, 5))
        self.color_entry = ttk.Entry(search_inner, width=25, font=("Segoe UI", 10))
        self.color_entry.pack(side=tk.LEFT, padx=5)
        self.color_entry.bind('<Return>', lambda e: self.search_color())
        
        ttk.Button(search_inner, text="🔎 Buscar", command=self.search_color).pack(side=tk.LEFT, padx=2)
        ttk.Button(search_inner, text="✕ Limpiar", command=self.clear_results).pack(side=tk.LEFT, padx=2)
        
        # Frame de vistas
        view_frame = ttk.LabelFrame(tab, text="📈 Estadísticas y Vistas", padding=10)
        view_frame.pack(fill=tk.X, padx=10, pady=8)
        
        button_frame = ttk.Frame(view_frame)
        button_frame.pack(fill=tk.X)
        
        ttk.Button(button_frame, text="📦 BACC", command=self.show_stats_bacc).pack(side=tk.LEFT, padx=3, pady=5)
        ttk.Button(button_frame, text="🎨 CCE", command=self.show_stats_cce).pack(side=tk.LEFT, padx=3, pady=5)
        ttk.Button(button_frame, text="🌈 Total Colores", command=self.show_total_colors).pack(side=tk.LEFT, padx=3, pady=5)
        ttk.Button(button_frame, text="💧 Colorantes", command=self.show_colorantes).pack(side=tk.LEFT, padx=3, pady=5)
        
        # Frame de resultados
        results_frame = ttk.LabelFrame(tab, text="📋 Resultados de Búsqueda", padding=0)
        results_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=8)
        
        self.results_text = scrolledtext.ScrolledText(results_frame, height=25, state=tk.DISABLED, 
                                                       font=("Segoe UI", 9), bg="#FFFFFF", fg="#2C3E50", wrap=tk.WORD)
        self.results_text.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)
    
    # ==================== TAB EMPLEADOS ====================
    def create_empleados_tab(self):
        """Tab de administración de empleados"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="👥 Empleados")
        
        # Frame de controles
        control_frame = ttk.LabelFrame(tab, text="⚙️ Controles y Acciones", padding=10)
        control_frame.pack(fill=tk.X, padx=10, pady=8)
        
        ttk.Button(control_frame, text="➕ Agregar Empleado", command=self.add_empleado).pack(side=tk.LEFT, padx=5, pady=5)
        
        # Frame de búsqueda
        search_frame = ttk.LabelFrame(tab, text="🔍 Búsqueda y Filtros", padding=10)
        search_frame.pack(fill=tk.X, padx=10, pady=8)
        
        search_row1 = ttk.Frame(search_frame)
        search_row1.pack(fill=tk.X, pady=5)
        
        ttk.Label(search_row1, text="Nombre:", font=("Segoe UI", 9, "bold")).pack(side=tk.LEFT, padx=(0, 5))
        self.emp_search_entry = ttk.Entry(search_row1, width=30, font=("Segoe UI", 10))
        self.emp_search_entry.pack(side=tk.LEFT, padx=5)
        self.emp_search_entry.bind('<Return>', lambda e: self.search_empleado())
        
        ttk.Label(search_row1, text="Sucursal:", font=("Segoe UI", 9, "bold")).pack(side=tk.LEFT, padx=(15, 5))
        self.emp_sucursal_combo = ttk.Combobox(search_row1, width=20, state="readonly", font=("Segoe UI", 9))
        self.emp_sucursal_combo.pack(side=tk.LEFT, padx=5)
        self.emp_sucursal_combo.bind('<<ComboboxSelected>>', lambda e: self.search_empleado())
        
        # Botones de búsqueda
        search_buttons = ttk.Frame(search_frame)
        search_buttons.pack(fill=tk.X, pady=(8, 0))
        
        ttk.Button(search_buttons, text="🔎 Buscar", command=self.search_empleado).pack(side=tk.LEFT, padx=2)
        ttk.Button(search_buttons, text="✕ Limpiar", command=self.clear_emp_search).pack(side=tk.LEFT, padx=2)
        
        # Frame de tabla
        table_frame = ttk.LabelFrame(tab, text="📋 Lista de Empleados", padding=0)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=8)
        
        # Scrollbars
        scrollbar_y = ttk.Scrollbar(table_frame)
        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        
        scrollbar_x = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL)
        scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Treeview
        columns = ("Nombre", "Código Empleado", "Sucursal", "Activo")
        self.empleados_tree = ttk.Treeview(table_frame, columns=columns, height=15,
                                           yscrollcommand=scrollbar_y.set,
                                           xscrollcommand=scrollbar_x.set)
        
        scrollbar_y.config(command=self.empleados_tree.yview)
        scrollbar_x.config(command=self.empleados_tree.xview)
        
        self.empleados_tree.column("#0", width=0, stretch=tk.NO)
        self.empleados_tree.column("Nombre", width=200, anchor=tk.W)
        self.empleados_tree.column("Código Empleado", width=130, anchor=tk.CENTER)
        self.empleados_tree.column("Sucursal", width=140, anchor=tk.CENTER)
        self.empleados_tree.column("Activo", width=70, anchor=tk.CENTER)
        
        self.empleados_tree.heading("#0", text="")
        self.empleados_tree.heading("Nombre", text="Nombre Completo")
        self.empleados_tree.heading("Código Empleado", text="Código")
        self.empleados_tree.heading("Sucursal", text="Sucursal")
        self.empleados_tree.heading("Activo", text="Estado")
        
        self.empleados_tree.pack(fill=tk.BOTH, expand=True)
        
        # Menú contextual para click derecho
        self.empleados_tree.bind("<Button-3>", self.show_emp_context_menu)
        
        # Frame de logs
        log_frame = ttk.LabelFrame(tab, text="📝 Registro de Cambios", padding=0)
        log_frame.pack(fill=tk.X, padx=10, pady=8)
        
        self.emp_log = scrolledtext.ScrolledText(log_frame, height=3, width=100, state=tk.DISABLED, 
                                                  font=("Segoe UI", 8), bg="#FFFFFF", fg="#2C3E50", wrap=tk.WORD)
        self.emp_log.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)
        
        self.load_empleados()
    
    def load_empleados(self):
        """Cargar todos los empleados desde la tabla coloristas"""
        if not self.conn:
            return
        
        try:
            for item in self.empleados_tree.get_children():
                self.empleados_tree.delete(item)
            
            # Limpiar mapa de IDs
            self.empleados_id_map = {}
            
            # Cargar todos los coloristas
            query = """
            SELECT id, nombre, codigo_empleado, sucursal, activo
            FROM coloristas
            ORDER BY nombre
            """
            
            self.cursor.execute(query)
            results = self.cursor.fetchall()
            
            # Agregar resultados al treeview
            for row in results:
                activo_text = "✓" if row['activo'] else "✗"
                item = self.empleados_tree.insert("", tk.END, text="",
                                          values=(row['nombre'], row['codigo_empleado'], 
                                                 row['sucursal'], activo_text),
                                          tags=("activo",))
                # Guardar el ID del empleado en el mapa
                self.empleados_id_map[item] = row['id']
            
            self.log_emp_message(f"✓ {len(results)} empleados cargados")
            
        except Exception as e:
            self.conn.rollback()
            self.log_emp_message(f"❌ Error: {str(e)}")
    
    def load_sucursales(self):
        """Cargar sucursales de la tabla sucursales (sincronizadas con admin)"""
        if not self.conn:
            return
        
        try:
            query = """
            SELECT nombre 
            FROM sucursales 
            WHERE activo = TRUE 
            ORDER BY nombre
            """
            
            self.cursor.execute(query)
            results = self.cursor.fetchall()
            self.sucursales = [row['nombre'] for row in results]
            
            # Si no hay sucursales en la tabla, intentar cargar desde coloristas como fallback
            if not self.sucursales:
                query_fallback = """
                SELECT DISTINCT sucursal 
                FROM coloristas 
                WHERE sucursal IS NOT NULL 
                ORDER BY sucursal
                """
                self.cursor.execute(query_fallback)
                results = self.cursor.fetchall()
                self.sucursales = [row['sucursal'] for row in results]
            
            # Actualizar combobox de sucursales con opcion "Todas"
            sucursales_list = ["Todas"] + self.sucursales
            self.emp_sucursal_combo.config(values=sucursales_list)
            self.emp_sucursal_combo.current(0)  # Seleccionar "Todas" por defecto
            
        except Exception as e:
            self.log_emp_message(f"⚠️ Error al cargar sucursales: {str(e)}")
    def search_empleado(self):
        """Buscar empleado por nombre y/o sucursal"""
        termino = self.emp_search_entry.get().strip()
        sucursal_seleccionada = self.emp_sucursal_combo.get()
        
        if not termino and sucursal_seleccionada == "Todas":
            # Si no hay filtros, cargar todos
            self.load_empleados()
            return
        
        if not self.conn:
            self.log_emp_message("❌ No conectado a BD")
            return
        
        try:
            # Reemplazar guión con espacio para mayor flexibilidad en búsqueda
            termino_busqueda = termino.replace('-', ' ').replace('_', ' ') if termino else "%"
            
            # Construir query con filtros
            query = """
            SELECT id, nombre, codigo_empleado, sucursal, activo
            FROM coloristas
            WHERE UPPER(nombre) LIKE UPPER(%s)
            """
            
            params = [f"%{termino_busqueda}%"]
            
            # Agregar filtro de sucursal si no es "Todas"
            if sucursal_seleccionada != "Todas":
                query += " AND sucursal = %s"
                params.append(sucursal_seleccionada)
            
            query += " ORDER BY nombre LIMIT 100"
            
            self.cursor.execute(query, params)
            results = self.cursor.fetchall()
            
            # Limpiar tabla y mapa de IDs
            for item in self.empleados_tree.get_children():
                self.empleados_tree.delete(item)
            self.empleados_id_map = {}
            
            # Agregar resultados al treeview
            for row in results:
                activo_text = "✓" if row['activo'] else "✗"
                item = self.empleados_tree.insert("", tk.END, text="",
                                          values=(row['nombre'], row['codigo_empleado'], 
                                                 row['sucursal'], activo_text),
                                          tags=("activo",))
                # Guardar el ID del empleado en el mapa
                self.empleados_id_map[item] = row['id']
            
            # Mostrar detalles en logs
            filtros = []
            if termino:
                filtros.append(f"Nombre: {termino}")
            if sucursal_seleccionada != "Todas":
                filtros.append(f"Sucursal: {sucursal_seleccionada}")
            
            filtro_texto = " | ".join(filtros) if filtros else "Sin filtros"
            
            self.log_emp_message(f"\n{'='*80}")
            self.log_emp_message(f"BÚSQUEDA: {filtro_texto} ({len(results)} resultados)")
            self.log_emp_message(f"{'='*80}\n")
            
            self.log_emp_message(f"✓ {len(results)} empleado(s) encontrado(s)")
            
        except Exception as e:
            self.conn.rollback()
            self.log_emp_message(f"❌ Error en búsqueda: {str(e)}")
    
    def show_emp_context_menu(self, event):
        """Mostrar menú contextual con click derecho en tabla Empleados"""
        # Seleccionar el item bajo el cursor
        item = self.empleados_tree.identify('item', event.x, event.y)
        if not item:
            return
        
        # Seleccionar el item
        self.empleados_tree.selection_set(item)
        
        # Crear menú contextual
        context_menu = tk.Menu(self.empleados_tree, tearoff=False)
        context_menu.add_command(label="✏️ Editar", command=self.edit_empleado)
        context_menu.add_command(label="🔓 Inhabilitar/Activar", command=self.disable_empleado)
        context_menu.add_separator()
        context_menu.add_command(label="🔄 Refrescar", command=self.load_empleados)
        
        # Mostrar menú en posición del cursor
        try:
            context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            context_menu.grab_release()
    
    def clear_emp_search(self):
        """Limpiar búsqueda y tabla de Empleados"""
        self.emp_search_entry.delete(0, tk.END)
        self.emp_sucursal_combo.current(0)  # Resetear a "Todas"
        self.load_empleados()
        self.log_emp_message("Búsqueda limpiada")
    
    def log_emp_message(self, message):
        """Registrar mensaje en logs de Empleados"""
        self.emp_log.config(state=tk.NORMAL)
        self.emp_log.insert(tk.END, message + "\n")
        self.emp_log.see(tk.END)
        self.emp_log.config(state=tk.DISABLED)
    
    def add_empleado(self):
        """Agregar nuevo empleado"""
        # Crear ventana de adición
        add_window = tk.Toplevel(self.root)
        add_window.title("➕ Agregar Nuevo Empleado")
        add_window.geometry("900x440")
        add_window.resizable(True, True)
        
        # Cargar icono para la ventana emergente
        try:
            icono_path = obtener_ruta_absoluta("icono.ico")
            if os.path.exists(icono_path):
                add_window.iconbitmap(icono_path)
        except Exception:
            pass
        
        # Centrar la ventana
        add_window.transient(self.root)
        add_window.grab_set()
        
        # Frame principal con padding
        main_frame = ttk.Frame(add_window, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        title_label = ttk.Label(main_frame, text="Nuevo Empleado", font=("Arial", 12, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=(0, 10))
        
        # Separador
        ttk.Separator(main_frame, orient=tk.HORIZONTAL).grid(row=1, column=0, columnspan=2, sticky=tk.EW, pady=5)
        
        # Frame de datos
        data_frame = ttk.LabelFrame(main_frame, text="Información del Empleado", padding="10")
        data_frame.grid(row=2, column=0, columnspan=2, sticky=tk.EW, pady=5)
        data_frame.columnconfigure(1, weight=1)
        
        # Campo Nombre
        ttk.Label(data_frame, text="Nombre:*").grid(row=0, column=0, sticky=tk.W, pady=5)
        nombre_entry = ttk.Entry(data_frame, width=40, font=("Arial", 10))
        nombre_entry.grid(row=0, column=1, sticky=tk.EW, pady=5, padx=(10, 0))
        
        # Campo Código Empleado
        ttk.Label(data_frame, text="Código Empleado:").grid(row=1, column=0, sticky=tk.W, pady=5)
        codigo_entry = ttk.Entry(data_frame, width=40, font=("Arial", 10))
        codigo_entry.grid(row=1, column=1, sticky=tk.EW, pady=5, padx=(10, 0))
        
        # Campo Sucursal (Combobox)
        ttk.Label(data_frame, text="Sucursal:").grid(row=2, column=0, sticky=tk.W, pady=5)
        sucursal_combo = ttk.Combobox(data_frame, width=37, values=self.sucursales, 
                                     state="readonly", font=("Arial", 10))
        sucursal_combo.grid(row=2, column=1, sticky=tk.EW, pady=5, padx=(10, 0))
        if self.sucursales:
            sucursal_combo.current(0)
        
        # Campo Activo (Checkbox)
        activo_var = tk.BooleanVar(value=True)
        ttk.Label(data_frame, text="Estado:").grid(row=3, column=0, sticky=tk.W, pady=5)
        status_frame = ttk.Frame(data_frame)
        status_frame.grid(row=3, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        ttk.Checkbutton(status_frame, text="Empleado Activo", variable=activo_var).pack(anchor=tk.W)
        
        # Frame de botones
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=2, sticky=tk.EW, pady=(10, 0))
        
        def guardar():
            nombre = nombre_entry.get().strip()
            codigo = codigo_entry.get().strip()
            sucursal = sucursal_combo.get().strip()
            activo = activo_var.get()
            
            if not nombre:
                messagebox.showwarning("Validación", "El nombre es obligatorio")
                return
            
            if not self.conn:
                messagebox.showerror("Error", "No conectado a BD")
                return
            
            try:
                # Insertar nuevo empleado
                query = """
                INSERT INTO coloristas (nombre, codigo_empleado, sucursal, activo, creado_en)
                VALUES (%s, %s, %s, %s, NOW())
                """
                
                self.cursor.execute(query, (nombre, codigo or None, sucursal or None, activo))
                self.conn.commit()
                
                self.log_emp_message(f"✓ Empleado '{nombre}' creado correctamente")
                messagebox.showinfo("Éxito", f"Empleado '{nombre}' creado correctamente")
                add_window.destroy()
                self.load_empleados()
                
            except Exception as e:
                self.conn.rollback()
                messagebox.showerror("Error", f"Error al crear empleado: {str(e)}")
                self.log_emp_message(f"❌ Error: {str(e)}")
        
        ttk.Button(button_frame, text="💾 Guardar", command=guardar).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="❌ Cancelar", command=add_window.destroy).pack(side=tk.LEFT, padx=5)
    
    def edit_empleado(self):
        """Editar empleado seleccionado"""
        selection = self.empleados_tree.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "Selecciona un empleado")
            return
        
        item = selection[0]
        empleado_id = self.empleados_id_map.get(item)
        
        if not empleado_id:
            messagebox.showerror("Error", "No se pudo obtener el ID del empleado")
            return
        
        # Obtener datos actuales del empleado
        try:
            query = "SELECT id, nombre, codigo_empleado, sucursal, activo FROM coloristas WHERE id = %s"
            self.cursor.execute(query, (empleado_id,))
            row = self.cursor.fetchone()
            
            if not row:
                messagebox.showerror("Error", "Empleado no encontrado")
                return
            
            # Crear ventana de edición
            edit_window = tk.Toplevel(self.root)
            edit_window.title(f"✏️ Editar Empleado")
            edit_window.geometry("900x440")
            edit_window.resizable(True, True)
            
            # Cargar icono para la ventana emergente
            try:
                icono_path = obtener_ruta_absoluta("icono.ico")
                if os.path.exists(icono_path):
                    edit_window.iconbitmap(icono_path)
            except Exception as e:
                pass  # Si no existe el icono, continuar sin él
            
            # Centrar la ventana
            edit_window.transient(self.root)
            edit_window.grab_set()
            
            # Frame principal con padding
            main_frame = ttk.Frame(edit_window, padding="15")
            main_frame.pack(fill=tk.BOTH, expand=True)
            
            # Título
            title_label = ttk.Label(main_frame, text=f"Empleado: {row['nombre']}", 
                                   font=("Arial", 12, "bold"))
            title_label.grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=(0, 10))
            
            # Separador
            ttk.Separator(main_frame, orient=tk.HORIZONTAL).grid(row=1, column=0, columnspan=2, sticky=tk.EW, pady=5)
            
            # Frame de datos
            data_frame = ttk.LabelFrame(main_frame, text="Información del Empleado", padding="10")
            data_frame.grid(row=2, column=0, columnspan=2, sticky=tk.EW, pady=5)
            data_frame.columnconfigure(1, weight=1)
            
            # Campo Nombre
            ttk.Label(data_frame, text="Nombre:").grid(row=0, column=0, sticky=tk.W, pady=5)
            nombre_entry = ttk.Entry(data_frame, width=40, font=("Arial", 10))
            nombre_entry.grid(row=0, column=1, sticky=tk.EW, pady=5, padx=(10, 0))
            nombre_entry.insert(0, row['nombre'])
            
            # Campo Código Empleado (READ-ONLY como Label)
            ttk.Label(data_frame, text="Código Empleado:").grid(row=1, column=0, sticky=tk.W, pady=5)
            codigo_label = ttk.Label(data_frame, text=row['codigo_empleado'] or "(sin código)", 
                                    font=("Arial", 10), foreground="#666666")
            codigo_label.grid(row=1, column=1, sticky=tk.W, pady=5, padx=(10, 0))
            
            # Campo Sucursal (Combobox)
            ttk.Label(data_frame, text="Sucursal:").grid(row=2, column=0, sticky=tk.W, pady=5)
            sucursal_combo = ttk.Combobox(data_frame, width=37, values=self.sucursales, 
                                         state="readonly", font=("Arial", 10))
            sucursal_combo.grid(row=2, column=1, sticky=tk.EW, pady=5, padx=(10, 0))
            if row['sucursal']:
                sucursal_combo.set(row['sucursal'])
            elif self.sucursales:
                sucursal_combo.current(0)
            
            # Campo Activo (Checkbox)
            activo_var = tk.BooleanVar(value=row['activo'])
            ttk.Label(data_frame, text="Estado:").grid(row=3, column=0, sticky=tk.W, pady=5)
            status_frame = ttk.Frame(data_frame)
            status_frame.grid(row=3, column=1, sticky=tk.W, pady=5, padx=(10, 0))
            ttk.Checkbutton(status_frame, text="Empleado Activo", variable=activo_var).pack(anchor=tk.W)
            
            # Frame de botones
            button_frame = ttk.Frame(main_frame)
            button_frame.grid(row=3, column=0, columnspan=2, sticky=tk.EW, pady=(10, 0))
            
            def guardar():
                self.save_empleado(empleado_id, nombre_entry.get(), row['codigo_empleado'], 
                                  sucursal_combo.get(), activo_var.get(), item, edit_window)
            
            ttk.Button(button_frame, text="💾 Guardar Cambios", command=guardar).pack(side=tk.LEFT, padx=5)
            ttk.Button(button_frame, text="❌ Cancelar", command=edit_window.destroy).pack(side=tk.LEFT, padx=5)
            
        except Exception as e:
            self.conn.rollback()
            messagebox.showerror("Error", f"Error al cargar empleado: {str(e)}")
    
    def save_empleado(self, empleado_id, nombre, codigo, sucursal, activo, item, window):
        """Guardar cambios del empleado en la BD"""
        if not nombre.strip():
            messagebox.showwarning("Validación", "El nombre no puede estar vacío")
            return
        
        if not self.conn:
            messagebox.showerror("Error", "No conectado a BD")
            return
        
        try:
            query = """
            UPDATE coloristas
            SET nombre = %s, codigo_empleado = %s, sucursal = %s, activo = %s, actualizado_en = NOW()
            WHERE id = %s
            """
            
            self.cursor.execute(query, (nombre.strip(), codigo.strip() or None, 
                                        sucursal.strip() or None, activo, empleado_id))
            self.conn.commit()
            
            # Actualizar en la tabla visual
            activo_text = "✓" if activo else "✗"
            self.empleados_tree.item(item, values=(nombre, codigo, sucursal, activo_text))
            
            self.log_emp_message(f"✓ Empleado '{nombre}' actualizado correctamente")
            messagebox.showinfo("Éxito", f"Empleado '{nombre}' guardado correctamente")
            window.destroy()
            
        except Exception as e:
            self.conn.rollback()
            messagebox.showerror("Error", f"Error al guardar: {str(e)}")
            self.log_emp_message(f"❌ Error: {str(e)}")
    
    def disable_empleado(self):
        """Inhabilitar/Activar empleado"""
        selection = self.empleados_tree.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "Selecciona un empleado")
            return
        
        item = selection[0]
        empleado_id = self.empleados_id_map.get(item)
        
        if not empleado_id:
            messagebox.showerror("Error", "No se pudo identificar el empleado")
            return
        
        if not self.conn:
            messagebox.showerror("Error", "No conectado a BD")
            return
        
        try:
            # Obtener estado actual
            query = "SELECT activo, nombre FROM coloristas WHERE id = %s"
            self.cursor.execute(query, (empleado_id,))
            row = self.cursor.fetchone()
            
            if not row:
                messagebox.showerror("Error", "Empleado no encontrado")
                return
            
            nombre = row['nombre']
            estado_actual = row['activo']
            nuevo_estado = not estado_actual
            
            # Confirmar cambio
            accion = "Activar" if nuevo_estado else "Inhabilitar"
            if not messagebox.askyesno("Confirmación", f"¿{accion} empleado '{nombre}'?"):
                return
            
            # Actualizar en BD
            query = "UPDATE coloristas SET activo = %s, actualizado_en = NOW() WHERE id = %s"
            self.cursor.execute(query, (nuevo_estado, empleado_id))
            self.conn.commit()
            
            # Actualizar en la tabla
            values = self.empleados_tree.item(item)['values']
            activo_text = "✓" if nuevo_estado else "✗"
            self.empleados_tree.item(item, values=(values[0], values[1], values[2], activo_text))
            
            accion_mensaje = "activado" if nuevo_estado else "inhabilitado"
            messagebox.showinfo("Éxito", f"Empleado '{nombre}' {accion_mensaje} correctamente")
            self.log_emp_message(f"✓ Empleado '{nombre}' {accion_mensaje}")
            
        except Exception as e:
            self.conn.rollback()
            messagebox.showerror("Error", f"Error al cambiar estado: {str(e)}")
            self.log_emp_message(f"❌ Error: {str(e)}")
    
    # ==================== TAB FÓRMULAS NORMALES ====================
    def create_formulas_normales_tab(self):
        """Tab de gestión de fórmulas normales de Excello Premium"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="🟌️ Fórmulas Normales")
        
        # Frame de búsqueda
        search_frame = ttk.LabelFrame(tab, text="🔍 Búsqueda", padding=10)
        search_frame.pack(fill=tk.X, padx=10, pady=8)
        
        search_row = ttk.Frame(search_frame)
        search_row.pack(fill=tk.X, pady=5)
        
        ttk.Label(search_row, text="Código Color:", font=("Segoe UI", 9, "bold")).pack(side=tk.LEFT, padx=(0, 5))
        self.fn_search_entry = ttk.Entry(search_row, width=20, font=("Segoe UI", 10))
        self.fn_search_entry.pack(side=tk.LEFT, padx=5)
        self.fn_search_entry.bind('<Return>', lambda e: self.search_formula_normal())
        
        ttk.Button(search_row, text="🔎 Buscar", command=self.search_formula_normal).pack(side=tk.LEFT, padx=2)
        ttk.Button(search_row, text="✕ Limpiar", command=self.clear_fn_search).pack(side=tk.LEFT, padx=2)
        
        # Frame de filtros por unidad
        filter_frame = ttk.LabelFrame(tab, text="📄 Filtrar por Presentación", padding=10)
        filter_frame.pack(fill=tk.X, padx=10, pady=8)
        
        self.fn_unit_var = tk.StringVar(value="galon")
        for unit in ["galon", "cubeta", "cuarto"]:
            ttk.Radiobutton(filter_frame, text=unit.upper(), variable=self.fn_unit_var, 
                           value=unit, command=self.on_fn_filter_changed).pack(side=tk.LEFT, padx=15)
        
        # Frame de tabla
        table_frame = ttk.LabelFrame(tab, text="📋 Fórmulas Registradas", padding=0)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=8)
        
        # Scrollbars
        scrollbar_y = ttk.Scrollbar(table_frame)
        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        
        scrollbar_x = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL)
        scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Treeview
        self.fn_tree = ttk.Treeview(table_frame, 
                                     columns=("Código", "Colorante", "OZ", "_32s", "_64s", "_128s"),
                                     height=18,
                                     yscrollcommand=scrollbar_y.set,
                                     xscrollcommand=scrollbar_x.set)
        
        scrollbar_y.config(command=self.fn_tree.yview)
        scrollbar_x.config(command=self.fn_tree.xview)
        
        self.fn_tree.column("#0", width=0, stretch=tk.NO)
        self.fn_tree.column("Código", width=110, anchor=tk.CENTER)
        self.fn_tree.column("Colorante", width=140, anchor=tk.CENTER)
        self.fn_tree.column("OZ", width=70, anchor=tk.CENTER)
        self.fn_tree.column("_32s", width=75, anchor=tk.CENTER)
        self.fn_tree.column("_64s", width=75, anchor=tk.CENTER)
        self.fn_tree.column("_128s", width=75, anchor=tk.CENTER)
        
        self.fn_tree.heading("#0", text="")
        self.fn_tree.heading("Código", text="Código Pintura")
        self.fn_tree.heading("Colorante", text="Colorante")
        self.fn_tree.heading("OZ", text="OZ")
        self.fn_tree.heading("_32s", text="32 oz")
        self.fn_tree.heading("_64s", text="64 oz")
        self.fn_tree.heading("_128s", text="128 oz")
        
        self.fn_tree.pack(fill=tk.BOTH, expand=True)
        
        # Menú contextual para click derecho
        self.fn_tree.bind("<Button-3>", self.show_fn_context_menu)
        
        # Frame de logs
        log_frame = ttk.LabelFrame(tab, text="📝 Registro de Cambios", padding=0)
        log_frame.pack(fill=tk.X, padx=10, pady=8)
        
        self.fn_log = scrolledtext.ScrolledText(log_frame, height=3, width=100, state=tk.DISABLED,
                                                font=("Segoe UI", 8), bg="#FFFFFF", fg="#2C3E50", wrap=tk.WORD)
        self.fn_log.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)
        
        self.load_formulas_normales()
    
    def load_formulas_normales(self):
        """Cargar fórmulas normales de la BD"""
        if not self.conn:
            return
        
        try:
            # Limpiar tabla
            for item in self.fn_tree.get_children():
                self.fn_tree.delete(item)
            
            # Obtener unidad seleccionada
            unit = self.fn_unit_var.get()
            
            # Cargar desde tabla presentacion (fórmulas estándar disponibles)
            query = """
            SELECT DISTINCT id_pintura, id_colorante, tipo, oz FROM presentacion
            WHERE tipo = %s
            ORDER BY id_pintura, id_colorante
            LIMIT 200
            """
            
            self.cursor.execute(query, (unit,))
            results = self.cursor.fetchall()
            
            for idx, row in enumerate(results, 1):
                # Mapear columnas: ID, Código, Nombre, Base, Ingredientes, Activo
                self.fn_tree.insert("", tk.END, text="",
                                    values=(idx, row['id_pintura'], row['id_colorante'], 
                                           row['tipo'], row['oz'], "✓"),
                                    tags=("activo",))
            
            self.log_message(f"✓ {len(results)} fórmulas normales cargadas ({unit.upper()})")
            
        except Exception as e:
            self.conn.rollback()
            self.log_message(f"❌ Error: {str(e)}")
    
    def add_formula_normal(self):
        """Agregar nueva fórmula normal"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Agregar Fórmula Normal")
        dialog.geometry("500x400")
        
        # Cargar icono para la ventana emergente
        try:
            icono_path = obtener_ruta_absoluta("icono.ico")
            if os.path.exists(icono_path):
                dialog.iconbitmap(icono_path)
        except Exception as e:
            pass  # Si no existe el icono, continuar sin él
        
        ttk.Label(dialog, text="Código Color (SW-XXXX):", font=("Arial", 10)).pack(pady=5)
        codigo_entry = ttk.Entry(dialog, width=20)
        codigo_entry.pack()
        
        ttk.Label(dialog, text="Nombre Fórmula:", font=("Arial", 10)).pack(pady=5)
        nombre_entry = ttk.Entry(dialog, width=40)
        nombre_entry.pack()
        
        ttk.Label(dialog, text="Base/Tipo (Excello Premium, etc):", font=("Arial", 10)).pack(pady=5)
        base_entry = ttk.Entry(dialog, width=40)
        base_entry.pack()
        
        ttk.Label(dialog, text="Descripción:", font=("Arial", 10)).pack(pady=5)
        desc_text = scrolledtext.ScrolledText(dialog, height=5, width=50)
        desc_text.pack(pady=5)
        
        def save():
            codigo = codigo_entry.get().strip()
            nombre = nombre_entry.get().strip()
            base = base_entry.get().strip()
            descripcion = desc_text.get("1.0", tk.END).strip()
            
            if not codigo or not nombre:
                messagebox.showwarning("Validación", "Código y Nombre son requeridos")
                return
            
            if not self.conn:
                messagebox.showerror("Error", "No conectado a BD")
                return
            
            try:
                query = """
                INSERT INTO formulas_normales (codigo_color, nombre, base, descripcion, activo)
                VALUES (%s, %s, %s, %s, TRUE)
                """
                self.cursor.execute(query, (codigo, nombre, base or None, descripcion or None))
                self.conn.commit()
                self.log_message(f"✓ Fórmula {codigo} agregada")
                self.load_formulas_normales()
                dialog.destroy()
            except Exception as e:
                self.conn.rollback()
                messagebox.showerror("Error", f"Error: {str(e)}")
        
        ttk.Button(dialog, text="Guardar", command=save).pack(pady=10)
    
    def edit_formula_normal(self):
        """Editar fórmula seleccionada"""
        selection = self.fn_tree.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "Selecciona una fórmula")
            return
        
        messagebox.showinfo("Información", "Función de edición en desarrollo")
    
    def disable_formula_normal(self):
        """Inhabilitar fórmula"""
        selection = self.fn_tree.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "Selecciona una fórmula")
            return
        
        messagebox.showinfo("Información", "Función de inhabilitación en desarrollo")
    
    def update_formula_normal_status(self, fn_id, status):
        """Actualizar estado de fórmula"""
        if not self.conn:
            return
        
        try:
            query = "UPDATE formulas_normales SET activo = %s WHERE id = %s"
            self.cursor.execute(query, (status, fn_id))
            self.conn.commit()
            self.log_message(f"✓ Fórmula actualizada" if status else "✓ Fórmula inhabilitada")
        except Exception as e:
            self.conn.rollback()
            self.log_message(f"❌ Error: {str(e)}")
    
    def search_formula_normal(self):
        """Buscar fórmula por código (búsqueda parcial) mostrando todos los datos"""
        codigo = self.fn_search_entry.get().strip()
        if not codigo:
            self.clear_fn_search()
            return
        
        if not self.conn:
            self.log_message("❌ No conectado a BD")
            return
        
        try:
            # Obtener unidad seleccionada
            unit = self.fn_unit_var.get()
            
            # Reemplazar guión con espacio para mayor flexibilidad en búsqueda
            # Así acepta tanto "7009" como "SW-7009" como "SW 7009"
            codigo_busqueda = codigo.replace('-', ' ').replace('_', ' ')
            
            # Búsqueda en tabla presentacion con coincidencia parcial - TODOS LOS DATOS
            # JOIN con tabla colorante para obtener nombre
            query = """
            SELECT p.*, c.nombre as colorante_nombre
            FROM presentacion p
            LEFT JOIN colorante c ON p.id_colorante = c.id
            WHERE UPPER(p.id_pintura) LIKE UPPER(%s)
            AND p.tipo = %s
            ORDER BY p.id_pintura, p.id_colorante
            LIMIT 100
            """
            
            self.cursor.execute(query, (f"%{codigo_busqueda}%", unit))
            results = self.cursor.fetchall()
            
            # Limpiar tabla
            for item in self.fn_tree.get_children():
                self.fn_tree.delete(item)
            
            # Agregar resultados al treeview
            for row in results:
                colorante_nombre = row['colorante_nombre'] if row['colorante_nombre'] else row['id_colorante']
                self.fn_tree.insert("", tk.END, text="",
                                    values=(row['id_pintura'], colorante_nombre, 
                                           row['oz'] or '', row['_32s'] or '', row['_64s'] or '', row['_128s'] or ''),
                                    tags=("activo",))
            
            # Mostrar detalles en logs
            self.log_message(f"\n{'='*80}")
            self.log_message(f"BÚSQUEDA: {codigo} - {unit.upper()} ({len(results)} resultados)")
            self.log_message(f"{'='*80}\n")
            
            for idx, row in enumerate(results, 1):
                self.log_message(f"--- Resultado {idx} ---")
                row_dict = dict(row)
                for key, value in row_dict.items():
                    self.log_message(f"  {key}: {value}")
                self.log_message("")
            
            self.log_message(f"✓ {len(results)} fórmula(s) encontrada(s)")
            
        except Exception as e:
            self.conn.rollback()
            self.log_message(f"❌ Error en búsqueda: {str(e)}")
    
    def show_fn_context_menu(self, event):
        """Mostrar menú contextual con click derecho en tabla Fórmulas Normales"""
        # Seleccionar el item bajo el cursor
        item = self.fn_tree.identify('item', event.x, event.y)
        if not item:
            return
        
        # Seleccionar el item
        self.fn_tree.selection_set(item)
        
        # Crear menú contextual
        context_menu = tk.Menu(self.fn_tree, tearoff=False)
        context_menu.add_command(label="✏️ Editar", command=self.edit_formula_normal)
        context_menu.add_command(label="❌ Inhabilitar", command=self.disable_formula_normal)
        context_menu.add_separator()
        context_menu.add_command(label="🔄 Refrescar", command=self.load_formulas_normales)
        
        # Mostrar menú en posición del cursor
        try:
            context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            context_menu.grab_release()
    
    def on_fn_filter_changed(self):
        """Se llama cuando cambia el filtro de presentación. Si hay búsqueda activa, re-busca"""
        codigo = self.fn_search_entry.get().strip()
        if codigo:
            # Si hay texto, ejecuta la búsqueda nuevamente con el nuevo filtro
            self.search_formula_normal()
        else:
            # Si no hay texto, limpia la tabla
            self.clear_fn_search()
    
    def clear_fn_search(self):
        """Limpiar búsqueda y tabla de Fórmulas Normales"""
        self.fn_search_entry.delete(0, tk.END)
        for item in self.fn_tree.get_children():
            self.fn_tree.delete(item)
        self.log_message("Búsqueda limpiada - escribe un código para buscar")
    
    # ==================== TAB PRESENTACIONES ====================
    def create_formulas_cce_tab(self):
        """Tab de fórmulas CCE"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="🞨 Fórmulas CCE")
        
        # Frame de filtros
        filter_frame = ttk.LabelFrame(tab, text="📄 Filtros", padding=10)
        filter_frame.pack(fill=tk.X, padx=10, pady=8)
        
        ttk.Label(filter_frame, text="Unidad:", font=("Segoe UI", 9, "bold")).pack(side=tk.LEFT, padx=(0, 10))
        self.cce_unit_var = tk.StringVar(value="galon")
        for unit in ["galon", "cubeta", "cuarto"]:
            ttk.Radiobutton(filter_frame, text=unit.upper(), variable=self.cce_unit_var, 
                          value=unit, command=self.on_cce_filter_changed).pack(side=tk.LEFT, padx=15)
        
        # Frame de búsqueda
        search_frame = ttk.LabelFrame(tab, text="🔍 Búsqueda", padding=10)
        search_frame.pack(fill=tk.X, padx=10, pady=8)
        
        search_row = ttk.Frame(search_frame)
        search_row.pack(fill=tk.X, pady=5)
        
        ttk.Label(search_row, text="Código Color:", font=("Segoe UI", 9, "bold")).pack(side=tk.LEFT, padx=(0, 5))
        self.cce_search_entry = ttk.Entry(search_row, width=20, font=("Segoe UI", 10))
        self.cce_search_entry.pack(side=tk.LEFT, padx=5)
        self.cce_search_entry.bind('<Return>', lambda e: self.search_formula_cce())
        
        ttk.Button(search_row, text="🔎 Buscar", command=self.search_formula_cce).pack(side=tk.LEFT, padx=2)
        ttk.Button(search_row, text="✕ Limpiar", command=self.clear_cce_search).pack(side=tk.LEFT, padx=2)
        
        # Frame de tabla
        table_frame = ttk.LabelFrame(tab, text="📋 Fórmulas CCE", padding=0)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=8)
        
        # Scrollbars
        scrollbar_y = ttk.Scrollbar(table_frame)
        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        
        scrollbar_x = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL)
        scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Treeview
        columns = ("Código", "Colorante", "OZ", "_32s", "_64s", "_128s")
        self.formulas_cce_tree = ttk.Treeview(table_frame, columns=columns, height=18,
                                              yscrollcommand=scrollbar_y.set,
                                              xscrollcommand=scrollbar_x.set)
        
        scrollbar_y.config(command=self.formulas_cce_tree.yview)
        scrollbar_x.config(command=self.formulas_cce_tree.xview)
        
        self.formulas_cce_tree.column("#0", width=0, stretch=tk.NO)
        self.formulas_cce_tree.column("Código", width=110, anchor=tk.CENTER)
        self.formulas_cce_tree.column("Colorante", width=140, anchor=tk.CENTER)
        self.formulas_cce_tree.column("OZ", width=70, anchor=tk.CENTER)
        self.formulas_cce_tree.column("_32s", width=75, anchor=tk.CENTER)
        self.formulas_cce_tree.column("_64s", width=75, anchor=tk.CENTER)
        self.formulas_cce_tree.column("_128s", width=75, anchor=tk.CENTER)
        
        self.formulas_cce_tree.heading("#0", text="")
        self.formulas_cce_tree.heading("Código", text="Código Pintura")
        self.formulas_cce_tree.heading("Colorante", text="Colorante")
        self.formulas_cce_tree.heading("OZ", text="OZ")
        self.formulas_cce_tree.heading("_32s", text="32 oz")
        self.formulas_cce_tree.heading("_64s", text="64 oz")
        self.formulas_cce_tree.heading("_128s", text="128 oz")
        
        self.formulas_cce_tree.pack(fill=tk.BOTH, expand=True)
        
        # Menú contextual para click derecho
        self.formulas_cce_tree.bind("<Button-3>", self.show_cce_context_menu)
        
        # Frame de logs
        log_frame = ttk.LabelFrame(tab, text="📝 Registro de Cambios", padding=0)
        log_frame.pack(fill=tk.X, padx=10, pady=8)
        
        self.cce_log = scrolledtext.ScrolledText(log_frame, height=3, width=100, state=tk.DISABLED,
                                                 font=("Segoe UI", 8), bg="#FFFFFF", fg="#2C3E50", wrap=tk.WORD)
        self.cce_log.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)
        
        self.load_formulas_cce()
    
    def load_formulas_cce(self):
        """Cargar fórmulas CCE según unidad seleccionada - solo si no hay búsqueda activa"""
        if not self.conn:
            return
        
        try:
            for item in self.formulas_cce_tree.get_children():
                self.formulas_cce_tree.delete(item)
            
            self.log_cce_message(f"Tabla vacía - Ingresa código para buscar")
            
        except Exception as e:
            self.conn.rollback()
            self.log_cce_message(f"❌ Error: {str(e)}")
    
    def search_formula_cce(self):
        """Buscar fórmula CCE por código (búsqueda parcial) mostrando todos los datos"""
        codigo = self.cce_search_entry.get().strip()
        if not codigo:
            self.clear_cce_search()
            return
        
        if not self.conn:
            self.log_cce_message("❌ No conectado a BD")
            return
        
        try:
            # Obtener unidad seleccionada
            unit = self.cce_unit_var.get()
            table_map = {"galon": "formulas_cce_g", "cubeta": "formulas_cce_c", "cuarto": "formulas_cce_qt"}
            table = table_map[unit]
            
            # Reemplazar guión con espacio para mayor flexibilidad en búsqueda
            codigo_busqueda = codigo.replace('-', ' ').replace('_', ' ')
            
            # Búsqueda en tabla formulas_cce_* con coincidencia parcial - TODOS LOS DATOS
            # JOIN con tabla colorante para obtener nombre
            query = f"""
            SELECT f.*, c.nombre as colorante_nombre
            FROM {table} f
            LEFT JOIN colorante c ON f.id_colorante = c.id
            WHERE UPPER(f.id_pintura) LIKE UPPER(%s)
            ORDER BY f.id_pintura, f.id_colorante
            LIMIT 100
            """
            
            self.cursor.execute(query, (f"%{codigo_busqueda}%",))
            results = self.cursor.fetchall()
            
            # Limpiar tabla
            for item in self.formulas_cce_tree.get_children():
                self.formulas_cce_tree.delete(item)
            
            # Agregar resultados al treeview
            for row in results:
                colorante_nombre = row['colorante_nombre'] if row['colorante_nombre'] else row['id_colorante']
                self.formulas_cce_tree.insert("", tk.END, text="",
                                            values=(row['id_pintura'], colorante_nombre, 
                                                   row['oz'] or '', row['_32s'] or '', row['_64s'] or '', row['_128s'] or ''),
                                            tags=("activo",))
            
            # Mostrar detalles en logs
            self.log_cce_message(f"\n{'='*80}")
            self.log_cce_message(f"BÚSQUEDA: {codigo} - {unit.upper()} ({len(results)} resultados)")
            self.log_cce_message(f"{'='*80}\n")
            
            for idx, row in enumerate(results, 1):
                self.log_cce_message(f"--- Resultado {idx} ---")
                row_dict = dict(row)
                for key, value in row_dict.items():
                    self.log_cce_message(f"  {key}: {value}")
                self.log_cce_message("")
            
            self.log_cce_message(f"✓ {len(results)} fórmula(s) encontrada(s)")
            
        except Exception as e:
            self.conn.rollback()
            self.log_cce_message(f"❌ Error en búsqueda: {str(e)}")
    
    def show_cce_context_menu(self, event):
        """Mostrar menú contextual con click derecho en tabla Fórmulas CCE"""
        # Seleccionar el item bajo el cursor
        item = self.formulas_cce_tree.identify('item', event.x, event.y)
        if not item:
            return
        
        # Seleccionar el item
        self.formulas_cce_tree.selection_set(item)
        
        # Crear menú contextual
        context_menu = tk.Menu(self.formulas_cce_tree, tearoff=False)
        context_menu.add_command(label="✏️ Editar", command=self.edit_formula_cce)
        context_menu.add_command(label="❌ Inhabilitar", command=self.disable_formula_cce)
        context_menu.add_separator()
        context_menu.add_command(label="🔄 Refrescar", command=self.load_formulas_cce)
        
        # Mostrar menú en posición del cursor
        try:
            context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            context_menu.grab_release()
    
    def on_cce_filter_changed(self):
        """Se llama cuando cambia el filtro de unidad. Si hay búsqueda activa, re-busca"""
        codigo = self.cce_search_entry.get().strip()
        if codigo:
            # Si hay texto, ejecuta la búsqueda nuevamente con el nuevo filtro
            self.search_formula_cce()
        else:
            # Si no hay texto, limpia la tabla
            self.clear_cce_search()
    
    def clear_cce_search(self):
        """Limpiar búsqueda y tabla de Fórmulas CCE"""
        self.cce_search_entry.delete(0, tk.END)
        for item in self.formulas_cce_tree.get_children():
            self.formulas_cce_tree.delete(item)
        self.log_cce_message("Búsqueda limpiada")
    
    def log_cce_message(self, message):
        """Registrar mensaje en logs de Fórmulas CCE"""
        self.cce_log.config(state=tk.NORMAL)
        self.cce_log.insert(tk.END, message + "\n")
        self.cce_log.see(tk.END)
        self.cce_log.config(state=tk.DISABLED)
    
    def add_formula_cce(self):
        """Agregar fórmula CCE"""
        messagebox.showinfo("Información", "Agregar fórmula CCE - En desarrollo")
    
    def edit_formula_cce(self):
        """Editar fórmula CCE"""
        messagebox.showinfo("Información", "Función de edición en desarrollo")
    
    def disable_formula_cce(self):
        """Inhabilitar fórmula CCE"""
        messagebox.showinfo("Información", "Función de inhabilitación en desarrollo")
    
    # ==================== TAB COLORES ====================
    # ==================== FUNCIONES AUXILIARES ====================
    def connect_database(self):
        """Conectar a la base de datos PostgreSQL"""
        try:
            self.conn = psycopg2.connect(
                host="dpg-d1b18u8dl3ps73e68v1g-a.oregon-postgres.render.com",
                port=5432,
                database="labels_app_db",
                user="admin",
                password="KCFjzM4KYzSQx63ArufESIXq03EFXHz3",
                sslmode='require'
            )
            self.cursor = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
            self.status_label.config(text="Conectado", foreground="#27AE60")
            
            # Cargar sucursales disponibles
            self.load_sucursales()
            
            # Cargar datos iniciales
            self.load_empleados()
            self.load_formulas_cce()
            
        except Exception as e:
            try:
                if self.conn:
                    self.conn.rollback()
            except:
                pass
            self.status_label.config(text="Desconectado", foreground="#E74C3C")
            self.log_message(f"✗ Error conectando a BD: {str(e)}")
    
    def search_color(self):
        """Buscar color en todas las tablas CCE y BACC con nombre de colorante"""
        if not hasattr(self, 'results_text'):
            return
            
        color_input = self.color_entry.get().strip().upper()
        
        if not color_input:
            messagebox.showwarning("Advertencia", "Ingrese un código de color")
            return
        
        if not self.conn:
            messagebox.showerror("Error", "No hay conexión a la base de datos")
            return
        
        # Normalizar el código: eliminar espacios y guiones
        codigo_limpio = color_input.replace(' ', '').replace('-', '')
        
        if not codigo_limpio.startswith('SW'):
            codigo_busqueda = codigo_limpio
        else:
            codigo_busqueda = codigo_limpio[2:]
        
        self.log_message(f"\n{'='*80}\nBúsqueda: {color_input} → Buscando: {codigo_busqueda}\n{'='*80}\n")
        
        try:
            # Tablas a buscar: CCE y BACC
            tablas = [
                ("GALONES CCE", "formulas_cce_g"),
                ("CUBETAS CCE", "formulas_cce_c"),
                ("CUARTOS CCE", "formulas_cce_qt"),
                ("GALONES BACC", "formulas_bacc_g"),
                ("CUBETAS BACC", "formulas_bacc_c"),
                ("CUARTOS BACC", "formulas_bacc_qt")
            ]
            
            for table_name, table in tablas:
                # Busca ignorando espacios y guiones, y trae el nombre del colorante
                query = f"""
                SELECT 
                    f.id, f.id_pintura, f.id_colorante, c.nombre as nombre_colorante,
                    f.tipo, f.oz, f._32s, f._64s, f._128s
                FROM {table} f
                LEFT JOIN colorante c ON f.id_colorante = c.id
                WHERE REPLACE(REPLACE(UPPER(f.id_pintura), ' ', ''), '-', '') LIKE %s 
                ORDER BY f.id_colorante
                """
                
                self.cursor.execute(query, (f"%{codigo_busqueda}%",))
                results = self.cursor.fetchall()
                
                if results:
                    self.log_message(f"\n{table_name}: ({len(results)} registros)")
                    self.log_message("-" * 70)
                    for row in results:
                        row_dict = dict(row)
                        # Mostrar nombre del colorante en lugar del ID
                        nombre_colorante = row_dict.pop('nombre_colorante') or 'Sin nombre'
                        id_colorante = row_dict.pop('id_colorante')
                        self.log_message(f"  Colorante: {id_colorante} ({nombre_colorante})")
                        self.log_message(f"  {row_dict}")
                        self.log_message("")
                else:
                    self.log_message(f"\n{table_name}: Sin resultados")
            
        except Exception as e:
            self.conn.rollback()
            self.log_message(f"✗ Error en búsqueda: {str(e)}")
    
    def show_stats_bacc(self):
        """Mostrar estadísticas BACC (igual que CCE pero para tablas BACC)"""
        if not self.conn:
            return
        
        try:
            self.log_message(f"\n{'='*80}\nESTADÍSTICAS SISTEMA BACC\n{'='*80}\n")
            
            for unit_name, table in [("GALONES", "formulas_bacc_g"), 
                                     ("CUBETAS", "formulas_bacc_c"), 
                                     ("CUARTOS", "formulas_bacc_qt")]:
                query = f"""
                SELECT COUNT(*) as total_filas, COUNT(DISTINCT id_pintura) as colores_unicos 
                FROM {table}
                """
                self.cursor.execute(query)
                row = self.cursor.fetchone()
                
                total = row['total_filas'] if row['total_filas'] else 0
                colores = row['colores_unicos'] if row['colores_unicos'] else 0
                self.log_message(f"{unit_name:15} - Fórmulas: {total:>6} | Colores: {colores:>6}")
            
        except Exception as e:
            self.conn.rollback()
            self.log_message(f"✗ Error: {str(e)}")
    
    def show_stats_cce(self):
        """Mostrar estadísticas CCE"""
        if not self.conn:
            return
        
        try:
            self.log_message(f"\n{'='*80}\nESTADÍSTICAS SISTEMA CCE\n{'='*80}\n")
            
            for unit_name, table in [("GALONES", "formulas_cce_g"), 
                                     ("CUBETAS", "formulas_cce_c"), 
                                     ("CUARTOS", "formulas_cce_qt")]:
                query = f"""
                SELECT COUNT(*) as total_filas, COUNT(DISTINCT id_pintura) as colores_unicos 
                FROM {table}
                """
                self.cursor.execute(query)
                row = self.cursor.fetchone()
                
                total = row['total_filas'] if row['total_filas'] else 0
                colores = row['colores_unicos'] if row['colores_unicos'] else 0
                self.log_message(f"{unit_name:15} - Fórmulas: {total:>6} | Colores: {colores:>6}")
            
        except Exception as e:
            self.conn.rollback()
            self.log_message(f"✗ Error: {str(e)}")
    
    def show_total_colors(self):
        """Mostrar total de colores únicos"""
        if not self.conn:
            return
        
        try:
            self.cursor.execute("SELECT COUNT(DISTINCT id_pintura) as total FROM formulas_cce_g")
            result = self.cursor.fetchone()
            total = result['total'] if result['total'] else 0
            
            self.log_message(f"\n✓ Total de colores únicos en sistema: {total}")
            
        except Exception as e:
            self.conn.rollback()
            self.log_message(f"✗ Error: {str(e)}")
    
    def show_colorantes(self):
        """Mostrar lista de colorantes usados en las fórmulas"""
        if not self.conn:
            return
        
        try:
            # Obtener colorantes que se usan en las fórmulas (desde presentacion y formulas_cce)
            query = """
            SELECT DISTINCT c.id, c.nombre
            FROM colorante c
            WHERE c.id IN (
                SELECT DISTINCT id_colorante FROM presentacion
                UNION
                SELECT DISTINCT id_colorante FROM formulas_cce_g
                UNION
                SELECT DISTINCT id_colorante FROM formulas_cce_c
                UNION
                SELECT DISTINCT id_colorante FROM formulas_cce_qt
            )
            ORDER BY c.nombre
            """
            
            self.cursor.execute(query)
            colorantes = self.cursor.fetchall()
            
            self.log_message(f"\n{'='*80}\nCOLORANTES USADOS EN FÓRMULAS ({len(colorantes)})\n{'='*80}\n")
            
            for col in colorantes:
                nombre = col['nombre'] if col['nombre'] else 'Sin nombre'
                self.log_message(f"  {col['id']:>3} - {nombre}")
            
        except Exception as e:
            self.conn.rollback()
            self.log_message(f"✗ Error: {str(e)}")
    
    def clear_results(self):
        """Limpiar resultados"""
        self.color_entry.delete(0, tk.END)
        self.results_text.config(state=tk.NORMAL)
        self.results_text.delete(1.0, tk.END)
        self.results_text.config(state=tk.DISABLED)
    
    def log_message(self, message):
        """Registrar mensaje en resultados"""
        self.results_text.config(state=tk.NORMAL)
        self.results_text.insert(tk.END, message + "\n")
        self.results_text.see(tk.END)
        self.results_text.config(state=tk.DISABLED)
    
    def on_empleado_select(self, event):
        """Manejar selección de empleado"""
        selection = self.empleados_tree.selection()
        if selection:
            self.selected_item = selection[0]
    
    def on_closing(self):
        """Manejar cierre de ventana"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
        self.root.destroy()


def main(usuario_id=None, username=None, usuario_nombre=None, rol=None, sucursal=None):
    """Función principal de AnalistaPF
    
    Args:
        usuario_id: ID del usuario (opcional)
        username: Username del usuario (opcional)
        usuario_nombre: Nombre completo del usuario (opcional)
        rol: Rol del usuario (opcional)
        sucursal: Sucursal del usuario (opcional)
        
    Si se llama sin parámetros, ejecuta el login. Si se llama con parámetros,
    abre AnalistaPF directamente sin login.
    """
    
    # Si se pasa info del usuario, crear app directamente sin login
    if usuario_nombre is not None:
        root = tk.Tk()
        app = AnalistaPF(root)
        app.usuario_actual = usuario_nombre
        app.sucursal_actual = sucursal
        
        root.protocol("WM_DELETE_WINDOW", app.on_closing)
        root.mainloop()
        return
    
    # Si no se pasa info, ejecutar login
    from login_analistapf import ejecutar_login
    loginok, sistema_login = ejecutar_login(master=None)
    
    if not loginok:
        return
    
    root = tk.Tk()
    app = AnalistaPF(root)
    app.usuario_actual = sistema_login.usuario_actual
    app.sucursal_actual = sistema_login.sucursal
    
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()


if __name__ == "__main__":
    main()
