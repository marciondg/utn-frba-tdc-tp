import numpy as np
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import ttk, messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
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
            ("Ganancia Proporcional (Kp):", 'Kp'),
            ("Ganancia Integral (Ki):", 'Ki'),
            #("Ganancia Derivativa (Kd):", 'Kd'),
            ("Tiempo de muestreo (s):", 'tiempo_scan'),
            ("Tiempo total (s):", 'total_time'),
            ("RPM mínimo:", 'rpm_min'),
            ("RPM máximo:", 'rpm_max'),
            ("RPM nominal:", 'rpm_nominal'),
            ("Generación de calor (°C/s):", 'q_cpu'),
            ("Coef. disipación (°C/s/RPM):", 'coef_diss'),
        ]:
            frame = ttk.Frame(tab_sistema)
            frame.pack(fill=tk.X, pady=2)
            ttk.Label(frame, text=label).pack(side=tk.LEFT)
            ttk.Entry(frame, textvariable=self.params[key], width=10).pack(side=tk.RIGHT)

        tab_pert = ttk.Frame(notebook)
        notebook.add(tab_pert, text="Perturbaciones EMI/RFI")

        for label, key in [
            ("Inicio de EMI (s):", 'emi_inicio'),
            ("Duración de EMI (s):", 'emi_duracion'),
            ("Magnitud EMI (RPM):", 'emi_magnitud'),
        ]:
            frame = ttk.Frame(tab_pert)
            frame.pack(fill=tk.X, pady=2)
            ttk.Label(frame, text=label).pack(side=tk.LEFT)
            ttk.Entry(frame, textvariable=self.perturbaciones[key], width=10).pack(side=tk.RIGHT)

        tab_control = ttk.Frame(notebook)
        notebook.add(tab_control, text="Control")

        ttk.Button(tab_control, text="Ejecutar Simulación", command=self.ejecutar_simulacion).pack(pady=10)

        self.resultado_text = tk.Text(tab_control, height=10, width=45, font=('Courier', 9))
        self.resultado_text.pack(fill=tk.BOTH, expand=True)

    def crear_graficos(self):
        self.fig = Figure(figsize=(12, 9), dpi=100)
        self.ax1 = self.fig.add_subplot(3, 1, 1)
        self.ax2 = self.fig.add_subplot(3, 1, 2)
        self.ax3 = self.fig.add_subplot(3, 1, 3)

        self.ax1.set_ylabel('Temp CPU (°C)')
        self.ax2.set_ylabel('RPM Ventilador')
        self.ax3.set_ylabel('Acción PI')
        self.ax3.set_xlabel('Tiempo (s)')

        self.canvas = FigureCanvasTkAgg(self.fig, self.plot_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        toolbar_frame = ttk.Frame(self.plot_frame)
        toolbar_frame.pack(fill=tk.X)
        NavigationToolbar2Tk(self.canvas, toolbar_frame)

    def ejecutar_simulacion(self):
        try:
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

            q_cpu = self.params['q_cpu'].get() # °C/seg que genera la CPU
            coef_diss = self.params['coef_diss'].get()

            emi_ini = self.perturbaciones['emi_inicio'].get()
            emi_dur = self.perturbaciones['emi_duracion'].get()
            emi_mag = self.perturbaciones['emi_magnitud'].get()

            t_values = np.arange(0, T, dt)
            temp_cpu = temp_ambiente + 10
            integral = 0
            error_prev = 0

            temps = []
            rpms = []
            accion_p = []
            accion_i = []
            #accion_d = []
            falla_detectada = False

            print(f"\n=== INICIO DE SIMULACIÓN ===")
            print(f"Temperatura objetivo: {temp_ref}°C")
            print(f"Temperatura inicial: {temp_cpu}°C")
            print(f"Ganancias: Kp={Kp}, Ki={Ki}, Kd={Kd}")
            print(f"RPM inicial: {rpm}")
            print(f"Generación de calor: {q_cpu}°C/s")
            print(f"Coef. disipación: {coef_diss}°C/s/RPM")
            print(f"Perturbación EMI: inicio={emi_ini}s, duración={emi_dur}s, magnitud={emi_mag}RPM")
            print(f"Tiempo de muestreo: {dt}s, Tiempo total: {T}s")
            print(f"{'Tiempo':>8} {'Temp':>8} {'RPM':>8} {'Error':>8} {'Acción P':>10} {'Acción I':>10} {'Acción D':>10} {'EMI':>6}")
            print("-" * 80)

            for t in t_values:
                """
                error = temp_ref - temp_cpu
                # Control Proporcional
                p = Kp * error

                # Control Integral
                integral += error * dt
                integral = max(min(integral, 300), -300) # Anti-windup: limitar la integral
                i = Ki * integral

                # Control Derivativo
                d = Kd * (error - error_prev) / dt
                control = -(p + i + d)

                rpm += control
                error_prev = error

                if emi_ini <= t <= emi_ini + emi_dur:
                    rpm -= emi_mag

                rpm = max(rpm_min, min(rpm_max, rpm))
                """
                # 1. Calculá el error
                error = temp_ref - temp_cpu
                
                if abs(error) < 3:
                    control = 0 # zona muerta
                else:
                    # 2. Calculá términos P, I, D (pero NO sumes todavía la integral)
                    p = Kp * error
                    d = Kd * (error - error_prev) / dt

                    # 3. Calculá la acción integral "candidata"
                    integral_candidate = integral + error * dt
                    i = Ki * integral_candidate
                    # 4. Calculá la salida total de control
                    control = -(p + i)

                max_delta_rpm = 100   # 100–200 RPM por ciclo es un valor típico para un dt = 0.5 s.

                # Antes de aplicar el cambio de RPM, limitá la variación máxima:
                if control > max_delta_rpm:
                    control = max_delta_rpm
                elif control < -max_delta_rpm:
                    control = -max_delta_rpm

                # 5. Aplicá el control a RPM y hacé el clamp
                rpm += control

                # 6. Perturbación EMI
                if emi_ini <= t <= emi_ini + emi_dur:
                    rpm -= emi_mag

                rpm = max(rpm_min, min(rpm_max, rpm))

                # 7. Ahora sí, ACTUALIZÁ la integral **sólo si el actuador NO está saturado en la dirección del error**
                if (rpm <= rpm_min and error > 0) or (rpm >= rpm_max and error < 0):
                    # No acumules, porque el control no puede actuar
                    pass
                else:
                    integral = integral_candidate
                    # Y podés seguir limitando el rango, por seguridad:
                    integral = max(min(integral, 300), -300)

                # 7. Guardá el error para el derivativo
                #error_prev = error

                ruido = random.uniform(-0.1, 0.1)  # ahora el ruido es de solo ±0.1 °C

                efecto_ventilador = coef_diss * rpm  # °C/seg que disipa el ventilador
                
                #coef_pasivo = 0.005
                #tau = 10
                # Cambio de temperatura
                dtemp = (q_cpu - efecto_ventilador) * dt
                #dtemp = (q_cpu - efecto_ventilador - (temp_cpu - temp_ambiente)/tau) * dt
                temp_cpu += dtemp + ruido
                temp_cpu = max(temp_ambiente, temp_cpu)

                temps.append(temp_cpu)
                rpms.append(rpm)
                accion_p.append(p)
                accion_i.append(i)
                #accion_d.append(d)

                # Log cada 5 muestras para no saturar la consola
                emi_activa = emi_ini <= t <= emi_ini + emi_dur
                emi_texto = "SÍ" if emi_activa else "NO"
                if len(temps) % 5 == 0:  # Mostrar cada 5 muestras
                    print(f"{t:8.1f} {temp_cpu:8.2f} {rpm:8.0f} {error:8.2f} {p:10.2f} {i:10.2f} {d:10.2f} {emi_texto:>6}")

                if (emi_dur / T > 0.5) and abs(temp_ref - temp_cpu) > 20:
                    falla_detectada = True

            idx_falla = np.where(t_values >= emi_ini)[0][0] if falla_detectada else None

            # Gráfico 1 - Temperatura
            self.ax1.clear()
            if falla_detectada:
                self.ax1.plot(t_values[:idx_falla], temps[:idx_falla], label='Temp CPU')
                self.ax1.plot(t_values[idx_falla:], temps[idx_falla:], color='red', label='Temp durante Falla')
                self.ax1.text(0.5, 0.85, 'FALLA DEL SISTEMA', transform=self.ax1.transAxes,
                              fontsize=16, color='red', ha='center')
            else:
                self.ax1.plot(t_values, temps, label='Temp CPU')
            self.ax1.axhline(temp_ref, color='r', linestyle='--', label='Ref')
            self.ax1.axvline(emi_ini, color='red', linestyle='--', alpha=0.7, label='Inicio EMI')
            self.ax1.axvline(emi_ini + emi_dur, color='purple', linestyle='--', alpha=0.7, label='Fin EMI')
            self.ax1.axvspan(emi_ini, emi_ini + emi_dur, color='red', alpha=0.1)
            self.ax1.set_ylabel('Temp CPU (°C)')
            self.ax1.legend()
            self.ax1.grid(True)

            # Gráfico 2 - RPM
            self.ax2.clear()
            if falla_detectada:
                self.ax2.plot(t_values[:idx_falla], rpms[:idx_falla], label='RPM')
                self.ax2.plot(t_values[idx_falla:], rpms[idx_falla:], color='red', label='RPM durante Falla')
            else:
                self.ax2.plot(t_values, rpms, label='RPM')
            self.ax2.axvline(emi_ini, color='red', linestyle='--', alpha=0.7)
            self.ax2.axvline(emi_ini + emi_dur, color='purple', linestyle='--', alpha=0.7)
            self.ax2.axvspan(emi_ini, emi_ini + emi_dur, color='red', alpha=0.1)
            self.ax2.set_ylabel('RPM Ventilador')
            self.ax2.legend()
            self.ax2.grid(True)

            # Gráfico 3 - Acción PI
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
            self.ax3.axvline(emi_ini, color='red', linestyle='--', alpha=0.7)
            self.ax3.axvline(emi_ini + emi_dur, color='purple', linestyle='--', alpha=0.7)
            self.ax3.axvspan(emi_ini, emi_ini + emi_dur, color='red', alpha=0.1)
            self.ax3.set_ylabel('Acción PI')
            self.ax3.set_xlabel('Tiempo (s)')
            self.ax3.legend()
            self.ax3.grid(True)

            self.canvas.draw()
            self.fig.savefig("simulacion_resultado.png")

            # Resumen final en consola
            print("-" * 70)
            print(f"=== RESUMEN DE SIMULACIÓN ===")
            print(f"Temperatura final: {temp_cpu:.2f}°C")
            print(f"RPM final: {rpm:.0f}")
            print(f"Error final: {temp_ref - temp_cpu:.2f}°C")
            print(f"Temperatura máxima alcanzada: {max(temps):.2f}°C")
            print(f"Temperatura mínima alcanzada: {min(temps):.2f}°C")
            print(f"RPM máximo alcanzado: {max(rpms):.0f}")
            print(f"RPM mínimo alcanzado: {min(rpms):.0f}")
            print(f"Generación de calor: {q_cpu}°C/s")
            print(f"Coef. disipación: {coef_diss}°C/s/RPM")
            if falla_detectada:
                print("¡FALLA DEL SISTEMA DETECTADA!")
            print("=" * 30)

            self.resultado_text.delete(1.0, tk.END)
            self.resultado_text.insert(tk.END, f"Simulación completada con Kp={Kp}, Ki={Ki}\n")
            if falla_detectada:
                self.resultado_text.insert(tk.END, "¡Falla del sistema detectada por perturbación prolongada!\n")

        except Exception as e:
            messagebox.showerror("Error", str(e))


def main():
    root = tk.Tk()
    app = SimuladorVentiladorCPU(root)
    root.mainloop()


if __name__ == "__main__":
    main()
