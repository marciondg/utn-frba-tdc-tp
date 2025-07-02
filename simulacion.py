import numpy as np
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import ttk, messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

class SimuladorVentiladorCPU:
    def __init__(self, root):
        self.root = root
        self.root.title("Simulador de Control de Velocidad del Ventilador CPU")
        self.root.geometry("1400x900")
        
        # Variables de control por defecto
        self.params = {
            'temp_ref': tk.DoubleVar(value=65.0),
            'temp_ambiente': tk.DoubleVar(value=22.0),
            'Kp': tk.DoubleVar(value=15.0),
            'Ki': tk.DoubleVar(value=2.0),
            'tiempo_scan': tk.DoubleVar(value=0.5),
            'total_time': tk.DoubleVar(value=150.0),
            'rpm_min': tk.DoubleVar(value=600),
            'rpm_max': tk.DoubleVar(value=3000),
            'rpm_nominal': tk.DoubleVar(value=1500),
        }
        
        # Variables de perturbaciones
        self.perturbaciones = {
            'pico_carga_inicio': tk.DoubleVar(value=45.0),
            'pico_carga_duracion': tk.DoubleVar(value=5.0),
            'pico_carga_magnitud': tk.DoubleVar(value=60.0),
            'temp_amb_inicio': tk.DoubleVar(value=70.0),
            'temp_amb_duracion': tk.DoubleVar(value=15.0),
            'temp_amb_magnitud': tk.DoubleVar(value=8.0),
            'obstruccion_inicio': tk.DoubleVar(value=100.0),
            'obstruccion_duracion': tk.DoubleVar(value=15.0),
            'obstruccion_eficiencia': tk.DoubleVar(value=0.7),
        }
        
        # Variables de simulación
        self.simulacion_activa = False
        self.datos_simulacion = None
        
        self.crear_interfaz()
        
    def crear_interfaz(self):
        # Frame principal
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Panel izquierdo - Controles
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        
        # Panel derecho - Gráficos
        self.plot_frame = ttk.Frame(main_frame)
        self.plot_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        self.crear_controles(control_frame)
        self.crear_graficos()
        
    def crear_controles(self, parent):
        # Notebook para organizar las pestañas
        notebook = ttk.Notebook(parent, width=400)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # Pestaña 1: Parámetros del sistema
        tab_sistema = ttk.Frame(notebook)
        notebook.add(tab_sistema, text="Sistema")
        
        # Parámetros del sistema
        ttk.Label(tab_sistema, text="PARÁMETROS DEL SISTEMA", font=('Arial', 10, 'bold')).pack(pady=5)
        
        # Temperatura objetivo
        frame_temp = ttk.Frame(tab_sistema)
        frame_temp.pack(fill=tk.X, pady=2)
        ttk.Label(frame_temp, text="Temperatura objetivo (°C):").pack(side=tk.LEFT)
        ttk.Entry(frame_temp, textvariable=self.params['temp_ref'], width=10).pack(side=tk.RIGHT)
        
        # Temperatura ambiente
        frame_amb = ttk.Frame(tab_sistema)
        frame_amb.pack(fill=tk.X, pady=2)
        ttk.Label(frame_amb, text="Temperatura ambiente (°C):").pack(side=tk.LEFT)
        ttk.Entry(frame_amb, textvariable=self.params['temp_ambiente'], width=10).pack(side=tk.RIGHT)
        
        # Controlador PI
        ttk.Separator(tab_sistema, orient='horizontal').pack(fill=tk.X, pady=10)
        ttk.Label(tab_sistema, text="CONTROLADOR PI", font=('Arial', 10, 'bold')).pack(pady=5)
        
        frame_kp = ttk.Frame(tab_sistema)
        frame_kp.pack(fill=tk.X, pady=2)
        ttk.Label(frame_kp, text="Ganancia Proporcional (Kp):").pack(side=tk.LEFT)
        ttk.Entry(frame_kp, textvariable=self.params['Kp'], width=10).pack(side=tk.RIGHT)
        
        frame_ki = ttk.Frame(tab_sistema)
        frame_ki.pack(fill=tk.X, pady=2)
        ttk.Label(frame_ki, text="Ganancia Integral (Ki):").pack(side=tk.LEFT)
        ttk.Entry(frame_ki, textvariable=self.params['Ki'], width=10).pack(side=tk.RIGHT)
        
        # Parámetros de simulación
        ttk.Separator(tab_sistema, orient='horizontal').pack(fill=tk.X, pady=10)
        ttk.Label(tab_sistema, text="SIMULACIÓN", font=('Arial', 10, 'bold')).pack(pady=5)
        
        frame_scan = ttk.Frame(tab_sistema)
        frame_scan.pack(fill=tk.X, pady=2)
        ttk.Label(frame_scan, text="Tiempo de muestreo (s):").pack(side=tk.LEFT)
        ttk.Entry(frame_scan, textvariable=self.params['tiempo_scan'], width=10).pack(side=tk.RIGHT)
        
        frame_time = ttk.Frame(tab_sistema)
        frame_time.pack(fill=tk.X, pady=2)
        ttk.Label(frame_time, text="Tiempo total (s):").pack(side=tk.LEFT)
        ttk.Entry(frame_time, textvariable=self.params['total_time'], width=10).pack(side=tk.RIGHT)
        
        # Parámetros del ventilador
        ttk.Separator(tab_sistema, orient='horizontal').pack(fill=tk.X, pady=10)
        ttk.Label(tab_sistema, text="VENTILADOR", font=('Arial', 10, 'bold')).pack(pady=5)
        
        frame_rpm_min = ttk.Frame(tab_sistema)
        frame_rpm_min.pack(fill=tk.X, pady=2)
        ttk.Label(frame_rpm_min, text="RPM mínimo:").pack(side=tk.LEFT)
        ttk.Entry(frame_rpm_min, textvariable=self.params['rpm_min'], width=10).pack(side=tk.RIGHT)
        
        frame_rpm_max = ttk.Frame(tab_sistema)
        frame_rpm_max.pack(fill=tk.X, pady=2)
        ttk.Label(frame_rpm_max, text="RPM máximo:").pack(side=tk.LEFT)
        ttk.Entry(frame_rpm_max, textvariable=self.params['rpm_max'], width=10).pack(side=tk.RIGHT)
        
        frame_rpm_nom = ttk.Frame(tab_sistema)
        frame_rpm_nom.pack(fill=tk.X, pady=2)
        ttk.Label(frame_rpm_nom, text="RPM nominal:").pack(side=tk.LEFT)
        ttk.Entry(frame_rpm_nom, textvariable=self.params['rpm_nominal'], width=10).pack(side=tk.RIGHT)
        
        # Pestaña 2: Perturbaciones
        tab_pert = ttk.Frame(notebook)
        notebook.add(tab_pert, text="Perturbaciones")
        
        # Pico de carga
        ttk.Label(tab_pert, text="PICO DE CARGA", font=('Arial', 10, 'bold')).pack(pady=5)
        
        frame_pc_inicio = ttk.Frame(tab_pert)
        frame_pc_inicio.pack(fill=tk.X, pady=2)
        ttk.Label(frame_pc_inicio, text="Tiempo de inicio (s):").pack(side=tk.LEFT)
        ttk.Entry(frame_pc_inicio, textvariable=self.perturbaciones['pico_carga_inicio'], width=10).pack(side=tk.RIGHT)
        
        frame_pc_dur = ttk.Frame(tab_pert)
        frame_pc_dur.pack(fill=tk.X, pady=2)
        ttk.Label(frame_pc_dur, text="Duración (s):").pack(side=tk.LEFT)
        ttk.Entry(frame_pc_dur, textvariable=self.perturbaciones['pico_carga_duracion'], width=10).pack(side=tk.RIGHT)
        
        frame_pc_mag = ttk.Frame(tab_pert)
        frame_pc_mag.pack(fill=tk.X, pady=2)
        ttk.Label(frame_pc_mag, text="Magnitud (%):").pack(side=tk.LEFT)
        ttk.Entry(frame_pc_mag, textvariable=self.perturbaciones['pico_carga_magnitud'], width=10).pack(side=tk.RIGHT)
        
        # Cambio temperatura ambiente
        ttk.Separator(tab_pert, orient='horizontal').pack(fill=tk.X, pady=10)
        ttk.Label(tab_pert, text="TEMPERATURA AMBIENTE", font=('Arial', 10, 'bold')).pack(pady=5)
        
        frame_ta_inicio = ttk.Frame(tab_pert)
        frame_ta_inicio.pack(fill=tk.X, pady=2)
        ttk.Label(frame_ta_inicio, text="Tiempo de inicio (s):").pack(side=tk.LEFT)
        ttk.Entry(frame_ta_inicio, textvariable=self.perturbaciones['temp_amb_inicio'], width=10).pack(side=tk.RIGHT)
        
        frame_ta_dur = ttk.Frame(tab_pert)
        frame_ta_dur.pack(fill=tk.X, pady=2)
        ttk.Label(frame_ta_dur, text="Duración (s):").pack(side=tk.LEFT)
        ttk.Entry(frame_ta_dur, textvariable=self.perturbaciones['temp_amb_duracion'], width=10).pack(side=tk.RIGHT)
        
        frame_ta_mag = ttk.Frame(tab_pert)
        frame_ta_mag.pack(fill=tk.X, pady=2)
        ttk.Label(frame_ta_mag, text="Incremento (°C):").pack(side=tk.LEFT)
        ttk.Entry(frame_ta_mag, textvariable=self.perturbaciones['temp_amb_magnitud'], width=10).pack(side=tk.RIGHT)
        
        # Obstrucción del flujo
        ttk.Separator(tab_pert, orient='horizontal').pack(fill=tk.X, pady=10)
        ttk.Label(tab_pert, text="OBSTRUCCIÓN DEL FLUJO", font=('Arial', 10, 'bold')).pack(pady=5)
        
        frame_ob_inicio = ttk.Frame(tab_pert)
        frame_ob_inicio.pack(fill=tk.X, pady=2)
        ttk.Label(frame_ob_inicio, text="Tiempo de inicio (s):").pack(side=tk.LEFT)
        ttk.Entry(frame_ob_inicio, textvariable=self.perturbaciones['obstruccion_inicio'], width=10).pack(side=tk.RIGHT)
        
        frame_ob_dur = ttk.Frame(tab_pert)
        frame_ob_dur.pack(fill=tk.X, pady=2)
        ttk.Label(frame_ob_dur, text="Duración (s):").pack(side=tk.LEFT)
        ttk.Entry(frame_ob_dur, textvariable=self.perturbaciones['obstruccion_duracion'], width=10).pack(side=tk.RIGHT)
        
        frame_ob_ef = ttk.Frame(tab_pert)
        frame_ob_ef.pack(fill=tk.X, pady=2)
        ttk.Label(frame_ob_ef, text="Eficiencia (0.0-1.0):").pack(side=tk.LEFT)
        ttk.Entry(frame_ob_ef, textvariable=self.perturbaciones['obstruccion_eficiencia'], width=10).pack(side=tk.RIGHT)
        
        # Pestaña 3: Control y resultados
        tab_control = ttk.Frame(notebook)
        notebook.add(tab_control, text="Control")
        
        # Botones de control
        ttk.Label(tab_control, text="CONTROL DE SIMULACIÓN", font=('Arial', 10, 'bold')).pack(pady=5)
        
        btn_frame = ttk.Frame(tab_control)
        btn_frame.pack(pady=10)
        
        self.btn_simular = ttk.Button(btn_frame, text="Ejecutar Simulación", 
                                     command=self.ejecutar_simulacion, width=20)
        self.btn_simular.pack(pady=5)
        
        ttk.Button(btn_frame, text="Limpiar Gráficos", 
                  command=self.limpiar_graficos, width=20).pack(pady=5)
        
        ttk.Button(btn_frame, text="Exportar Datos", 
                  command=self.exportar_datos, width=20).pack(pady=5)
        
        # Área de resultados
        ttk.Separator(tab_control, orient='horizontal').pack(fill=tk.X, pady=10)
        ttk.Label(tab_control, text="MÉTRICAS DE DESEMPEÑO", font=('Arial', 10, 'bold')).pack(pady=5)
        
        self.resultado_text = tk.Text(tab_control, height=15, width=45, font=('Courier', 9))
        self.resultado_text.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(tab_control, orient="vertical", command=self.resultado_text.yview)
        scrollbar.pack(side="right", fill="y")
        self.resultado_text.configure(yscrollcommand=scrollbar.set)
        
    def crear_graficos(self):
        # Crear figura matplotlib
        self.fig = Figure(figsize=(10, 8), dpi=100)
        
        # Crear subplots
        self.ax1 = self.fig.add_subplot(4, 1, 1)
        self.ax2 = self.fig.add_subplot(4, 1, 2)
        self.ax3 = self.fig.add_subplot(4, 1, 3)
        self.ax4 = self.fig.add_subplot(4, 1, 4)
        
        # Configurar ejes
        self.ax1.set_ylabel('Temperatura (°C)')
        self.ax1.set_title('Sistema de Control de Velocidad del Ventilador CPU')
        self.ax1.grid(True, alpha=0.3)
        
        self.ax2.set_ylabel('Velocidad (RPM)')
        self.ax2.grid(True, alpha=0.3)
        
        self.ax3.set_ylabel('Duty Cycle (%)')
        self.ax3.grid(True, alpha=0.3)
        
        self.ax4.set_ylabel('Carga CPU (%)')
        self.ax4.set_xlabel('Tiempo (s)')
        self.ax4.grid(True, alpha=0.3)
        
        self.fig.tight_layout()
        
        # Integrar con tkinter
        self.canvas = FigureCanvasTkAgg(self.fig, self.plot_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
    def generar_carga_cpu(self, t):
        """Genera perfil de carga del CPU a lo largo del tiempo"""
        if t < 20:
            return 15 + 5 * np.sin(0.1 * t)
        elif t < 40:
            return 45 + 10 * np.sin(0.2 * t)
        elif t < 60:
            return 75 + 10 * np.sin(0.15 * t)
        elif t < 80:
            return 30 + 15 * np.sin(0.3 * t)
        else:
            return 20 + 25 * np.sin(0.1 * t)
            
    def aplicar_perturbaciones(self, t):
        """Define perturbaciones específicas del sistema"""
        perturbaciones = {}
        
        # Pico de carga abrupta
        inicio_carga = self.perturbaciones['pico_carga_inicio'].get()
        fin_carga = inicio_carga + self.perturbaciones['pico_carga_duracion'].get()
        if inicio_carga <= t <= fin_carga:
            perturbaciones['carga_extra'] = self.perturbaciones['pico_carga_magnitud'].get()
        
        # Cambio de temperatura ambiente
        inicio_temp = self.perturbaciones['temp_amb_inicio'].get()
        fin_temp = inicio_temp + self.perturbaciones['temp_amb_duracion'].get()
        if inicio_temp <= t <= fin_temp:
            perturbaciones['temp_ambiente_extra'] = self.perturbaciones['temp_amb_magnitud'].get()
        
        # Obstrucción parcial del flujo de aire
        inicio_obs = self.perturbaciones['obstruccion_inicio'].get()
        fin_obs = inicio_obs + self.perturbaciones['obstruccion_duracion'].get()
        if inicio_obs <= t <= fin_obs:
            perturbaciones['eficiencia_reducida'] = self.perturbaciones['obstruccion_eficiencia'].get()
        
        return perturbaciones
        
    def calcular_temp_cpu(self, carga_cpu, temp_ambiente_actual, rpm_ventilador, eficiencia_disipacion=1.0):
        """Calcula la temperatura del CPU basada en la carga y condiciones"""
        factor_carga = (carga_cpu / 100) * 45
        factor_ventilador = max(0, (rpm_ventilador - self.params['rpm_min'].get()) / 
                               (self.params['rpm_max'].get() - self.params['rpm_min'].get()))
        reduccion_temp = factor_ventilador * 15 * eficiencia_disipacion
        
        temp_calculada = temp_ambiente_actual + factor_carga - reduccion_temp
        return max(35.0, temp_calculada)
        
    def rpm_to_duty_cycle(self, rpm):
        """Convierte RPM a duty cycle PWM"""
        rpm_min = self.params['rpm_min'].get()
        rpm_max = self.params['rpm_max'].get()
        
        if rpm <= rpm_min:
            return 20
        elif rpm >= rpm_max:
            return 100
        else:
            return 20 + (rpm - rpm_min) * 80 / (rpm_max - rpm_min)
            
    def ejecutar_simulacion(self):
        try:
            self.btn_simular.config(state='disabled', text='Ejecutando...')
            self.root.update()
            
            # Obtener parámetros
            temp_ref = self.params['temp_ref'].get()
            temp_ambiente = self.params['temp_ambiente'].get()
            Kp = self.params['Kp'].get()
            Ki = self.params['Ki'].get()
            tiempo_scan = self.params['tiempo_scan'].get()
            total_time = self.params['total_time'].get()
            rpm_min = self.params['rpm_min'].get()
            rpm_max = self.params['rpm_max'].get()
            rpm_nominal = self.params['rpm_nominal'].get()
            
            # Variables de simulación
            temp_cpu = temp_ambiente + 13
            integral_error = 0.0
            rpm_ventilador = rpm_nominal
            
            # Arrays para almacenar datos
            tiempos = []
            temperaturas_cpu = []
            rpms_ventilador = []
            duty_cycles = []
            errores_temp = []
            cargas_cpu = []
            temps_ambiente = []
            
            # Simulación principal
            for t_idx in range(int(total_time / tiempo_scan)):
                t = t_idx * tiempo_scan
                
                # Generar carga del CPU
                carga_cpu_base = self.generar_carga_cpu(t)
                
                # Aplicar perturbaciones
                perturbaciones = self.aplicar_perturbaciones(t)
                carga_cpu_actual = carga_cpu_base + perturbaciones.get('carga_extra', 0)
                temp_ambiente_actual = temp_ambiente + perturbaciones.get('temp_ambiente_extra', 0)
                eficiencia_disipacion = perturbaciones.get('eficiencia_reducida', 1.0)
                
                # Calcular temperatura del CPU
                temp_cpu = self.calcular_temp_cpu(carga_cpu_actual, temp_ambiente_actual, 
                                                rpm_ventilador, eficiencia_disipacion)
                
                # Calcular error de temperatura
                error_temp = temp_cpu - temp_ref
                
                # Controlador PI
                accion_proporcional = Kp * error_temp
                
                integral_error += error_temp * tiempo_scan
                # Anti-windup
                integral_error = max(-1000, min(1000, integral_error))
                accion_integral = Ki * integral_error
                
                # Señal de control total
                control_signal = accion_proporcional + accion_integral
                
                # Calcular nuevo RPM del ventilador
                nuevo_rpm = rpm_ventilador + control_signal
                rpm_ventilador = max(rpm_min, min(rpm_max, nuevo_rpm))
                
                # Convertir a duty cycle
                duty_cycle = self.rpm_to_duty_cycle(rpm_ventilador)
                
                # Almacenar datos
                tiempos.append(t)
                temperaturas_cpu.append(temp_cpu)
                rpms_ventilador.append(rpm_ventilador)
                duty_cycles.append(duty_cycle)
                errores_temp.append(error_temp)
                cargas_cpu.append(carga_cpu_actual)
                temps_ambiente.append(temp_ambiente_actual)
            
            # Guardar datos para exportación
            self.datos_simulacion = {
                'tiempos': tiempos,
                'temperaturas_cpu': temperaturas_cpu,
                'rpms_ventilador': rpms_ventilador,
                'duty_cycles': duty_cycles,
                'errores_temp': errores_temp,
                'cargas_cpu': cargas_cpu,
                'temps_ambiente': temps_ambiente
            }
            
            # Actualizar gráficos
            self.actualizar_graficos()
            
            # Calcular y mostrar métricas
            self.calcular_metricas()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error en la simulación: {str(e)}")
        finally:
            self.btn_simular.config(state='normal', text='Ejecutar Simulación')
            
    def actualizar_graficos(self):
        if self.datos_simulacion is None:
            return
            
        # Limpiar gráficos
        self.ax1.clear()
        self.ax2.clear()
        self.ax3.clear()
        self.ax4.clear()
        
        datos = self.datos_simulacion
        temp_ref = self.params['temp_ref'].get()
        rpm_min = self.params['rpm_min'].get()
        rpm_max = self.params['rpm_max'].get()
        rpm_nominal = self.params['rpm_nominal'].get()
        
        # Gráfico 1: Temperatura
        self.ax1.plot(datos['tiempos'], datos['temperaturas_cpu'], 'b-', linewidth=2, label='Temperatura CPU')
        self.ax1.axhline(y=temp_ref, color='r', linestyle='--', linewidth=2, label=f'Referencia ({temp_ref}°C)')
        self.ax1.axhline(y=temp_ref + 3, color='g', linestyle=':', alpha=0.7, label='Zona Normal (±3°C)')
        self.ax1.axhline(y=temp_ref - 3, color='g', linestyle=':', alpha=0.7)
        self.ax1.axhline(y=80, color='orange', linestyle='--', alpha=0.7, label='Zona Crítica (80°C)')
        self.ax1.set_ylabel('Temperatura (°C)')
        self.ax1.set_title('Sistema de Control de Velocidad del Ventilador CPU')
        self.ax1.legend()
        self.ax1.grid(True, alpha=0.3)
        
        # Gráfico 2: RPM
        self.ax2.plot(datos['tiempos'], datos['rpms_ventilador'], 'g-', linewidth=2, label='Velocidad Ventilador')
        self.ax2.axhline(y=rpm_nominal, color='orange', linestyle='--', alpha=0.7, label=f'Nominal ({rpm_nominal} RPM)')
        self.ax2.axhline(y=rpm_max, color='red', linestyle='--', alpha=0.7, label=f'Máximo ({rpm_max} RPM)')
        self.ax2.axhline(y=rpm_min, color='blue', linestyle='--', alpha=0.7, label=f'Mínimo ({rpm_min} RPM)')
        self.ax2.set_ylabel('Velocidad (RPM)')
        self.ax2.legend()
        self.ax2.grid(True, alpha=0.3)
        
        # Gráfico 3: Duty Cycle
        self.ax3.plot(datos['tiempos'], datos['duty_cycles'], 'm-', linewidth=2, label='Duty Cycle PWM')
        self.ax3.axhline(y=50, color='orange', linestyle='--', alpha=0.7, label='50% (Nominal)')
        self.ax3.set_ylabel('Duty Cycle (%)')
        self.ax3.legend()
        self.ax3.grid(True, alpha=0.3)
        
        # Gráfico 4: Carga CPU
        self.ax4.plot(datos['tiempos'], datos['cargas_cpu'], 'c-', linewidth=2, label='Carga CPU')
        self.ax4.plot(datos['tiempos'], datos['temps_ambiente'], 'y-', linewidth=1, alpha=0.7, label='Temp. Ambiente')
        self.ax4.set_ylabel('Carga CPU (%) / Temp. Amb. (°C)')
        self.ax4.set_xlabel('Tiempo (s)')
        self.ax4.legend()
        self.ax4.grid(True, alpha=0.3)
        
        self.fig.tight_layout()
        self.canvas.draw()
        
    def calcular_metricas(self):
        if self.datos_simulacion is None:
            return
            
        datos = self.datos_simulacion
        
        # Métricas de desempeño
        temp_promedio = np.mean(datos['temperaturas_cpu'])
        temp_max_sim = np.max(datos['temperaturas_cpu'])
        temp_min_sim = np.min(datos['temperaturas_cpu'])
        error_promedio = np.mean(np.abs(datos['errores_temp']))
        error_max = np.max(np.abs(datos['errores_temp']))
        
        # Tiempo en zona crítica
        tiempo_scan = self.params['tiempo_scan'].get()
        total_time = self.params['total_time'].get()
        tiempo_critico = sum(1 for temp in datos['temperaturas_cpu'] if temp > 80.0) * tiempo_scan
        porcentaje_critico = (tiempo_critico / total_time) * 100
        
        # RMSE
        rmse = np.sqrt(np.mean(np.array(datos['errores_temp'])**2))
        
        # Mostrar resultados
        resultados = f"""ANÁLISIS DE RESULTADOS
{'='*40}

Métricas de Temperatura:
  • Promedio: {temp_promedio:.2f}°C
  • Máxima: {temp_max_sim:.2f}°C
  • Mínima: {temp_min_sim:.2f}°C

Métricas de Error:
  • Error promedio: {error_promedio:.2f}°C
  • Error máximo: {error_max:.2f}°C
  • RMSE: {rmse:.2f}°C

Tiempo en zona crítica (>80°C):
  • Tiempo: {tiempo_critico:.1f}s
  • Porcentaje: {porcentaje_critico:.1f}%

Parámetros del Controlador:
  • Kp: {self.params['Kp'].get():.2f} RPM/°C
  • Ki: {self.params['Ki'].get():.2f} RPM/(°C·s)
  • Tiempo de muestreo: {self.params['tiempo_scan'].get():.2f}s

Estado del Sistema:
  • {'ESTABLE' if error_max < 10 else 'INESTABLE'}
  • {'ÓPTIMO' if porcentaje_critico < 5 else 'REQUIERE AJUSTE'}
"""
        
        self.resultado_text.delete(1.0, tk.END)
        self.resultado_text.insert(1.0, resultados)
        
    def limpiar_graficos(self):
        self.ax1.clear()
        self.ax2.clear()
        self.ax3.clear()
        self.ax4.clear()
        
        # Reconfigurar ejes
        self.ax1.set_ylabel('Temperatura (°C)')
        self.ax1.set_title('Sistema de Control de Velocidad del Ventilador CPU')
        self.ax1.grid(True, alpha=0.3)
        
        self.ax2.set_ylabel('Velocidad (RPM)')
        self.ax2.grid(True, alpha=0.3)
        
        self.ax3.set_ylabel('Duty Cycle (%)')
        self.ax3.grid(True, alpha=0.3)
        
        self.ax4.set_ylabel('Carga CPU (%)')
        self.ax4.set_xlabel('Tiempo (s)')
        self.ax4.grid(True, alpha=0.3)
        
        self.fig.tight_layout()
        self.canvas.draw()
        
        # Limpiar resultados
        self.resultado_text.delete(1.0, tk.END)
        self.datos_simulacion = None
        
    def exportar_datos(self):
        if self.datos_simulacion is None:
            messagebox.showwarning("Advertencia", "No hay datos para exportar. Ejecute una simulación primero.")
            return
            
        try:
            from tkinter import filedialog
            import csv
            
            # Abrir diálogo para guardar archivo
            filename = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                title="Guardar datos de simulación"
            )
            
            if filename:
                with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                    writer = csv.writer(csvfile)
                    
                    # Escribir encabezados
                    headers = ['Tiempo(s)', 'Temp_CPU(°C)', 'RPM_Ventilador', 'Duty_Cycle(%)', 
                              'Error_Temp(°C)', 'Carga_CPU(%)', 'Temp_Ambiente(°C)']
                    writer.writerow(headers)
                    
                    # Escribir datos
                    datos = self.datos_simulacion
                    for i in range(len(datos['tiempos'])):
                        row = [
                            datos['tiempos'][i],
                            datos['temperaturas_cpu'][i],
                            datos['rpms_ventilador'][i],
                            datos['duty_cycles'][i],
                            datos['errores_temp'][i],
                            datos['cargas_cpu'][i],
                            datos['temps_ambiente'][i]
                        ]
                        writer.writerow(row)
                
                messagebox.showinfo("Éxito", f"Datos exportados exitosamente a:\n{filename}")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al exportar datos: {str(e)}")
            
    def validar_parametros(self):
        """Valida que los parámetros ingresados sean correctos"""
        try:
            # Validar rangos de temperatura
            if self.params['temp_ref'].get() < 30 or self.params['temp_ref'].get() > 90:
                raise ValueError("La temperatura objetivo debe estar entre 30°C y 90°C")
                
            if self.params['temp_ambiente'].get() < 15 or self.params['temp_ambiente'].get() > 40:
                raise ValueError("La temperatura ambiente debe estar entre 15°C y 40°C")
                
            # Validar controlador PI
            if self.params['Kp'].get() <= 0:
                raise ValueError("Kp debe ser mayor que 0")
                
            if self.params['Ki'].get() < 0:
                raise ValueError("Ki debe ser mayor o igual que 0")
                
            # Validar parámetros de simulación
            if self.params['tiempo_scan'].get() <= 0 or self.params['tiempo_scan'].get() > 5:
                raise ValueError("El tiempo de muestreo debe estar entre 0.1s y 5s")
                
            if self.params['total_time'].get() <= 0:
                raise ValueError("El tiempo total debe ser mayor que 0")
                
            # Validar RPM
            if self.params['rpm_min'].get() >= self.params['rpm_max'].get():
                raise ValueError("RPM mínimo debe ser menor que RPM máximo")
                
            if self.params['rpm_nominal'].get() < self.params['rpm_min'].get() or \
               self.params['rpm_nominal'].get() > self.params['rpm_max'].get():
                raise ValueError("RPM nominal debe estar entre RPM mínimo y máximo")
                
            return True
            
        except ValueError as e:
            messagebox.showerror("Error de Validación", str(e))
            return False
            
    def cargar_configuracion_predeterminada(self):
        """Carga una configuración predeterminada"""
        # Configuración conservadora
        self.params['temp_ref'].set(65.0)
        self.params['temp_ambiente'].set(22.0)
        self.params['Kp'].set(15.0)
        self.params['Ki'].set(2.0)
        self.params['tiempo_scan'].set(0.5)
        self.params['total_time'].set(150.0)
        self.params['rpm_min'].set(600)
        self.params['rpm_max'].set(3000)
        self.params['rpm_nominal'].set(1500)
        
        # Perturbaciones por defecto
        self.perturbaciones['pico_carga_inicio'].set(45.0)
        self.perturbaciones['pico_carga_duracion'].set(5.0)
        self.perturbaciones['pico_carga_magnitud'].set(60.0)
        self.perturbaciones['temp_amb_inicio'].set(70.0)
        self.perturbaciones['temp_amb_duracion'].set(15.0)
        self.perturbaciones['temp_amb_magnitud'].set(8.0)
        self.perturbaciones['obstruccion_inicio'].set(100.0)
        self.perturbaciones['obstruccion_duracion'].set(15.0)
        self.perturbaciones['obstruccion_eficiencia'].set(0.7)


def main():
    root = tk.Tk()
    app = SimuladorVentiladorCPU(root)
    
    # Agregar menú
    menubar = tk.Menu(root)
    root.config(menu=menubar)
    
    # Menú Archivo
    archivo_menu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label="Archivo", menu=archivo_menu)
    archivo_menu.add_command(label="Exportar Datos", command=app.exportar_datos)
    archivo_menu.add_separator()
    archivo_menu.add_command(label="Salir", command=root.quit)
    
    # Menú Configuración
    config_menu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label="Configuración", menu=config_menu)
    config_menu.add_command(label="Cargar Configuración Predeterminada", 
                           command=app.cargar_configuracion_predeterminada)
    
    # Menú Ayuda
    ayuda_menu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label="Ayuda", menu=ayuda_menu)
    ayuda_menu.add_command(label="Acerca de", command=lambda: messagebox.showinfo(
        "Acerca de", 
        "Simulador de Control de Velocidad del Ventilador CPU\n\n" +
        "Trabajo Práctico - Teoría del Control\n" +
        "UTN FRBA - Ingeniería en Sistemas\n" +
        "Año 2025\n\n" +
        "Sistema de control PI en lazo cerrado para\n" +
        "regulación automática de temperatura del CPU"
    ))
    
    root.mainloop()


if __name__ == "__main__":
    main()