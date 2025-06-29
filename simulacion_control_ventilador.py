#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simulación del Sistema de Control de Velocidad del Ventilador de CPU
Teoría de Control - UTN FRBA

Sistema de lazo cerrado con:
- Controlador Digital PID
- Actuador PWM (Ventilador)
- Planta (Proceso de disipación de calor)
- Transductor (Sensor de temperatura)
- Perturbaciones (Temperatura ambiente, Carga del procesador)
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy import signal
from scipy.integrate import odeint
import control as ctrl

# Configuración para gráficos en español
plt.rcParams['font.size'] = 12
plt.rcParams['axes.grid'] = True

class SistemaControlVentilador:
    """
    Clase principal que modela el sistema completo de control de ventilador
    """
    
    def __init__(self):
        # Parámetros del sistema
        self.setup_parametros()
        self.setup_controlador()
        self.setup_planta()
        
    def setup_parametros(self):
        """Configuración de parámetros del sistema"""
        # Parámetros del controlador PID
        self.Kp = 2.0      # Ganancia proporcional
        self.Ki = 0.5      # Ganancia integral
        self.Kd = 0.1      # Ganancia derivativa
        
        # Parámetros del actuador (PWM)
        self.K_pwm = 100   # Ganancia del PWM (RPM/%PWM)
        self.tau_pwm = 0.1 # Constante de tiempo del actuador [s]
        
        # Parámetros de la planta (disipación térmica)
        self.R_th = 2.0    # Resistencia térmica [°C/W]
        self.C_th = 50.0   # Capacitancia térmica [J/°C]
        self.tau_th = self.R_th * self.C_th  # Constante de tiempo térmica
        
        # Parámetros del sensor
        self.K_sensor = 1.0    # Ganancia del sensor
        self.tau_sensor = 0.05 # Constante de tiempo del sensor [s]
        
        # Condiciones iniciales
        self.temp_inicial = 25.0  # Temperatura inicial [°C]
        self.temp_referencia = 65.0  # Temperatura objetivo [°C]
        
        # Perturbaciones
        self.temp_ambiente = 25.0  # Temperatura ambiente [°C]
        self.carga_procesador = 50.0  # Carga del procesador [W]
        
    def setup_controlador(self):
        """Configuración del controlador PID digital"""
        # Función de transferencia del PID continuo
        # C(s) = Kp + Ki/s + Kd*s
        num_pid = [self.Kd, self.Kp, self.Ki]
        den_pid = [1, 0]
        self.pid_continuo = ctrl.tf(num_pid, den_pid)
        
        # Discretización del PID (método de Tustin)
        self.Ts = 0.1  # Período de muestreo [s]
        self.pid_discreto = ctrl.sample_system(self.pid_continuo, self.Ts, method='tustin')
        
    def setup_planta(self):
        """Configuración de las funciones de transferencia de la planta"""
        # Actuador PWM: G_pwm(s) = K_pwm / (tau_pwm*s + 1)
        self.G_pwm = ctrl.tf([self.K_pwm], [self.tau_pwm, 1])
        
        # Planta térmica: G_th(s) = R_th / (tau_th*s + 1)
        self.G_termica = ctrl.tf([self.R_th], [self.tau_th, 1])
        
        # Sensor: G_sensor(s) = K_sensor / (tau_sensor*s + 1)
        self.G_sensor = ctrl.tf([self.K_sensor], [self.tau_sensor, 1])
        
        # Función de transferencia de lazo abierto
        self.G_lazo_abierto = self.pid_continuo * self.G_pwm * self.G_termica * self.G_sensor
        
        # Función de transferencia de lazo cerrado
        self.G_lazo_cerrado = ctrl.feedback(self.G_lazo_abierto, 1)
        
    def simular_respuesta_escalon(self, tiempo_final=20):
        """
        Simula la respuesta del sistema ante un escalón en la referencia
        """
        t = np.linspace(0, tiempo_final, int(tiempo_final/self.Ts))
        
        # Escalón de referencia
        referencia = np.ones_like(t) * (self.temp_referencia - self.temp_inicial)
        
        # Respuesta del sistema
        t_resp, y_resp = ctrl.step_response(self.G_lazo_cerrado, t)
        
        # Agregar temperatura inicial
        temperatura = y_resp + self.temp_inicial
        
        return t_resp, temperatura, referencia + self.temp_inicial
    
    def simular_con_perturbaciones(self, tiempo_final=30):
        """
        Simula el sistema con perturbaciones variables
        """
        t = np.linspace(0, tiempo_final, int(tiempo_final/self.Ts))
        
        # Definir perturbaciones variables
        temp_amb_var = self.temp_ambiente + 5 * np.sin(0.1 * t)  # Variación sinusoidal
        carga_var = self.carga_procesador * (1 + 0.3 * np.sin(0.05 * t))  # Variación de carga
        
        # Referencia constante
        referencia = np.ones_like(t) * self.temp_referencia
        
        # Simulación simplificada (para demostración)
        # En una implementación más completa, se usaría integración numérica
        temperatura = np.zeros_like(t)
        temperatura[0] = self.temp_inicial
        
        for i in range(1, len(t)):
            # Error
            error = referencia[i-1] - temperatura[i-1]
            
            # Salida del controlador (simplificado)
            u = self.Kp * error
            
            # Efecto de las perturbaciones
            perturbacion = (temp_amb_var[i] - self.temp_ambiente) * 0.1 + \
                          (carga_var[i] - self.carga_procesador) * 0.02
            
            # Actualización de temperatura (modelo simplificado)
            dt = t[i] - t[i-1]
            temperatura[i] = temperatura[i-1] + dt * (
                -0.1 * (temperatura[i-1] - temp_amb_var[i]) + 
                0.05 * carga_var[i] - 
                0.02 * u + 
                perturbacion
            )
        
        return t, temperatura, referencia, temp_amb_var, carga_var
    
    def analizar_estabilidad(self):
        """
        Análisis de estabilidad del sistema
        """
        # Margen de ganancia y fase
        gm, pm, wg, wp = ctrl.margin(self.G_lazo_abierto)
        
        # Polos del sistema en lazo cerrado
        polos = ctrl.pole(self.G_lazo_cerrado)
        
        return {
            'margen_ganancia': gm,
            'margen_fase': pm,
            'freq_ganancia': wg,
            'freq_fase': wp,
            'polos': polos,
            'estable': all(np.real(polos) < 0)
        }
    
    def calcular_metricas_desempeno(self, t, y, referencia):
        """
        Calcula métricas de desempeño del sistema
        """
        # Encontrar el valor final
        valor_final = y[-1]
        valor_referencia = referencia[-1]
        
        # Error en estado estacionario
        error_ss = abs(valor_referencia - valor_final)
        
        # Tiempo de establecimiento (2% del valor final)
        indice_2_porciento = np.where(
            abs(y - valor_referencia) <= 0.02 * abs(valor_referencia)
        )[0]
        
        if len(indice_2_porciento) > 0:
            tiempo_establecimiento = t[indice_2_porciento[0]]
        else:
            tiempo_establecimiento = t[-1]
        
        # Sobreimpulso
        valor_max = np.max(y)
        if valor_referencia != 0:
            sobreimpulso = ((valor_max - valor_referencia) / valor_referencia) * 100
        else:
            sobreimpulso = 0
        
        # Tiempo de subida (10% a 90%)
        valor_10 = 0.1 * valor_referencia + 0.9 * y[0]
        valor_90 = 0.9 * valor_referencia + 0.1 * y[0]
        
        try:
            idx_10 = np.where(y >= valor_10)[0][0]
            idx_90 = np.where(y >= valor_90)[0][0]
            tiempo_subida = t[idx_90] - t[idx_10]
        except:
            tiempo_subida = 0
        
        return {
            'error_estado_estacionario': error_ss,
            'tiempo_establecimiento': tiempo_establecimiento,
            'sobreimpulso': sobreimpulso,
            'tiempo_subida': tiempo_subida
        }

def main():
    """Función principal para ejecutar las simulaciones"""
    # Crear instancia del sistema
    sistema = SistemaControlVentilador()
    
    print("=== SIMULACIÓN DEL SISTEMA DE CONTROL DE VENTILADOR ===\n")
    
    # 1. Análisis de estabilidad
    print("1. ANÁLISIS DE ESTABILIDAD")
    estabilidad = sistema.analizar_estabilidad()
    print(f"   Sistema estable: {'SÍ' if estabilidad['estable'] else 'NO'}")
    print(f"   Margen de ganancia: {estabilidad['margen_ganancia']:.2f} dB")
    print(f"   Margen de fase: {estabilidad['margen_fase']:.2f}°")
    print(f"   Polos: {estabilidad['polos']}")
    print()
    
    # 2. Respuesta al escalón
    print("2. RESPUESTA AL ESCALÓN")
    t1, temp1, ref1 = sistema.simular_respuesta_escalon()
    metricas = sistema.calcular_metricas_desempeno(t1, temp1, ref1)
    
    print(f"   Error en estado estacionario: {metricas['error_estado_estacionario']:.2f}°C")
    print(f"   Tiempo de establecimiento: {metricas['tiempo_establecimiento']:.2f}s")
    print(f"   Sobreimpulso: {metricas['sobreimpulso']:.2f}%")
    print(f"   Tiempo de subida: {metricas['tiempo_subida']:.2f}s")
    print()
    
    # 3. Simulación con perturbaciones
    print("3. SIMULACIÓN CON PERTURBACIONES")
    t2, temp2, ref2, temp_amb, carga = sistema.simular_con_perturbaciones()
    print("   Simulación completada con perturbaciones variables")
    print()
    
    # 4. Gráficos de resultados
    crear_graficos(sistema, t1, temp1, ref1, t2, temp2, ref2, temp_amb, carga)
    
    print("4. GRÁFICOS GENERADOS")
    print("   - Respuesta al escalón")
    print("   - Simulación con perturbaciones")
    print("   - Diagramas de Bode")
    print("   - Lugar de las raíces")

def crear_graficos(sistema, t1, temp1, ref1, t2, temp2, ref2, temp_amb, carga):
    """Crear todos los gráficos de análisis"""
    
    # Configurar el estilo de los gráficos
    plt.style.use('default')
    
    # Figura 1: Respuesta al escalón
    fig1, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
    
    ax1.plot(t1, temp1, 'b-', linewidth=2, label='Temperatura CPU')
    ax1.plot(t1, ref1, 'r--', linewidth=2, label='Referencia')
    ax1.set_ylabel('Temperatura [°C]')
    ax1.set_title('Respuesta del Sistema al Escalón de Referencia')
    ax1.legend()
    ax1.grid(True)
    
    # Error
    error1 = ref1 - temp1
    ax2.plot(t1, error1, 'g-', linewidth=2)
    ax2.set_xlabel('Tiempo [s]')
    ax2.set_ylabel('Error [°C]')
    ax2.set_title('Error de Seguimiento')
    ax2.grid(True)
    
    plt.tight_layout()
    plt.savefig('respuesta_escalon.png', dpi=300, bbox_inches='tight')
    
    # Figura 2: Simulación con perturbaciones
    fig2, ((ax3, ax4), (ax5, ax6)) = plt.subplots(2, 2, figsize=(15, 10))
    
    ax3.plot(t2, temp2, 'b-', linewidth=2, label='Temperatura CPU')
    ax3.plot(t2, ref2, 'r--', linewidth=2, label='Referencia')
    ax3.set_ylabel('Temperatura [°C]')
    ax3.set_title('Respuesta con Perturbaciones')
    ax3.legend()
    ax3.grid(True)
    
    ax4.plot(t2, temp_amb, 'orange', linewidth=2)
    ax4.set_ylabel('Temp. Ambiente [°C]')
    ax4.set_title('Perturbación: Temperatura Ambiente')
    ax4.grid(True)
    
    ax5.plot(t2, carga, 'purple', linewidth=2)
    ax5.set_xlabel('Tiempo [s]')
    ax5.set_ylabel('Carga CPU [W]')
    ax5.set_title('Perturbación: Carga del Procesador')
    ax5.grid(True)
    
    error2 = ref2 - temp2
    ax6.plot(t2, error2, 'g-', linewidth=2)
    ax6.set_xlabel('Tiempo [s]')
    ax6.set_ylabel('Error [°C]')
    ax6.set_title('Error con Perturbaciones')
    ax6.grid(True)
    
    plt.tight_layout()
    plt.savefig('simulacion_perturbaciones.png', dpi=300, bbox_inches='tight')
    
    # Figura 3: Diagramas de Bode
    fig3, (ax7, ax8) = plt.subplots(2, 1, figsize=(12, 8))
    
    # Bode de lazo abierto
    w, mag, phase = ctrl.bode_plot(sistema.G_lazo_abierto, plot=False)
    
    ax7.semilogx(w, 20*np.log10(mag))
    ax7.set_ylabel('Magnitud [dB]')
    ax7.set_title('Diagrama de Bode - Lazo Abierto')
    ax7.grid(True)
    
    ax8.semilogx(w, phase*180/np.pi)
    ax8.set_xlabel('Frecuencia [rad/s]')
    ax8.set_ylabel('Fase [°]')
    ax8.grid(True)
    
    plt.tight_layout()
    plt.savefig('bode_lazo_abierto.png', dpi=300, bbox_inches='tight')
    
    # Figura 4: Lugar de las raíces
    fig4, ax9 = plt.subplots(1, 1, figsize=(10, 8))
    
    try:
        ctrl.root_locus(sistema.G_lazo_abierto, ax=ax9)
        ax9.set_title('Lugar Geométrico de las Raíces')
        ax9.grid(True)
        plt.savefig('lugar_raices.png', dpi=300, bbox_inches='tight')
    except:
        print("   Nota: No se pudo generar el lugar de las raíces")
    
    plt.show()

if __name__ == "__main__":
    main() 