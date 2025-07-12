import numpy as np
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.backends._backend_tk import NavigationToolbar2Tk
from matplotlib.figure import Figure
import random
import json
import csv
from datetime import datetime
import threading
import os

class ToolTip:
    """Clase para crear tooltips informativos"""
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.widget.bind("<Enter>", self.on_enter)
        self.widget.bind("<Leave>", self.on_leave)
        self.tooltip_window = None

    def on_enter(self, event=None):
        """Muestra el tooltip al pasar el mouse"""
        if self.tooltip_window or not self.text:
            return
        
        x, y, cx, cy = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 25
        
        self.tooltip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        
        label = tk.Label(tw, text=self.text, justify='left',
                        background='#ffffe0', relief='solid', borderwidth=1,
                        font=('Arial', 9), wraplength=300)
        label.pack(ipadx=5, ipady=3)

    def on_leave(self, event=None):
        """Oculta el tooltip al salir del widget"""
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None

class SimuladorVentiladorCPUMejorado:
    def __init__(self, root):
        self.root = root
        self.root.title("Simulador Avanzado de Control de Velocidad del Ventilador CPU")
        self.root.geometry("1600x1000")
        self.root.minsize(1200, 800)
        
        # Configurar estilo moderno
        self.configurar_estilos()
        
        # Variables de parámetros con validación
        self.params = {
            'temp_ref': tk.DoubleVar(value=65.0),
            'temp_ambiente': tk.DoubleVar(value=22.0),
            'Kp': tk.DoubleVar(value=15),
            'Ki': tk.DoubleVar(value=2),
            'Kd': tk.DoubleVar(value=0.01),
            'tiempo_scan': tk.DoubleVar(value=0.5),
            'total_time': tk.DoubleVar(value=500.0),
            'rpm_min': tk.DoubleVar(value=600),
            'rpm_max': tk.DoubleVar(value=3000),
            'rpm_nominal': tk.DoubleVar(value=1500),
            'q_cpu': tk.DoubleVar(value=1.0),
            'coef_diss': tk.DoubleVar(value=0.001),
        }

        self.perturbaciones = {
            'emi_inicio': tk.DoubleVar(value=50.0),
            'emi_duracion': tk.DoubleVar(value=3.0),
            'emi_magnitud': tk.DoubleVar(value=500.0),
        }

        # Variables de estado
        self.simulacion_activa = False
        self.datos_simulacion = None
        self.historial_simulaciones = []
        
        # Variables de configuración
        self.presets = {
            'Conservador': {'Kp': 10, 'Ki': 1, 'Kd': 0.005},
            'Balanceado': {'Kp': 15, 'Ki': 2, 'Kd': 0.01},
            'Agresivo': {'Kp': 25, 'Ki': 3, 'Kd': 0.02},
            'Alta Performance': {'Kp': 35, 'Ki': 4, 'Kd': 0.03}
        }
        
        self.crear_interfaz()
        self.configurar_tooltips()
        
    def configurar_estilos(self):
        """Configura estilos modernos para la interfaz"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configurar colores personalizados
        style.configure('Title.TLabel', font=('Arial', 12, 'bold'))
        style.configure('Header.TLabel', font=('Arial', 10, 'bold'))
        style.configure('Success.TLabel', foreground='green')
        style.configure('Error.TLabel', foreground='red')
        style.configure('Warning.TLabel', foreground='orange')
        
        # Botón de simulación destacado
        style.configure('Action.TButton', font=('Arial', 10, 'bold'))

    def crear_interfaz(self):
        """Crea la interfaz principal mejorada"""
        # Frame principal con padding mejorado
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

        # Crear barra de menú
        self.crear_menu()
        
        # Frame de título y estado
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(header_frame, text="Simulador Avanzado de Control PID", 
                 style='Title.TLabel').pack(side=tk.LEFT)
        
        self.status_label = ttk.Label(header_frame, text="Listo", style='Success.TLabel')
        self.status_label.pack(side=tk.RIGHT)

        # Frame principal dividido
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True)

        # Panel de control mejorado (izquierda)
        self.control_frame = ttk.LabelFrame(content_frame, text="Panel de Control", padding=10)
        self.control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))

        # Panel de gráficos (derecha)
        self.plot_frame = ttk.LabelFrame(content_frame, text="Visualización de Resultados", padding=5)
        self.plot_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Botón para ocultar/mostrar panel de control
        self.btn_toggle_panel = ttk.Button(self.plot_frame, text="◀ Ocultar Panel", 
                                         command=self.toggle_panel_control)
        self.btn_toggle_panel.pack(anchor=tk.NE, pady=(0, 5))
        ToolTip(self.btn_toggle_panel, "Oculta/muestra el panel de configuración\npara maximizar el espacio de los gráficos")

        self.crear_controles_mejorados(self.control_frame)
        self.crear_graficos_mejorados()

    def crear_menu(self):
        """Crea la barra de menú"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # Menú Archivo
        archivo_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Archivo", menu=archivo_menu)
        archivo_menu.add_command(label="Nueva Configuración", command=self.nueva_configuracion)
        archivo_menu.add_separator()
        archivo_menu.add_command(label="Abrir Configuración...", command=self.abrir_configuracion)
        archivo_menu.add_command(label="Guardar Configuración...", command=self.guardar_configuracion)
        archivo_menu.add_separator()
        archivo_menu.add_command(label="Exportar Datos...", command=self.exportar_datos)
        archivo_menu.add_command(label="Guardar Gráficos...", command=self.guardar_graficos)
        archivo_menu.add_separator()
        archivo_menu.add_command(label="Salir", command=self.root.quit)

        # Menú Simulación
        sim_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Simulación", menu=sim_menu)
        sim_menu.add_command(label="Ejecutar", command=self.ejecutar_simulacion_con_progreso)
        sim_menu.add_command(label="Detener", command=self.detener_simulacion)
        sim_menu.add_separator()
        sim_menu.add_command(label="Limpiar Gráficos", command=self.limpiar_graficos)
        
        # Menú Vista
        vista_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Vista", menu=vista_menu)
        vista_menu.add_command(label="Ocultar/Mostrar Panel", command=self.toggle_panel_control)
        vista_menu.add_command(label="Maximizar Ventana", command=self.maximizar_ventana)
        vista_menu.add_command(label="Restaurar Ventana", command=self.restaurar_ventana)

        # Menú Ayuda
        ayuda_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Ayuda", menu=ayuda_menu)
        ayuda_menu.add_command(label="Guía de Uso", command=self.mostrar_guia)
        ayuda_menu.add_command(label="Acerca de", command=self.mostrar_acerca_de)

    def crear_controles_mejorados(self, parent):
        """Crea los controles mejorados con validación y presets"""
        # Notebook con estilo mejorado - más angosto para dar más espacio a los gráficos
        notebook = ttk.Notebook(parent, width=350)
        notebook.pack(fill=tk.BOTH, expand=True)

        # Tab 1: Configuración del Sistema
        tab_sistema = ttk.Frame(notebook)
        notebook.add(tab_sistema, text="Sistema")
        
        # Presets de configuración
        preset_frame = ttk.LabelFrame(tab_sistema, text="Configuraciones Predefinidas", padding=5)
        preset_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.preset_var = tk.StringVar(value="Seleccionar preset...")
        preset_combo = ttk.Combobox(preset_frame, textvariable=self.preset_var, 
                                   values=list(self.presets.keys()), state="readonly", width=15)
        preset_combo.pack(side=tk.LEFT, padx=(0, 5))
        preset_combo.bind('<<ComboboxSelected>>', self.aplicar_preset)
        ToolTip(preset_combo, "Configuraciones predefinidas optimizadas:\n\n• Conservador: Respuesta lenta pero muy estable\n• Balanceado: Compromiso entre velocidad y estabilidad\n• Agresivo: Respuesta rápida con posible overshoot\n• Alta Performance: Máxima velocidad de respuesta")
        
        btn_aplicar = ttk.Button(preset_frame, text="Aplicar", command=self.aplicar_preset)
        btn_aplicar.pack(side=tk.LEFT)
        ToolTip(btn_aplicar, "Aplica la configuración seleccionada.\nSobrescribe los valores actuales de Kp, Ki y Kd.")

        # Parámetros del sistema con agrupación visual
        params_frame = ttk.LabelFrame(tab_sistema, text="Parámetros del Sistema", padding=5)
        params_frame.pack(fill=tk.BOTH, expand=True)

        # Grupo: Temperaturas
        temp_group = ttk.LabelFrame(params_frame, text="Temperaturas", padding=5)
        temp_group.pack(fill=tk.X, pady=(0, 5))
        
        self.crear_campo_validado(temp_group, "Temperatura objetivo (°C):", 'temp_ref', 20, 100)
        self.crear_campo_validado(temp_group, "Temperatura ambiente (°C):", 'temp_ambiente', 10, 40)

        # Grupo: Control PID
        pid_group = ttk.LabelFrame(params_frame, text="Control PID", padding=5)
        pid_group.pack(fill=tk.X, pady=(0, 5))
        
        self.crear_campo_validado(pid_group, "Ganancia Proporcional (Kp):", 'Kp', 1, 100)
        self.crear_campo_validado(pid_group, "Ganancia Integral (Ki):", 'Ki', 0.1, 50)
        self.crear_campo_validado(pid_group, "Ganancia Derivativa (Kd):", 'Kd', 0.001, 1)

        # Grupo: Timing
        timing_group = ttk.LabelFrame(params_frame, text="Temporización", padding=5)
        timing_group.pack(fill=tk.X, pady=(0, 5))
        
        self.crear_campo_validado(timing_group, "Tiempo de muestreo (s):", 'tiempo_scan', 0.1, 2.0)
        self.crear_campo_validado(timing_group, "Tiempo total (s):", 'total_time', 10, 2000)

        # Grupo: RPM
        rpm_group = ttk.LabelFrame(params_frame, text="Ventilador", padding=5)
        rpm_group.pack(fill=tk.X, pady=(0, 5))
        
        self.crear_campo_validado(rpm_group, "RPM mínimo:", 'rpm_min', 300, 1000)
        self.crear_campo_validado(rpm_group, "RPM máximo:", 'rpm_max', 2000, 5000)
        self.crear_campo_validado(rpm_group, "RPM nominal:", 'rpm_nominal', 800, 3000)

        # Grupo: Física del sistema
        fisica_group = ttk.LabelFrame(params_frame, text="Física del Sistema", padding=5)
        fisica_group.pack(fill=tk.X)
        
        self.crear_campo_validado(fisica_group, "Generación de calor (°C/s):", 'q_cpu', 0.1, 10)
        self.crear_campo_validado(fisica_group, "Coef. disipación (°C/s/RPM):", 'coef_diss', 0.0001, 0.01)

        # Tab 2: Perturbaciones EMI/RFI
        tab_pert = ttk.Frame(notebook)
        notebook.add(tab_pert, text="Perturbaciones")

        pert_frame = ttk.LabelFrame(tab_pert, text="Interferencias EMI/RFI", padding=10)
        pert_frame.pack(fill=tk.BOTH, expand=True)

        self.crear_campo_validado(pert_frame, "Inicio de EMI (s):", 'emi_inicio', 0, 1000, es_perturbacion=True)
        self.crear_campo_validado(pert_frame, "Duración de EMI (s):", 'emi_duracion', 0.1, 100, es_perturbacion=True)
        self.crear_campo_validado(pert_frame, "Magnitud EMI (RPM):", 'emi_magnitud', 10, 2000, es_perturbacion=True)

        # Simulación de múltiples perturbaciones
        multi_pert_frame = ttk.LabelFrame(tab_pert, text="Perturbaciones Múltiples", padding=5)
        multi_pert_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.multiple_pert_var = tk.BooleanVar()
        checkbox_multi = ttk.Checkbutton(multi_pert_frame, text="Simular múltiples perturbaciones aleatorias", 
                                        variable=self.multiple_pert_var)
        checkbox_multi.pack()
        ToolTip(checkbox_multi, "Funcionalidad experimental:\nGenera perturbaciones adicionales aleatorias durante la simulación\npara probar la robustez del controlador.")

        # Tab 3: Control y Resultados
        tab_control = ttk.Frame(notebook)
        notebook.add(tab_control, text="Control")

        # Botones de control mejorados
        control_buttons_frame = ttk.Frame(tab_control)
        control_buttons_frame.pack(fill=tk.X, pady=(0, 10))

        self.btn_ejecutar = ttk.Button(control_buttons_frame, text="Ejecutar Simulación", 
                                      command=self.ejecutar_simulacion_con_progreso, style='Action.TButton')
        self.btn_ejecutar.pack(fill=tk.X, pady=2)
        ToolTip(self.btn_ejecutar, "Ejecuta la simulación con los parámetros actuales.\nLa simulación se ejecuta en segundo plano sin bloquear la interfaz.")

        self.btn_detener = ttk.Button(control_buttons_frame, text="Detener", 
                                     command=self.detener_simulacion, state='disabled')
        self.btn_detener.pack(fill=tk.X, pady=2)
        ToolTip(self.btn_detener, "Detiene la simulación en curso.\nSolo disponible durante la ejecución.")

        btn_limpiar = ttk.Button(control_buttons_frame, text="Limpiar", 
                               command=self.limpiar_graficos)
        btn_limpiar.pack(fill=tk.X, pady=2)
        ToolTip(btn_limpiar, "Limpia todos los gráficos y resultados.\nNo afecta los parámetros de configuración.")

        btn_guardar = ttk.Button(control_buttons_frame, text="Guardar Gráficos", 
                               command=self.guardar_graficos)
        btn_guardar.pack(fill=tk.X, pady=2)
        ToolTip(btn_guardar, "Guarda los gráficos actuales en un archivo de imagen.\nSoporta PNG, PDF, SVG y JPEG.")

        # Barra de progreso
        self.progress = ttk.Progressbar(tab_control, mode='determinate')
        self.progress.pack(fill=tk.X, pady=(0, 10))
        ToolTip(self.progress, "Indica el progreso de la simulación en curso.\nSe actualiza en tiempo real durante la ejecución.")

        # Área de resultados mejorada
        results_frame = ttk.LabelFrame(tab_control, text="Resultados y Análisis", padding=5)
        results_frame.pack(fill=tk.BOTH, expand=True)

        # Pestañas para diferentes tipos de resultados
        results_notebook = ttk.Notebook(results_frame)
        results_notebook.pack(fill=tk.BOTH, expand=True)

        # Log de simulación
        log_frame = ttk.Frame(results_notebook)
        results_notebook.add(log_frame, text="Log")
        
        self.resultado_text = tk.Text(log_frame, height=12, width=40, font=('Consolas', 9))
        scrollbar_log = ttk.Scrollbar(log_frame, orient="vertical", command=self.resultado_text.yview)
        self.resultado_text.configure(yscrollcommand=scrollbar_log.set)
        self.resultado_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar_log.pack(side=tk.RIGHT, fill=tk.Y)
        ToolTip(self.resultado_text, "Registro detallado de la simulación:\n• Parámetros iniciales\n• Progreso de la simulación\n• Mensajes de estado\n• Resumen final")

        # Análisis estadístico
        stats_frame = ttk.Frame(results_notebook)
        results_notebook.add(stats_frame, text="Estadísticas")
        
        self.stats_text = tk.Text(stats_frame, height=12, width=40, font=('Consolas', 9))
        scrollbar_stats = ttk.Scrollbar(stats_frame, orient="vertical", command=self.stats_text.yview)
        self.stats_text.configure(yscrollcommand=scrollbar_stats.set)
        self.stats_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar_stats.pack(side=tk.RIGHT, fill=tk.Y)
        ToolTip(self.stats_text, "Análisis estadístico automático:\n• Métricas de rendimiento (RMSE, MAE)\n• Tiempo de establecimiento\n• Análisis de overshoot\n• Evaluación de calidad del control")

    def crear_campo_validado(self, parent, label, key, min_val, max_val, es_perturbacion=False):
        """Crea un campo de entrada con validación visual y tooltip"""
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.X, pady=1)
        
        label_widget = ttk.Label(frame, text=label, width=24)
        label_widget.pack(side=tk.LEFT)
        
        # Variable apropiada
        var = self.perturbaciones[key] if es_perturbacion else self.params[key]
        
        # Entry con validación - más ancho y expandible
        entry = ttk.Entry(frame, textvariable=var, width=14)
        entry.pack(side=tk.RIGHT, padx=(5, 0), fill=tk.X, expand=True)
        
        # Tooltip informativo
        tooltip_text = self.obtener_tooltip_texto(key, min_val, max_val)
        ToolTip(entry, tooltip_text)
        ToolTip(label_widget, tooltip_text)
        
        # Validación en tiempo real
        def validar(*args):
            try:
                value = var.get()
                if min_val <= value <= max_val:
                    entry.configure(style='TEntry')
                else:
                    entry.configure(style='Error.TEntry')
            except:
                entry.configure(style='Error.TEntry')
        
        var.trace('w', validar)

    def crear_graficos_mejorados(self):
        """Crea los gráficos con mejor diseño y sin espacio en blanco arriba"""
        self.fig = Figure(figsize=(16, 14), dpi=100)
        self.fig.patch.set_facecolor('white')

        # Canvas de Tkinter con scroll horizontal y vertical
        graficos_container = ttk.Frame(self.plot_frame)
        graficos_container.pack(fill=tk.BOTH, expand=True)

        self.scroll_canvas = tk.Canvas(graficos_container)
        self.scroll_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar_v = ttk.Scrollbar(graficos_container, orient=tk.VERTICAL, command=self.scroll_canvas.yview)
        self.scrollbar_v.pack(side=tk.RIGHT, fill=tk.Y)
        self.scrollbar_h = ttk.Scrollbar(self.plot_frame, orient=tk.HORIZONTAL, command=self.scroll_canvas.xview)
        self.scrollbar_h.pack(side=tk.BOTTOM, fill=tk.X)
        self.scroll_canvas.configure(yscrollcommand=self.scrollbar_v.set, xscrollcommand=self.scrollbar_h.set)

        # Widget de matplotlib directamente en el canvas de scroll
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.scroll_canvas)
        self.canvas.draw()
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_window = self.scroll_canvas.create_window((0, 0), window=self.canvas_widget, anchor="nw")

        # Botón flotante arriba a la derecha
        self.btn_toggle_panel = ttk.Button(self.plot_frame, text="◀ Ocultar Panel", command=self.toggle_panel_control)
        self.btn_toggle_panel.place(relx=1.0, y=2, anchor='ne')
        ToolTip(self.btn_toggle_panel, "Oculta/muestra el panel de configuración\npara maximizar el espacio de los gráficos")

        # Toolbar
        toolbar_frame = ttk.Frame(self.plot_frame)
        toolbar_frame.pack(fill=tk.X)
        NavigationToolbar2Tk(self.canvas, toolbar_frame)

        # Ejes
        self.ax1 = self.fig.add_subplot(4, 1, 1)
        self.ax2 = self.fig.add_subplot(4, 1, 2)
        self.ax3 = self.fig.add_subplot(4, 1, 3)
        self.ax4 = self.fig.add_subplot(4, 1, 4)

        # Ajustar scrollregion cuando cambie el tamaño del gráfico
        def _update_scrollregion(event=None):
            self.scroll_canvas.configure(scrollregion=self.scroll_canvas.bbox("all"))
        self.canvas_widget.bind("<Configure>", _update_scrollregion)
        self.scroll_canvas.bind("<Configure>", _update_scrollregion)

    def configurar_tooltips(self):
        """Configura tooltips explicativos"""
        # Los tooltips ahora se configuran automáticamente en crear_campo_validado
        pass

    def obtener_tooltip_texto(self, key, min_val, max_val):
        """Obtiene el texto del tooltip para un parámetro específico"""
        tooltips = {
            'temp_ref': f"Temperatura objetivo que el sistema debe mantener.\nRango válido: {min_val}°C - {max_val}°C\n\nUna temperatura más alta requiere mayor velocidad del ventilador.",
            
            'temp_ambiente': f"Temperatura del ambiente donde opera el sistema.\nRango válido: {min_val}°C - {max_val}°C\n\nTemperatura base desde la cual se calcula la disipación de calor.",
            
            'Kp': f"Ganancia Proporcional del controlador PID.\nRango válido: {min_val} - {max_val}\n\n• Valores altos: respuesta rápida pero posible inestabilidad\n• Valores bajos: respuesta lenta pero más estable",
            
            'Ki': f"Ganancia Integral del controlador PID.\nRango válido: {min_val} - {max_val}\n\n• Elimina el error en estado estacionario\n• Valores altos pueden causar oscilaciones\n• Valores bajos hacen la respuesta más lenta",
            
            'Kd': f"Ganancia Derivativa del controlador PID.\nRango válido: {min_val} - {max_val}\n\n• Reduce el overshoot y oscilaciones\n• Amplifica el ruido si es muy alto\n• Mejora la estabilidad del sistema",
            
            'tiempo_scan': f"Tiempo de muestreo del controlador.\nRango válido: {min_val}s - {max_val}s\n\n• Valores menores: control más preciso pero mayor carga computacional\n• Valores mayores: menos precisión pero más eficiente",
            
            'total_time': f"Duración total de la simulación.\nRango válido: {min_val}s - {max_val}s\n\nTiempo suficiente para observar la respuesta completa del sistema.",
            
            'rpm_min': f"RPM mínimo del ventilador.\nRango válido: {min_val} - {max_val}\n\nVelocidad mínima a la que puede operar el ventilador.",
            
            'rpm_max': f"RPM máximo del ventilador.\nRango válido: {min_val} - {max_val}\n\nVelocidad máxima que puede alcanzar el ventilador.",
            
            'rpm_nominal': f"RPM nominal inicial del ventilador.\nRango válido: {min_val} - {max_val}\n\nVelocidad de operación inicial antes de aplicar el control.",
            
            'q_cpu': f"Generación de calor de la CPU.\nRango válido: {min_val}°C/s - {max_val}°C/s\n\nCantidad de calor que genera la CPU por segundo.",
            
            'coef_diss': f"Coeficiente de disipación del ventilador.\nRango válido: {min_val} - {max_val}\n\nEficiencia del ventilador para disipar calor por RPM.",
            
            'emi_inicio': f"Momento de inicio de la interferencia EMI.\nRango válido: {min_val}s - {max_val}s\n\nTiempo en que comienza la perturbación electromagnética.",
            
            'emi_duracion': f"Duración de la interferencia EMI.\nRango válido: {min_val}s - {max_val}s\n\nTiempo que dura la perturbación electromagnética.",
            
            'emi_magnitud': f"Magnitud de la interferencia EMI.\nRango válido: {min_val} - {max_val} RPM\n\nIntensidad de la perturbación que afecta al ventilador."
        }
        
        return tooltips.get(key, f"Parámetro {key}\nRango válido: {min_val} - {max_val}")

    def aplicar_preset(self, event=None):
        """Aplica una configuración predefinida"""
        preset_name = self.preset_var.get()
        if preset_name in self.presets:
            preset = self.presets[preset_name]
            for param, value in preset.items():
                if param in self.params:
                    self.params[param].set(value)
            self.actualizar_status(f"Preset '{preset_name}' aplicado", 'success')

    def ejecutar_simulacion_con_progreso(self):
        """Ejecuta la simulación en un hilo separado con barra de progreso"""
        if self.simulacion_activa:
            return
            
        self.simulacion_activa = True
        self.btn_ejecutar.configure(state='disabled')
        self.btn_detener.configure(state='normal')
        self.progress['value'] = 0
        self.actualizar_status("Ejecutando simulación...", 'warning')
        
        # Ejecutar en hilo separado
        thread = threading.Thread(target=self.ejecutar_simulacion_thread)
        thread.daemon = True
        thread.start()

    def ejecutar_simulacion_thread(self):
        """Hilo de ejecución de la simulación"""
        try:
            self.ejecutar_simulacion()
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", str(e)))
        finally:
            self.root.after(0, self.finalizar_simulacion)

    def finalizar_simulacion(self):
        """Finaliza la simulación y restaura la interfaz"""
        self.simulacion_activa = False
        self.btn_ejecutar.configure(state='normal')
        self.btn_detener.configure(state='disabled')
        self.progress['value'] = 100
        self.actualizar_status("Simulación completada", 'success')

    def detener_simulacion(self):
        """Detiene la simulación en curso"""
        self.simulacion_activa = False
        self.actualizar_status("Simulación detenida", 'warning')

    def ejecutar_simulacion(self):
        """Ejecuta la simulación principal (código adaptado del original)"""
        try:
            # Obtener parámetros
            temp_ref = self.params['temp_ref'].get()
            temp_ambiente = self.params['temp_ambiente'].get()
            Kp = self.params['Kp'].get()
            Ki = self.params['Ki'].get()
            Kd = self.params['Kd'].get()
            dt = self.params['tiempo_scan'].get()
            T = self.params['total_time'].get()

            rpm_min = self.params['rpm_min'].get()
            rpm_max = self.params['rpm_max'].get()
            rpm = self.params['rpm_nominal'].get()

            q_cpu = self.params['q_cpu'].get()
            coef_diss = self.params['coef_diss'].get()

            emi_ini = self.perturbaciones['emi_inicio'].get()
            emi_dur = self.perturbaciones['emi_duracion'].get()
            emi_mag = self.perturbaciones['emi_magnitud'].get()

            t_values = np.arange(0, T, dt)
            total_steps = len(t_values)
            temp_cpu = temp_ambiente + 10
            integral = 0
            error_prev = 0

            # Arrays para almacenar datos
            temps = []
            rpms = []
            accion_p = []
            accion_i = []
            refs = []
            errores = []
            controles = []
            salida_actuador = []
            perturbaciones = []

            falla_detectada = False

            # Log inicial
            self.root.after(0, lambda: self.log_simulacion(
                f"=== INICIO DE SIMULACIÓN ===\n"
                f"Temperatura objetivo: {temp_ref}°C\n"
                f"Ganancias: Kp={Kp}, Ki={Ki}, Kd={Kd}\n"
                f"Tiempo total: {T}s\n"
            ))

            # Bucle principal de simulación
            for i, t in enumerate(t_values):
                if not self.simulacion_activa:
                    break
                    
                # Actualizar progreso
                progress = int((i / total_steps) * 100)
                self.root.after(0, lambda p=progress: setattr(self.progress, 'value', p))

                # Lógica de control (adaptada del original)
                error = temp_ref - temp_cpu
                
                p = 0
                i_val = 0
                d = 0
                
                if abs(error) < 10:
                    control = 0
                else:
                    p = Kp * error
                    d = Kd * (error - error_prev) / dt
                    integral_candidate = integral + error * dt
                    i_val = Ki * integral_candidate
                    control = -(p + i_val)

                max_delta_rpm = 100
                if control > max_delta_rpm:
                    control = max_delta_rpm
                elif control < -max_delta_rpm:
                    control = -max_delta_rpm

                rpm += control

                # Perturbación EMI
                perturbacion_emi = 0
                if emi_ini <= t <= emi_ini + emi_dur:
                    perturbacion_emi = -emi_mag
                    rpm += perturbacion_emi

                rpm = max(rpm_min, min(rpm_max, rpm))

                # Anti-windup
                if (rpm <= rpm_min and error > 0) or (rpm >= rpm_max and error < 0):
                    pass
                else:
                    integral = integral_candidate
                    integral = max(min(integral, 300), -300)

                # Modelo físico
                ruido = random.uniform(-0.1, 0.1)
                efecto_ventilador = coef_diss * rpm
                dtemp = (q_cpu - efecto_ventilador) * dt
                temp_cpu += dtemp + ruido
                temp_cpu = max(temp_ambiente, temp_cpu)

                # Almacenar datos
                temps.append(temp_cpu)
                rpms.append(rpm)
                accion_p.append(p)
                accion_i.append(i_val)
                refs.append(temp_ref)
                errores.append(error)
                controles.append(control)
                salida_actuador.append(rpm)
                perturbaciones.append(perturbacion_emi)

                error_prev = error

                # Detección de falla
                if (emi_dur / T > 0.5) and abs(temp_ref - temp_cpu) > 20:
                    falla_detectada = True

            # Almacenar datos para análisis
            self.datos_simulacion = {
                't_values': t_values[:len(temps)],
                'temps': temps,
                'rpms': rpms,
                'accion_p': accion_p,
                'accion_i': accion_i,
                'refs': refs,
                'errores': errores,
                'controles': controles,
                'salida_actuador': salida_actuador,
                'perturbaciones': perturbaciones,
                'falla_detectada': falla_detectada,
                'emi_ini': emi_ini,
                'emi_dur': emi_dur
            }

            # Actualizar gráficos
            self.root.after(0, self.actualizar_graficos)
            
            # Generar análisis estadístico
            self.root.after(0, self.generar_analisis)

        except Exception as e:
            raise e

    def actualizar_graficos(self):
        """Actualiza los gráficos con los datos de la simulación"""
        if not self.datos_simulacion:
            return
        datos = self.datos_simulacion
        t_values = datos['t_values']
        temps = datos['temps']
        rpms = datos['rpms']
        accion_p = datos['accion_p']
        accion_i = datos['accion_i']
        refs = datos['refs']
        errores = datos['errores']
        controles = datos['controles']
        salida_actuador = datos['salida_actuador']
        perturbaciones = datos['perturbaciones']
        falla_detectada = datos['falla_detectada']
        emi_ini = datos['emi_ini']
        emi_dur = datos['emi_dur']

        # Limpiar gráficos
        for ax in [self.ax1, self.ax2, self.ax3, self.ax4]:
            ax.clear()

        # Configurar colores y estilos mejorados
        color_temp = '#2E8B57'
        color_ref = '#DC143C'
        color_rpm = '#4169E1'
        color_error = '#FF6347'

        # Gráfico 1 - Temperatura
        if falla_detectada:
            idx_falla = next((i for i, t in enumerate(t_values) if t >= emi_ini), 0)
            self.ax1.plot(t_values[:idx_falla], temps[:idx_falla], 
                         color=color_temp, linewidth=2, label='Temp CPU')
            self.ax1.plot(t_values[idx_falla:], temps[idx_falla:], 
                         color='red', linewidth=2, label='Temp durante Falla')
            self.ax1.text(0.5, 0.85, '⚠️ FALLA DEL SISTEMA', 
                         transform=self.ax1.transAxes, fontsize=14, color='red', 
                         ha='center', bbox=dict(boxstyle="round,pad=0.3", facecolor="yellow", alpha=0.7))
        else:
            self.ax1.plot(t_values, temps, color=color_temp, linewidth=2, label='Temp CPU')

        self.ax1.axhline(refs[0], color=color_ref, linestyle='--', linewidth=2, label='Referencia')
        self.ax1.axvline(emi_ini, color='red', linestyle=':', alpha=0.7, label='Inicio EMI')
        self.ax1.axvline(emi_ini + emi_dur, color='purple', linestyle=':', alpha=0.7, label='Fin EMI')
        self.ax1.axvspan(emi_ini, emi_ini + emi_dur, color='red', alpha=0.1)
        
        self.ax1.set_title('Temperatura de la CPU', fontsize=12, fontweight='bold')
        self.ax1.set_ylabel('Temperatura (°C)')
        self.ax1.legend(loc='lower left', fontsize=8)
        self.ax1.grid(True, alpha=0.3)

        # Gráfico 2 - RPM
        if falla_detectada:
            idx_falla = next((i for i, t in enumerate(t_values) if t >= emi_ini), 0)
            self.ax2.plot(t_values[:idx_falla], rpms[:idx_falla], 
                         color=color_rpm, linewidth=2, label='RPM')
            self.ax2.plot(t_values[idx_falla:], rpms[idx_falla:], 
                         color='red', linewidth=2, label='RPM durante Falla')
        else:
            self.ax2.plot(t_values, rpms, color=color_rpm, linewidth=2, label='RPM')

        self.ax2.axvline(emi_ini, color='red', linestyle=':', alpha=0.7)
        self.ax2.axvline(emi_ini + emi_dur, color='purple', linestyle=':', alpha=0.7)
        self.ax2.axvspan(emi_ini, emi_ini + emi_dur, color='red', alpha=0.1)
        
        self.ax2.set_title('RPM del Ventilador', fontsize=12, fontweight='bold')
        self.ax2.set_ylabel('RPM')
        self.ax2.legend(loc='lower left', fontsize=8)
        self.ax2.grid(True, alpha=0.3)

        # Gráfico 3 - Acción PID
        self.ax3.plot(t_values, accion_p, color='orange', linewidth=2, label='Acción Proporcional')
        self.ax3.plot(t_values, accion_i, color='green', linewidth=2, label='Acción Integral')
        self.ax3.axvline(emi_ini, color='red', linestyle=':', alpha=0.7)
        self.ax3.axvline(emi_ini + emi_dur, color='purple', linestyle=':', alpha=0.7)
        self.ax3.axvspan(emi_ini, emi_ini + emi_dur, color='red', alpha=0.1)
        
        self.ax3.set_title('Acciones del Control PID', fontsize=12, fontweight='bold')
        self.ax3.set_ylabel('Acción de Control')
        self.ax3.legend(loc='lower left', fontsize=8)
        self.ax3.grid(True, alpha=0.3)

        # Gráfico 4 - Señales del sistema
        self.ax4.plot(t_values, temps, label='Temp CPU', color=color_temp, linewidth=1.5)
        self.ax4.plot(t_values, refs, label='Referencia', color=color_ref, linestyle='--', linewidth=1.5)
        self.ax4.plot(t_values, errores, label='Error', color=color_error, linewidth=1)
        self.ax4.plot(t_values, controles, label='Control', color='orange', linewidth=1)
        
        self.ax4.set_title('Señales del Sistema', fontsize=12, fontweight='bold')
        self.ax4.set_ylabel('Amplitud')
        self.ax4.set_xlabel('Tiempo (s)')
        self.ax4.legend(loc='lower left', fontsize=8)
        self.ax4.grid(True, alpha=0.3)

        # Ajustar márgenes: poco margen arriba y espacio entre gráficos
        self.fig.subplots_adjust(top=0.95, hspace=0.35)
        self.canvas.draw()
        # Ajustar scrollregion después de dibujar
        self.scroll_canvas.configure(scrollregion=self.scroll_canvas.bbox("all"))

    def generar_analisis(self):
        """Genera análisis estadístico de los resultados"""
        if not self.datos_simulacion:
            return

        datos = self.datos_simulacion
        temps = np.array(datos['temps'])
        rpms = np.array(datos['rpms'])
        errores = np.array(datos['errores'])
        
        # Calcular estadísticas
        temp_final = temps[-1]
        temp_max = np.max(temps)
        temp_min = np.min(temps)
        temp_promedio = np.mean(temps)
        temp_std = np.std(temps)
        
        rpm_final = rpms[-1]
        rpm_max = np.max(rpms)
        rpm_min = np.min(rpms)
        rpm_promedio = np.mean(rpms)
        
        error_final = errores[-1]
        error_rmse = np.sqrt(np.mean(errores**2))
        error_mae = np.mean(np.abs(errores))
        
        # Análisis de estabilidad
        settling_time = self.calcular_tiempo_establecimiento(datos['t_values'], temps, datos['refs'][0])
        overshoot = self.calcular_overshoot(temps, datos['refs'][0])
        
        # Mostrar análisis
        analisis = f"""=== ANÁLISIS ESTADÍSTICO ===

📊 TEMPERATURAS:
  • Final: {temp_final:.2f}°C
  • Máxima: {temp_max:.2f}°C
  • Mínima: {temp_min:.2f}°C
  • Promedio: {temp_promedio:.2f}°C
  • Desv. Estándar: {temp_std:.2f}°C

🔄 RPM:
  • Final: {rpm_final:.0f}
  • Máximo: {rpm_max:.0f}
  • Mínimo: {rpm_min:.0f}
  • Promedio: {rpm_promedio:.0f}

⚡ ERROR DE CONTROL:
  • Final: {error_final:.2f}°C
  • RMSE: {error_rmse:.2f}°C
  • MAE: {error_mae:.2f}°C

📈 ANÁLISIS DE RESPUESTA:
  • Tiempo de establecimiento: {settling_time:.1f}s
  • Sobrepaso: {overshoot:.1f}%
  
🎯 CALIDAD DEL CONTROL:
  • {self.evaluar_calidad_control(error_rmse, overshoot, settling_time)}

{'⚠️ FALLA DETECTADA' if datos['falla_detectada'] else '✅ SISTEMA ESTABLE'}
"""
        
        self.stats_text.delete(1.0, tk.END)
        self.stats_text.insert(tk.END, analisis)

    def calcular_tiempo_establecimiento(self, t_values, temps, ref, tolerancia=0.02):
        """Calcula el tiempo de establecimiento (2% de tolerancia)"""
        error_rel = np.abs(np.array(temps) - ref) / ref
        indices_estables = np.where(error_rel <= tolerancia)[0]
        
        if len(indices_estables) > 0:
            # Buscar el primer punto donde se mantiene estable por al menos 10 muestras
            for i in indices_estables:
                if i + 10 < len(error_rel) and all(error_rel[i:i+10] <= tolerancia):
                    return t_values[i]
        
        return t_values[-1]  # Si no se estabiliza, retornar tiempo total

    def calcular_overshoot(self, temps, ref):
        """Calcula el sobrepaso máximo"""
        max_temp = max(temps)
        if max_temp > ref:
            return ((max_temp - ref) / ref) * 100
        return 0

    def evaluar_calidad_control(self, rmse, overshoot, settling_time):
        """Evalúa la calidad del control basado en métricas"""
        if rmse < 1 and overshoot < 5 and settling_time < 100:
            return "🌟 EXCELENTE - Control muy preciso"
        elif rmse < 2 and overshoot < 10 and settling_time < 200:
            return "✅ BUENO - Control aceptable"
        elif rmse < 5 and overshoot < 20 and settling_time < 300:
            return "⚠️ REGULAR - Necesita ajustes"
        else:
            return "❌ DEFICIENTE - Requiere resintonización"

    def log_simulacion(self, mensaje):
        """Agrega mensaje al log de simulación"""
        self.resultado_text.insert(tk.END, mensaje + "\n")
        self.resultado_text.see(tk.END)

    def actualizar_status(self, mensaje, tipo='info'):
        """Actualiza el mensaje de estado"""
        styles = {
            'success': 'Success.TLabel',
            'error': 'Error.TLabel', 
            'warning': 'Warning.TLabel',
            'info': 'TLabel'
        }
        self.status_label.configure(text=mensaje, style=styles.get(tipo, 'TLabel'))

    def limpiar_graficos(self):
        """Limpia todos los gráficos"""
        for ax in [self.ax1, self.ax2, self.ax3, self.ax4]:
            ax.clear()
            ax.grid(True, alpha=0.3)
        
        self.ax1.set_title('Temperatura de la CPU', fontsize=12, fontweight='bold')
        self.ax2.set_title('RPM del Ventilador', fontsize=12, fontweight='bold')
        self.ax3.set_title('Acciones del Control PID', fontsize=12, fontweight='bold')
        self.ax4.set_title('Señales del Sistema', fontsize=12, fontweight='bold')
        
        self.canvas.draw()
        self.actualizar_status("Gráficos limpiados", 'info')

    def toggle_panel_control(self):
        """Oculta o muestra el panel de control para maximizar los gráficos"""
        if self.control_frame.winfo_viewable():
            # Ocultar panel
            self.control_frame.pack_forget()
            self.btn_toggle_panel.configure(text="▶ Mostrar Panel")
            self.actualizar_status("Panel de control oculto - Gráficos maximizados", 'info')
        else:
            # Mostrar panel
            self.control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
            self.btn_toggle_panel.configure(text="◀ Ocultar Panel")
            self.actualizar_status("Panel de control visible", 'info')

    def maximizar_ventana(self):
        """Maximiza la ventana para aprovechar toda la pantalla"""
        self.root.state('zoomed')  # En Windows
        self.actualizar_status("Ventana maximizada", 'info')

    def restaurar_ventana(self):
        """Restaura la ventana a su tamaño normal"""
        self.root.state('normal')
        self.root.geometry("1600x1000")
        self.actualizar_status("Ventana restaurada", 'info')

    def nueva_configuracion(self):
        """Restablece la configuración a valores por defecto"""
        defaults = {
            'temp_ref': 65.0, 'temp_ambiente': 22.0, 'Kp': 15, 'Ki': 2, 'Kd': 0.01,
            'tiempo_scan': 0.5, 'total_time': 500.0, 'rpm_min': 600, 'rpm_max': 3000,
            'rpm_nominal': 1500, 'q_cpu': 1.0, 'coef_diss': 0.001
        }
        
        for key, value in defaults.items():
            self.params[key].set(value)
            
        pert_defaults = {'emi_inicio': 50.0, 'emi_duracion': 3.0, 'emi_magnitud': 500.0}
        for key, value in pert_defaults.items():
            self.perturbaciones[key].set(value)
            
        self.actualizar_status("Nueva configuración cargada", 'success')

    def guardar_configuracion(self):
        """Guarda la configuración actual en un archivo JSON"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Guardar Configuración"
        )
        
        if filename:
            config = {
                'params': {key: var.get() for key, var in self.params.items()},
                'perturbaciones': {key: var.get() for key, var in self.perturbaciones.items()},
                'timestamp': datetime.now().isoformat()
            }
            
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(config, f, indent=2, ensure_ascii=False)
                self.actualizar_status(f"Configuración guardada: {os.path.basename(filename)}", 'success')
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo guardar la configuración:\n{e}")

    def abrir_configuracion(self):
        """Abre una configuración desde un archivo JSON"""
        filename = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Abrir Configuración"
        )
        
        if filename:
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                
                # Cargar parámetros
                for key, value in config.get('params', {}).items():
                    if key in self.params:
                        self.params[key].set(value)
                
                for key, value in config.get('perturbaciones', {}).items():
                    if key in self.perturbaciones:
                        self.perturbaciones[key].set(value)
                
                self.actualizar_status(f"Configuración cargada: {os.path.basename(filename)}", 'success')
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo cargar la configuración:\n{e}")

    def exportar_datos(self):
        """Exporta los datos de la simulación a CSV"""
        if not self.datos_simulacion:
            messagebox.showwarning("Advertencia", "No hay datos de simulación para exportar")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            title="Exportar Datos"
        )
        
        if filename:
            try:
                datos = self.datos_simulacion
                with open(filename, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    
                    # Encabezados
                    writer.writerow(['Tiempo', 'Temperatura', 'RPM', 'Error', 'Accion_P', 
                                   'Accion_I', 'Control', 'Referencia', 'Perturbacion'])
                    
                    # Datos
                    for i in range(len(datos['t_values'])):
                        writer.writerow([
                            datos['t_values'][i],
                            datos['temps'][i],
                            datos['rpms'][i], 
                            datos['errores'][i],
                            datos['accion_p'][i],
                            datos['accion_i'][i],
                            datos['controles'][i],
                            datos['refs'][i],
                            datos['perturbaciones'][i]
                        ])
                
                self.actualizar_status(f"Datos exportados: {os.path.basename(filename)}", 'success')
            except Exception as e:
                messagebox.showerror("Error", f"No se pudieron exportar los datos:\n{e}")

    def guardar_graficos(self):
        """Guarda los gráficos actuales en un archivo de imagen"""
        if not self.datos_simulacion:
            messagebox.showwarning("Advertencia", "No hay gráficos para guardar. Ejecute una simulación primero.")
            return
        
        # Generar nombre por defecto con timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_name = f"simulacion_ventilador_{timestamp}.png"
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".png",
            initialfile=default_name,
            filetypes=[
                ("PNG files", "*.png"),
                ("PDF files", "*.pdf"),
                ("SVG files", "*.svg"),
                ("JPEG files", "*.jpg"),
                ("All files", "*.*")
            ],
            title="Guardar Gráficos"
        )
        
        if filename:
            try:
                # Guardar con alta calidad
                self.fig.savefig(filename, dpi=300, bbox_inches='tight', 
                               facecolor='white', edgecolor='none')
                self.actualizar_status(f"Gráficos guardados: {os.path.basename(filename)}", 'success')
            except Exception as e:
                messagebox.showerror("Error", f"No se pudieron guardar los gráficos:\n{e}")

    def mostrar_guia(self):
        """Muestra la guía de uso"""
        guia = """
🎯 GUÍA DE USO DEL SIMULADOR

📋 PASOS BÁSICOS:
1. Configurar parámetros del sistema en la pestaña "Sistema"
2. Ajustar perturbaciones EMI en "Perturbaciones" 
3. Ejecutar simulación desde "Control"
4. Analizar resultados en gráficos y estadísticas

🎛️ CONTROL PID:
• Kp: Respuesta proporcional al error actual
• Ki: Elimina error en estado estacionario
• Kd: Reduce oscilaciones y overshoot

⚙️ PRESETS:
• Conservador: Respuesta lenta pero estable
• Balanceado: Compromiso entre velocidad y estabilidad
• Agresivo: Respuesta rápida con posible overshoot
• Alta Performance: Máxima velocidad de respuesta

📊 ANÁLISIS:
• RMSE: Error cuadrático medio (menor es mejor)
• Overshoot: Sobrepaso máximo en %
• Settling time: Tiempo hasta estabilización

💾 ARCHIVOS:
• Guardar/Cargar configuraciones en JSON
• Exportar datos de simulación en CSV
• Gráficos se guardan automáticamente como PNG
"""
        
        ventana_guia = tk.Toplevel(self.root)
        ventana_guia.title("Guía de Uso")
        ventana_guia.geometry("600x500")
        
        text_widget = tk.Text(ventana_guia, wrap=tk.WORD, font=('Arial', 10))
        text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        text_widget.insert(tk.END, guia)
        text_widget.configure(state='disabled')

    def mostrar_acerca_de(self):
        """Muestra información sobre la aplicación"""
        info = """
🚀 SIMULADOR AVANZADO DE CONTROL PID
Versión 2.0 - Mejorado

👨‍💻 Desarrollado para el análisis y diseño de
sistemas de control de temperatura CPU

🔧 Características:
• Control PID con anti-windup
• Simulación de perturbaciones EMI/RFI
• Análisis estadístico automático
• Configuraciones predefinidas
• Exportación de datos y gráficos

📧 Contacto: tu-email@universidad.edu
🏫 Universidad Tecnológica Nacional
📅 2024
"""
        messagebox.showinfo("Acerca de", info)


def main():
    root = tk.Tk()
    app = SimuladorVentiladorCPUMejorado(root)
    root.mainloop()


if __name__ == "__main__":
    main() 