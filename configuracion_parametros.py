#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Configuración de Parámetros del Sistema de Control de Ventilador
Teoría de Control - UTN FRBA

Este archivo permite modificar fácilmente los parámetros del sistema
para experimentar con diferentes configuraciones.
"""

class ConfiguracionSistema:
    """
    Clase de configuración con todos los parámetros del sistema
    """
    
    def __init__(self):
        self.setup_parametros_por_defecto()
    
    def setup_parametros_por_defecto(self):
        """Configuración por defecto del sistema"""
        
        # ===== PARÁMETROS DEL CONTROLADOR PID =====
        self.controlador = {
            'Kp': 2.0,      # Ganancia proporcional
            'Ki': 0.5,      # Ganancia integral  
            'Kd': 0.1,      # Ganancia derivativa
            'Ts': 0.1,      # Período de muestreo [s]
        }
        
        # ===== PARÁMETROS DEL ACTUADOR (PWM) =====
        self.actuador = {
            'K_pwm': 100,       # Ganancia del PWM [RPM/%PWM]
            'tau_pwm': 0.1,     # Constante de tiempo [s]
            'pwm_min': 0,       # PWM mínimo [%]
            'pwm_max': 100,     # PWM máximo [%]
        }
        
        # ===== PARÁMETROS DE LA PLANTA TÉRMICA =====
        self.planta = {
            'R_th': 2.0,        # Resistencia térmica [°C/W]
            'C_th': 50.0,       # Capacitancia térmica [J/°C]
            'eficiencia_ventilador': 0.8,  # Eficiencia del ventilador
        }
        
        # ===== PARÁMETROS DEL SENSOR =====
        self.sensor = {
            'K_sensor': 1.0,        # Ganancia del sensor
            'tau_sensor': 0.05,     # Constante de tiempo [s]
            'resolucion': 0.1,      # Resolución del sensor [°C]
            'ruido_std': 0.2,       # Desviación estándar del ruido [°C]
        }
        
        # ===== CONDICIONES INICIALES =====
        self.condiciones_iniciales = {
            'temp_inicial': 25.0,       # Temperatura inicial [°C]
            'temp_referencia': 65.0,    # Temperatura objetivo [°C]
            'temp_maxima': 85.0,        # Temperatura máxima permitida [°C]
        }
        
        # ===== PERTURBACIONES =====
        self.perturbaciones = {
            'temp_ambiente': 25.0,      # Temperatura ambiente base [°C]
            'variacion_ambiente': 5.0,  # Variación de temp. ambiente [°C]
            'carga_procesador': 50.0,   # Carga base del procesador [W]
            'variacion_carga': 30.0,    # Variación de carga [%]
        }
        
        # ===== PARÁMETROS DE SIMULACIÓN =====
        self.simulacion = {
            'tiempo_simulacion': 30.0,  # Tiempo total de simulación [s]
            'paso_integracion': 0.01,   # Paso de integración [s]
            'freq_muestreo': 10.0,      # Frecuencia de muestreo [Hz]
        }
    
    def configuracion_conservadora(self):
        """Configuración conservadora (respuesta lenta pero estable)"""
        self.controlador['Kp'] = 1.0
        self.controlador['Ki'] = 0.2
        self.controlador['Kd'] = 0.05
        return self
    
    def configuracion_agresiva(self):
        """Configuración agresiva (respuesta rápida)"""
        self.controlador['Kp'] = 5.0
        self.controlador['Ki'] = 1.0
        self.controlador['Kd'] = 0.2
        return self
    
    def configuracion_gaming(self):
        """Configuración optimizada para gaming (alta carga variable)"""
        self.controlador['Kp'] = 3.0
        self.controlador['Ki'] = 0.8
        self.controlador['Kd'] = 0.15
        self.condiciones_iniciales['temp_referencia'] = 70.0
        self.perturbaciones['carga_procesador'] = 80.0
        self.perturbaciones['variacion_carga'] = 50.0
        return self
    
    def configuracion_servidor(self):
        """Configuración para servidor (carga constante alta)"""
        self.controlador['Kp'] = 2.5
        self.controlador['Ki'] = 0.6
        self.controlador['Kd'] = 0.1
        self.condiciones_iniciales['temp_referencia'] = 60.0
        self.perturbaciones['carga_procesador'] = 90.0
        self.perturbaciones['variacion_carga'] = 10.0
        return self
    
    def configuracion_oficina(self):
        """Configuración para uso de oficina (carga baja)"""
        self.controlador['Kp'] = 1.5
        self.controlador['Ki'] = 0.3
        self.controlador['Kd'] = 0.08
        self.condiciones_iniciales['temp_referencia'] = 55.0
        self.perturbaciones['carga_procesador'] = 20.0
        self.perturbaciones['variacion_carga'] = 20.0
        return self
    
    def imprimir_configuracion(self):
        """Imprime la configuración actual"""
        print("=== CONFIGURACIÓN ACTUAL DEL SISTEMA ===\n")
        
        print("CONTROLADOR PID:")
        for key, value in self.controlador.items():
            print(f"  {key}: {value}")
        
        print("\nACTUADOR:")
        for key, value in self.actuador.items():
            print(f"  {key}: {value}")
        
        print("\nPLANTA:")
        for key, value in self.planta.items():
            print(f"  {key}: {value}")
        
        print("\nSENSOR:")
        for key, value in self.sensor.items():
            print(f"  {key}: {value}")
        
        print("\nCONDICIONES INICIALES:")
        for key, value in self.condiciones_iniciales.items():
            print(f"  {key}: {value}")
        
        print("\nPERTURBACIONES:")
        for key, value in self.perturbaciones.items():
            print(f"  {key}: {value}")
        
        print("\nSIMULACIÓN:")
        for key, value in self.simulacion.items():
            print(f"  {key}: {value}")
        print()

# Configuraciones predefinidas
CONFIGURACIONES = {
    'por_defecto': ConfiguracionSistema(),
    'conservadora': ConfiguracionSistema().configuracion_conservadora(),
    'agresiva': ConfiguracionSistema().configuracion_agresiva(),
    'gaming': ConfiguracionSistema().configuracion_gaming(),
    'servidor': ConfiguracionSistema().configuracion_servidor(),
    'oficina': ConfiguracionSistema().configuracion_oficina(),
}

def obtener_configuracion(nombre='por_defecto'):
    """
    Obtiene una configuración predefinida
    
    Args:
        nombre: Nombre de la configuración ('por_defecto', 'conservadora', 
                'agresiva', 'gaming', 'servidor', 'oficina')
    
    Returns:
        ConfiguracionSistema: Objeto con la configuración solicitada
    """
    if nombre in CONFIGURACIONES:
        return CONFIGURACIONES[nombre]
    else:
        print(f"Configuración '{nombre}' no encontrada. Usando configuración por defecto.")
        return CONFIGURACIONES['por_defecto']

if __name__ == "__main__":
    # Ejemplo de uso
    print("=== CONFIGURACIONES DISPONIBLES ===\n")
    
    for nombre, config in CONFIGURACIONES.items():
        print(f"--- {nombre.upper()} ---")
        config.imprimir_configuracion()
        print("-" * 50) 