import numpy as np
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import ttk, messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.backends._backend_tk import NavigationToolbar2Tk
from matplotlib.figure import Figure
import random

class SimuladorVentiladorCPU:
    def __init__(self, root):
        self.root = root
        self.root.title("Simulador de Control de Velocidad del Ventilador CPU")
        self.root.geometry("1400x900")

        self.params = {
            'temp_ref': tk.DoubleVar(value=65.0),
            'temp_ambiente': tk.DoubleVar(value=22.0),
            'umbral_tolerancia': tk.DoubleVar(value=3),
            'Kp': tk.DoubleVar(value=15),
            'Ki': tk.DoubleVar(value=0),
            'Kd': tk.DoubleVar(value=0),
            'tiempo_scan': tk.DoubleVar(value=0.5),
            'total_time': tk.DoubleVar(value=500.0),
            'rpm_min': tk.DoubleVar(value=600),
            'rpm_max': tk.DoubleVar(value=3000),
            'rpm_nominal': tk.DoubleVar(value=1500),
            'q_cpu': tk.DoubleVar(value=1.0),
            # 'coef_diss': tk.DoubleVar(value=0.001),  # Fijo en 0.001
        }

        self.perturbaciones = {
            'emi_inicio': tk.DoubleVar(value=0),
            'emi_duracion': tk.DoubleVar(value=0),
            'emi_magnitud': tk.DoubleVar(value=0),
            'pert_carga_inicio': tk.DoubleVar(value=0),
            'pert_carga_duracion': tk.DoubleVar(value=0),
            'pert_carga_magnitud': tk.DoubleVar(value=0),
        }

        self.simulacion_activa = False
        self.datos_simulacion = None

        self.crear_interfaz()

    def crear_interfaz(self):
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        control_frame = ttk.Frame(main_frame)
        control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))

        self.plot_frame = ttk.Frame(main_frame)
        self.plot_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.crear_controles(control_frame)
        self.crear_graficos()

    def crear_controles(self, parent):
        notebook = ttk.Notebook(parent, width=400)
        notebook.pack(fill=tk.BOTH, expand=True)

        tab_sistema = ttk.Frame(notebook)
        notebook.add(tab_sistema, text="Sistema")

        for label, key in [
            ("Temperatura objetivo (°C):", 'temp_ref'),
            ("Temperatura ambiente (°C):", 'temp_ambiente'),
            ("Umbral de tolerancia (°C):", 'umbral_tolerancia'),
            ("Ganancia Proporcional (Kp):", 'Kp'),
            ("Ganancia Integral (Ki):", 'Ki'),
            ("Ganancia Derivativa (Kd):", 'Kd'),
            ("Tiempo de muestreo (s):", 'tiempo_scan'),
            ("Tiempo total (s):", 'total_time'),
            ("RPM mínimo:", 'rpm_min'),
            ("RPM máximo:", 'rpm_max'),
            ("RPM nominal:", 'rpm_nominal'),
            ("Generación de calor (°C/s):", 'q_cpu'),
            # ("Coef. disipación (°C/s/RPM):", 'coef_diss'),  # Fijo en 0.001
        ]:
            frame = ttk.Frame(tab_sistema)
            frame.pack(fill=tk.X, pady=2)
            ttk.Label(frame, text=label).pack(side=tk.LEFT)
            ttk.Entry(frame, textvariable=self.params[key], width=10).pack(side=tk.RIGHT)

        # Muevo el botón a la pestaña Sistema
        ttk.Button(tab_sistema, text="Ejecutar Simulación", command=self.ejecutar_simulacion).pack(pady=10)

        tab_pert = ttk.Frame(notebook)
        notebook.add(tab_pert, text="Perturbaciones EMI/RFI")

        for label, key in [
            ("Inicio de EMI (s):", 'emi_inicio'),
            ("Duración de EMI (s):", 'emi_duracion'),
            ("Magnitud EMI (RPM):", 'emi_magnitud'),
            ("Inicio perturbación de carga (s):", 'pert_carga_inicio'),
            ("Duración perturbación de carga (s):", 'pert_carga_duracion'),
            ("Magnitud perturbación de carga (°C/s):", 'pert_carga_magnitud'),
        ]:
            frame = ttk.Frame(tab_pert)
            frame.pack(fill=tk.X, pady=2)
            ttk.Label(frame, text=label).pack(side=tk.LEFT)
            ttk.Entry(frame, textvariable=self.perturbaciones[key], width=10).pack(side=tk.RIGHT)

        self.resultado_text = tk.Text(tab_sistema, height=10, width=45, font=('Courier', 9))
        self.resultado_text.pack(fill=tk.BOTH, expand=True)

    def crear_graficos(self):
        self.fig = Figure(figsize=(14, 12), dpi=100)
        
        # Usar GridSpec para dar más espacio al primer gráfico
        from matplotlib.gridspec import GridSpec
        gs = GridSpec(4, 1, height_ratios=[2, 1, 1, 1], hspace=0.25)
        
        self.ax1 = self.fig.add_subplot(gs[0])  # Gráfico 1 más grande (altura 2)
        self.ax2 = self.fig.add_subplot(gs[1])  # Gráfico 2 (altura 1)
        self.ax3 = self.fig.add_subplot(gs[2])  # Gráfico 3 (altura 1)
        self.ax4 = self.fig.add_subplot(gs[3])  # Gráfico 4 (altura 1)

        self.ax1.set_ylabel('Temp CPU (°C)')
        self.ax2.set_ylabel('Error (°C)')
        self.ax3.set_ylabel('Acción PI')
        self.ax4.set_ylabel('RPM Ventilador')
        self.ax4.set_xlabel('Tiempo (s)')

        self.canvas = FigureCanvasTkAgg(self.fig, self.plot_frame)
        self.fig.subplots_adjust(top=0.95)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        toolbar_frame = ttk.Frame(self.plot_frame)
        toolbar_frame.pack(fill=tk.X)
        NavigationToolbar2Tk(self.canvas, toolbar_frame)

    def log(self, mensaje):
        print(mensaje)
        self.resultado_text.insert(tk.END, mensaje + '\n')
        self.resultado_text.see(tk.END)

    def ejecutar_simulacion(self):
        try:
            self.resultado_text.delete(1.0, tk.END)

            #Parámetros
            temp_ref = self.params['temp_ref'].get()
            temp_ambiente = self.params['temp_ambiente'].get()
            umbral_tolerancia = self.params['umbral_tolerancia'].get()
            Kp = self.params['Kp'].get()
            Ki = self.params['Ki'].get()
            Kd = self.params['Kd'].get()
            dt = self.params['tiempo_scan'].get()
            T = self.params['total_time'].get()
            rpm_min = self.params['rpm_min'].get()
            rpm_max = self.params['rpm_max'].get()
            rpm = self.params['rpm_nominal'].get()
            q_cpu = self.params['q_cpu'].get() # °C/seg que genera la CPU
            # coef_diss = self.params['coef_diss'].get() # °C/s/RPM
            coef_diss = 0.001 # °C/s/RPM

            #Perturbaciones
            emi_ini = self.perturbaciones['emi_inicio'].get()
            emi_dur = self.perturbaciones['emi_duracion'].get()
            emi_mag = self.perturbaciones['emi_magnitud'].get()
            pert_carga_ini = self.perturbaciones['pert_carga_inicio'].get()
            pert_carga_dur = self.perturbaciones['pert_carga_duracion'].get()
            pert_carga_mag = self.perturbaciones['pert_carga_magnitud'].get()
            
            #Variables
            t_values = np.arange(0, T, dt)
            temp_cpu = temp_ambiente + 10 # °C
            p=0 # Acción Proporcional
            i=0 # Acción Integral
            d=0 # Acción Derivativa
            error_prev = 0 # Error previo (Para el derivativo)
            integral = 0
            ruido = 0

            temps = []
            rpms = []
            accion_p = []
            accion_i = []
            accion_d = []
            refs = []
            errores = []
            controles = []
            salida_actuador = []

            falla_detectada = False
            tipo_falla = None
            self.tiempo_fuera_control = 0  # Inicializar contador de tiempo fuera de control

            self.log(f"\n=== INICIO DE SIMULACIÓN ===")
            self.log(f"Temperatura objetivo: {temp_ref}°C")
            self.log(f"Temperatura inicial: {temp_cpu}°C")
            self.log(f"Ganancias: Kp={Kp}, Ki={Ki}, Kd={Kd}")
            self.log(f"RPM inicial: {rpm}")
            self.log(f"Generación de calor: {q_cpu}°C/s")
            self.log(f"Coef. disipación: {coef_diss}°C/s/RPM")
            self.log(f"Perturbación EMI: inicio={emi_ini}s, duración={emi_dur}s, magnitud={emi_mag}RPM")
            self.log(f"Perturbación de carga: inicio={pert_carga_ini}s, duración={pert_carga_dur}s, magnitud={pert_carga_mag}°C/s")
            self.log(f"Tiempo de muestreo: {dt}s, Tiempo total: {T}s")
            self.log(f"{'Tiempo':>8} {'Temp':>8} {'RPM':>8} {'Error':>8} {'Acción P':>10} {'Acción I':>10} {'Acción D':>10} {'EMI':>6} {'Pert. carga':>12}")
            self.log("-" * 80)

            for t in t_values:
                # 1. Calcular señal de error
                error = temp_ref - temp_cpu
                
                if abs(error) < umbral_tolerancia:
                    control = 0 # zona muerta - no aplicar control.
                else:
                    # 2. Proporcional
                    p = Kp * error

                    # 3. Derivativo
                    d = Kd * (error - error_prev) / dt

                    # 4. Integral
                    integral_candidate = integral + error * dt
                    i = Ki * integral_candidate

                    # 5. Salida final del controlador
                    control = -(p + i + d)

                """
                max_delta_rpm = 100   # 100–200 RPM por ciclo es un valor típico para un dt = 0.5 s.

                # Antes de aplicar el cambio de RPM, limitá la variación máxima:
                if control > max_delta_rpm:
                    control = max_delta_rpm
                elif control < -max_delta_rpm:
                    control = -max_delta_rpm
                """
                # 6. Guardá el error para el derivativo
                error_prev = error

                # 7. Control al Actuador.
                rpm += control

                # 8. Perturbación EMI - Afecta la salida del actuador.
                perturbacion_emi = 0
                emi_activa = emi_ini <= t <= emi_ini + emi_dur
                if emi_activa:
                    perturbacion_emi = -emi_mag
                    rpm += perturbacion_emi

                rpm = max(rpm_min, min(rpm_max, rpm))

                # 7. Ahora sí, ACTUALIZÁ la integral **sólo si el actuador NO está saturado en la dirección del error**
                if (rpm <= rpm_min and error > 0) or (rpm >= rpm_max and error < 0):
                    # No acumules, porque el control no puede actuar
                    pass
                else:
                    integral = integral_candidate
                    # Y podés seguir limitando el rango, por seguridad:
                    integral = max(min(integral, 50), -50)

                #ruido = random.uniform(-0.1, 0.1)  # ahora el ruido es de solo ±0.1 °C

                efecto_ventilador = coef_diss * rpm  # °C/seg que disipa el ventilador
                
                """
                Con inercia termica

                #coef_pasivo = 0.005
                #tau = 10
                #dtemp = (q_cpu - efecto_ventilador - (temp_cpu - temp_ambiente)/tau) * dt
                """

                # Cambio de temperatura
                q_cpu_efectivo = q_cpu
                carga_activa = pert_carga_ini <= t <= pert_carga_ini + pert_carga_dur
                if carga_activa:
                    q_cpu_efectivo += pert_carga_mag
                dtemp = (q_cpu_efectivo - efecto_ventilador) * dt
                temp_cpu += dtemp + ruido
                temp_cpu = max(temp_ambiente, temp_cpu)

                temps.append(temp_cpu)
                rpms.append(rpm)
                accion_p.append(p)
                accion_i.append(i)
                accion_d.append(d)
                refs.append(temp_ref)
                errores.append(error)
                controles.append(control)
                salida_actuador.append(rpm)  # Salida del actuador (RPM final)
                
                # Log cada 5 muestras para no saturar la consola
                emi_texto = "SÍ" if emi_activa else "NO"
                carga_texto = "SÍ" if carga_activa else "NO"
                if len(temps) % 5 == 0:  # Mostrar cada 5 muestras
                    print(f"{t:8.1f} {temp_cpu:8.2f} {rpm:8.0f} {error:8.2f} {p:10.2f} {i:10.2f} {d:10.2f} {emi_texto:>6} {carga_texto:>12}")

                # Detección de falla térmica (temperatura crítica)
                if temp_cpu >= 100.0:
                    falla_detectada = True
                    tipo_falla = "TÉRMICA"
                    break  # Detener la simulación inmediatamente
                
                # Detección de falla: solo cuando hay perturbaciones activas y el sistema no puede controlar
                hay_perturbacion_activa = emi_activa or carga_activa
                
                if t > 30 and hay_perturbacion_activa and abs(error) > max(umbral_tolerancia, 1) * 3:
                    self.tiempo_fuera_control += dt
                    if self.tiempo_fuera_control > 60:
                        falla_detectada = True
                        tipo_falla = "CONTROL"
                        break  # Detener la simulación inmediatamente
                else:
                    self.tiempo_fuera_control = 0

            # Determinar el momento de la falla
            if falla_detectada:
                idx_falla = len(errores) - 1
            else:
                idx_falla = None

            # Unificar longitud de todos los datos
            min_len = min(len(temps), len(errores), len(controles), len(rpms))
            t_real = t_values[:min_len]
            temps = temps[:min_len]
            errores = errores[:min_len]
            controles = controles[:min_len]
            rpms = rpms[:min_len]

            # Gráfico 1 - Salida del sistema (Temperatura)
            self.ax1.clear()
            self.ax1.axhspan(temp_ref - umbral_tolerancia, temp_ref + umbral_tolerancia, color='green', alpha=0.15, label='Umbral Tolerancia')
            self.ax1.plot(t_real, temps, label='Temp CPU')
            self.ax1.axhline(temp_ref, color='r', linestyle='--', label='Ref')
            self.ax1.axhline(100.0, color='darkred', linestyle=':', linewidth=2, alpha=0.8, label='Límite térmico')
            # Líneas de inicio y fin de perturbaciones (sin leyenda)
            self.ax1.axvline(emi_ini, color='red', linestyle='--', alpha=0.7, label='_nolegend_')
            self.ax1.axvline(emi_ini + emi_dur, color='purple', linestyle='--', alpha=0.7, label='_nolegend_')
            self.ax1.axvline(pert_carga_ini, color='orange', linestyle='--', alpha=0.7, label='_nolegend_')
            self.ax1.axvline(pert_carga_ini + pert_carga_dur, color='darkorange', linestyle='--', alpha=0.7, label='_nolegend_')
            
            # Áreas de perturbaciones (con leyenda)
            self.ax1.axvspan(emi_ini, emi_ini + emi_dur, color='red', alpha=0.1, label='Perturbación EMI')
            self.ax1.axvspan(pert_carga_ini, pert_carga_ini + pert_carga_dur, color='orange', alpha=0.15, label='Perturbación Carga')
            if falla_detectada and idx_falla is not None:
                tiempo_falla = t_real[idx_falla]
                self.ax1.axvline(tiempo_falla, color='red', linewidth=2, alpha=0.7, label='Falla del sistema')
            self.ax1.set_ylabel('Temp CPU (°C)')
            self.ax1.legend(fontsize=8)
            self.ax1.grid(True)
            self.ax1.set_xlim(0, T)

            # Gráfico 2 - Error (Temperatura deseada - temperatura real)
            self.ax2.clear()
            self.ax2.axhspan(-umbral_tolerancia, umbral_tolerancia, color='green', alpha=0.15, label='Umbral tolerancia')
            self.ax2.plot(t_real, errores, color='magenta', label='Error')
            self.ax2.axhline(0, color='black', linestyle='-', alpha=0.5)
            self.ax2.axvline(emi_ini, color='red', linestyle='--', alpha=0.7, label='_nolegend_')
            self.ax2.axvline(emi_ini + emi_dur, color='purple', linestyle='--', alpha=0.7, label='_nolegend_')
            self.ax2.axvline(pert_carga_ini, color='orange', linestyle='--', alpha=0.7, label='_nolegend_')
            self.ax2.axvline(pert_carga_ini + pert_carga_dur, color='darkorange', linestyle='--', alpha=0.7, label='_nolegend_')
            self.ax2.axvspan(emi_ini, emi_ini + emi_dur, color='red', alpha=0.1, label='_nolegend_')
            self.ax2.axvspan(pert_carga_ini, pert_carga_ini + pert_carga_dur, color='orange', alpha=0.15, label='_nolegend_')
            if falla_detectada and idx_falla is not None:
                tiempo_falla = t_real[idx_falla]
                self.ax2.axvline(tiempo_falla, color='red', linewidth=2, alpha=0.7, label='Falla del sistema')
            self.ax2.set_ylabel('Error (°C)')
            self.ax2.legend(fontsize=8)
            self.ax2.grid(True)
            self.ax2.set_xlim(0, T)

            """
            # Gráfico 3 - Acción del controlador (acción proporcional - integral)
            self.ax3.clear()
            if falla_detectada:
                self.ax3.plot(t_values[:idx_falla], accion_p[:idx_falla], color='orange', label='Acción Proporcional')
                self.ax3.plot(t_values[idx_falla:], accion_p[idx_falla:], color='darkred', label='Acción P durante Falla')
                self.ax3.plot(t_values[:idx_falla], accion_i[:idx_falla], color='green', label='Acción Integral')
                self.ax3.plot(t_values[idx_falla:], accion_i[idx_falla:], color='darkgreen', label='Acción I durante Falla')
                #self.ax3.plot(t_values[:idx_falla], accion_d[:idx_falla], color='blue', label='Acción Derivativa')
                #self.ax3.plot(t_values[idx_falla:], accion_d[idx_falla:], color='darkblue', label='Acción D durante Falla')
            else:
                self.ax3.plot(t_values, accion_p, color='orange', label='Acción Proporcional')
                self.ax3.plot(t_values, accion_i, color='green', label='Acción Integral')
                # self.ax3.plot(t_values, accion_d, color='blue', label='Acción Derivativa')
            self.ax3.axhline(0, color='black', linestyle='-', alpha=0.5)
            self.ax3.axvline(emi_ini, color='red', linestyle='--', alpha=0.7)
            self.ax3.axvline(emi_ini + emi_dur, color='purple', linestyle='--', alpha=0.7)
            self.ax3.axvspan(emi_ini, emi_ini + emi_dur, color='red', alpha=0.1)
            self.ax3.set_ylabel('Acción PI')
            self.ax3.legend()
            self.ax3.grid(True)
            """

            # Gráfico 3 - Acción del controlador (control final aplicado)
            self.ax3.clear()
            self.ax3.plot(t_real, controles, color='orange', label='Control')
            self.ax3.axhline(0, color='black', linestyle='-', alpha=0.5)
            self.ax3.axvline(emi_ini, color='red', linestyle='--', alpha=0.7, label='_nolegend_')
            self.ax3.axvline(emi_ini + emi_dur, color='purple', linestyle='--', alpha=0.7, label='_nolegend_')
            self.ax3.axvline(pert_carga_ini, color='orange', linestyle='--', alpha=0.7, label='_nolegend_')
            self.ax3.axvline(pert_carga_ini + pert_carga_dur, color='darkorange', linestyle='--', alpha=0.7, label='_nolegend_')
            self.ax3.axvspan(emi_ini, emi_ini + emi_dur, color='red', alpha=0.1, label='_nolegend_')
            self.ax3.axvspan(pert_carga_ini, pert_carga_ini + pert_carga_dur, color='orange', alpha=0.15, label='_nolegend_')
            if falla_detectada and idx_falla is not None:
                tiempo_falla = t_real[idx_falla]
                self.ax3.axvline(tiempo_falla, color='red', linewidth=2, alpha=0.7, label='Falla del sistema')
            self.ax3.set_ylabel('Control')
            self.ax3.legend(fontsize=8)
            self.ax3.grid(True)
            self.ax3.set_xlim(0, T)

            # Gráfico 4 - Acción del actuador (RPM del ventilador)
            self.ax4.clear()
            self.ax4.plot(t_real, rpms, label='RPM')
            self.ax4.axvline(emi_ini, color='red', linestyle='--', alpha=0.7, label='_nolegend_')
            self.ax4.axvline(emi_ini + emi_dur, color='purple', linestyle='--', alpha=0.7, label='_nolegend_')
            self.ax4.axvline(pert_carga_ini, color='orange', linestyle='--', alpha=0.7, label='_nolegend_')
            self.ax4.axvline(pert_carga_ini + pert_carga_dur, color='darkorange', linestyle='--', alpha=0.7, label='_nolegend_')
            self.ax4.axvspan(emi_ini, emi_ini + emi_dur, color='red', alpha=0.1, label='_nolegend_')
            self.ax4.axvspan(pert_carga_ini, pert_carga_ini + pert_carga_dur, color='orange', alpha=0.15, label='_nolegend_')
            if falla_detectada and idx_falla is not None:
                tiempo_falla = t_real[idx_falla]
                self.ax4.axvline(tiempo_falla, color='red', linewidth=2, alpha=0.7, label='Falla del sistema')
            self.ax4.set_ylabel('RPM Ventilador')
            self.ax4.set_xlabel('Tiempo (s)')
            self.ax4.legend(fontsize=8)
            self.ax4.grid(True)
            self.ax4.set_xlim(0, T)

            # Mostrar título general de falla si corresponde
            if falla_detectada:
                if tipo_falla == "TÉRMICA":
                    self.fig.suptitle('FALLA TÉRMICA - TEMPERATURA CRÍTICA', fontsize=22, color='darkred', weight='bold')
                else:
                    self.fig.suptitle('FALLA DEL SISTEMA', fontsize=22, color='red', weight='bold')
            else:
                self.fig.suptitle('')
                
            # Ajustar espacios y márgenes de la figura
            self.fig.subplots_adjust(hspace=0.25, top=0.95)

            self.canvas.draw()
            self.fig.savefig("simulacion_resultado.png")

            # Resumen final en consola
            self.log("-" * 70)
            self.log(f"=== RESUMEN DE SIMULACIÓN ===")
            self.log(f"Temperatura final: {temp_cpu:.2f}°C")
            self.log(f"RPM final: {rpm:.0f}")
            self.log(f"Error final: {temp_ref - temp_cpu:.2f}°C")
            self.log(f"Temperatura máxima alcanzada: {max(temps):.2f}°C")
            self.log(f"Temperatura mínima alcanzada: {min(temps):.2f}°C")
            self.log(f"RPM máximo alcanzado: {max(rpms):.0f}")
            self.log(f"RPM mínimo alcanzado: {min(rpms):.0f}")
            self.log(f"Generación de calor: {q_cpu}°C/s")
            self.log(f"Coef. disipación: {coef_diss}°C/s/RPM")
            if falla_detectada:
                if tipo_falla == "TÉRMICA":
                    self.log("¡FALLA TÉRMICA DETECTADA!")
                    self.log("La temperatura alcanzó el umbral crítico de 105°C")
                else:
                    self.log("¡FALLA DEL SISTEMA DETECTADA!")
                    self.log(f"El sistema estuvo fuera de control por {self.tiempo_fuera_control:.1f} segundos")
            else:
                self.log("SISTEMA FUNCIONANDO CORRECTAMENTE")
            self.log("=" * 30)

            self.resultado_text.insert(tk.END, f"Simulación completada con Kp={Kp}, Ki={Ki}\n")
            if falla_detectada:
                if tipo_falla == "TÉRMICA":
                    self.resultado_text.insert(tk.END, f"¡FALLA TÉRMICA! La temperatura alcanzó 105°C - RIESGO DE DAÑO PERMANENTE\n")
                else:
                    self.resultado_text.insert(tk.END, f"¡Falla del sistema detectada! El sistema estuvo fuera de control por {self.tiempo_fuera_control:.1f} segundos\n")
            else:
                self.resultado_text.insert(tk.END, "Sistema funcionando correctamente - todas las perturbaciones fueron controladas\n")

        except Exception as e:
            messagebox.showerror("Error", str(e))


def main():
    root = tk.Tk()
    app = SimuladorVentiladorCPU(root)
    root.mainloop()


if __name__ == "__main__":
    main()
