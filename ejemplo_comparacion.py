#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ejemplo de Comparación de Configuraciones
Sistema de Control de Ventilador de CPU
Teoría de Control - UTN FRBA

Este script compara diferentes configuraciones del controlador PID
para mostrar cómo afectan al comportamiento del sistema.
"""

import numpy as np
import matplotlib.pyplot as plt
from simulacion_control_ventilador import SistemaControlVentilador
from configuracion_parametros import obtener_configuracion

def comparar_configuraciones():
    """
    Compara diferentes configuraciones del sistema
    """
    # Configuraciones a comparar
    configuraciones = ['conservadora', 'por_defecto', 'agresiva', 'gaming']
    colores = ['blue', 'green', 'red', 'purple']
    
    # Configurar gráficos
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
    
    print("=== COMPARACIÓN DE CONFIGURACIONES ===\n")
    
    for i, (config_nombre, color) in enumerate(zip(configuraciones, colores)):
        print(f"Simulando configuración: {config_nombre}")
        
        # Obtener configuración
        config = obtener_configuracion(config_nombre)
        
        # Crear sistema con configuración específica
        sistema = SistemaControlVentilador()
        
        # Aplicar parámetros de configuración
        sistema.Kp = config.controlador['Kp']
        sistema.Ki = config.controlador['Ki']
        sistema.Kd = config.controlador['Kd']
        sistema.temp_referencia = config.condiciones_iniciales['temp_referencia']
        
        # Recalcular funciones de transferencia
        sistema.setup_controlador()
        sistema.setup_planta()
        
        # Simular respuesta al escalón
        t, temp, ref = sistema.simular_respuesta_escalon(tiempo_final=15)
        
        # Calcular métricas
        metricas = sistema.calcular_metricas_desempeno(t, temp, ref)
        
        # Graficar respuesta al escalón
        ax1.plot(t, temp, color=color, linewidth=2, label=f'{config_nombre}')
        ax1.plot(t, ref, '--', color=color, alpha=0.5)
        
        # Graficar error
        error = ref - temp
        ax2.plot(t, error, color=color, linewidth=2, label=f'{config_nombre}')
        
        # Simular con perturbaciones
        t2, temp2, ref2, temp_amb, carga = sistema.simular_con_perturbaciones(tiempo_final=20)
        
        # Graficar respuesta con perturbaciones
        ax3.plot(t2, temp2, color=color, linewidth=2, label=f'{config_nombre}')
        ax3.plot(t2, ref2, '--', color=color, alpha=0.5)
        
        # Graficar error con perturbaciones
        error2 = ref2 - temp2
        ax4.plot(t2, error2, color=color, linewidth=2, label=f'{config_nombre}')
        
        # Imprimir métricas
        print(f"  Kp={sistema.Kp}, Ki={sistema.Ki}, Kd={sistema.Kd}")
        print(f"  Error estado estacionario: {metricas['error_estado_estacionario']:.2f}°C")
        print(f"  Tiempo establecimiento: {metricas['tiempo_establecimiento']:.2f}s")
        print(f"  Sobreimpulso: {metricas['sobreimpulso']:.2f}%")
        print()
    
    # Configurar gráficos
    ax1.set_title('Respuesta al Escalón - Comparación de Configuraciones')
    ax1.set_xlabel('Tiempo [s]')
    ax1.set_ylabel('Temperatura [°C]')
    ax1.legend()
    ax1.grid(True)
    
    ax2.set_title('Error de Seguimiento - Escalón')
    ax2.set_xlabel('Tiempo [s]')
    ax2.set_ylabel('Error [°C]')
    ax2.legend()
    ax2.grid(True)
    
    ax3.set_title('Respuesta con Perturbaciones')
    ax3.set_xlabel('Tiempo [s]')
    ax3.set_ylabel('Temperatura [°C]')
    ax3.legend()
    ax3.grid(True)
    
    ax4.set_title('Error con Perturbaciones')
    ax4.set_xlabel('Tiempo [s]')
    ax4.set_ylabel('Error [°C]')
    ax4.legend()
    ax4.grid(True)
    
    plt.tight_layout()
    plt.savefig('comparacion_configuraciones.png', dpi=300, bbox_inches='tight')
    plt.show()

def analizar_sintonizacion_pid():
    """
    Analiza el efecto de cada parámetro del PID por separado
    """
    print("=== ANÁLISIS DE SINTONIZACIÓN PID ===\n")
    
    # Configuración base
    config_base = obtener_configuracion('por_defecto')
    
    # Crear figura para análisis
    fig, ((ax1, ax2, ax3), (ax4, ax5, ax6)) = plt.subplots(2, 3, figsize=(18, 12))
    
    # 1. Efecto de Kp
    print("1. Analizando efecto de Kp...")
    valores_kp = [0.5, 1.0, 2.0, 4.0, 8.0]
    colores_kp = ['blue', 'green', 'orange', 'red', 'purple']
    
    for kp, color in zip(valores_kp, colores_kp):
        sistema = SistemaControlVentilador()
        sistema.Kp = kp
        sistema.Ki = config_base.controlador['Ki']
        sistema.Kd = config_base.controlador['Kd']
        sistema.setup_controlador()
        sistema.setup_planta()
        
        t, temp, ref = sistema.simular_respuesta_escalon(tiempo_final=10)
        ax1.plot(t, temp, color=color, linewidth=2, label=f'Kp={kp}')
        
        error = ref - temp
        ax4.plot(t, error, color=color, linewidth=2, label=f'Kp={kp}')
    
    # 2. Efecto de Ki
    print("2. Analizando efecto de Ki...")
    valores_ki = [0.1, 0.3, 0.5, 1.0, 2.0]
    colores_ki = ['blue', 'green', 'orange', 'red', 'purple']
    
    for ki, color in zip(valores_ki, colores_ki):
        sistema = SistemaControlVentilador()
        sistema.Kp = config_base.controlador['Kp']
        sistema.Ki = ki
        sistema.Kd = config_base.controlador['Kd']
        sistema.setup_controlador()
        sistema.setup_planta()
        
        t, temp, ref = sistema.simular_respuesta_escalon(tiempo_final=10)
        ax2.plot(t, temp, color=color, linewidth=2, label=f'Ki={ki}')
        
        error = ref - temp
        ax5.plot(t, error, color=color, linewidth=2, label=f'Ki={ki}')
    
    # 3. Efecto de Kd
    print("3. Analizando efecto de Kd...")
    valores_kd = [0.0, 0.05, 0.1, 0.2, 0.5]
    colores_kd = ['blue', 'green', 'orange', 'red', 'purple']
    
    for kd, color in zip(valores_kd, colores_kd):
        sistema = SistemaControlVentilador()
        sistema.Kp = config_base.controlador['Kp']
        sistema.Ki = config_base.controlador['Ki']
        sistema.Kd = kd
        sistema.setup_controlador()
        sistema.setup_planta()
        
        t, temp, ref = sistema.simular_respuesta_escalon(tiempo_final=10)
        ax3.plot(t, temp, color=color, linewidth=2, label=f'Kd={kd}')
        
        error = ref - temp
        ax6.plot(t, error, color=color, linewidth=2, label=f'Kd={kd}')
    
    # Configurar gráficos
    titles = ['Efecto de Kp', 'Efecto de Ki', 'Efecto de Kd']
    for i, (ax, title) in enumerate(zip([ax1, ax2, ax3], titles)):
        ax.set_title(f'{title} - Respuesta')
        ax.set_xlabel('Tiempo [s]')
        ax.set_ylabel('Temperatura [°C]')
        ax.legend()
        ax.grid(True)
    
    for i, (ax, title) in enumerate(zip([ax4, ax5, ax6], titles)):
        ax.set_title(f'{title} - Error')
        ax.set_xlabel('Tiempo [s]')
        ax.set_ylabel('Error [°C]')
        ax.legend()
        ax.grid(True)
    
    plt.tight_layout()
    plt.savefig('analisis_sintonizacion_pid.png', dpi=300, bbox_inches='tight')
    plt.show()

def simular_escenarios_reales():
    """
    Simula escenarios de uso real del sistema
    """
    print("=== SIMULACIÓN DE ESCENARIOS REALES ===\n")
    
    # Escenarios diferentes
    escenarios = {
        'Arranque en frío': {
            'temp_inicial': 20.0,
            'carga_inicial': 10.0,
            'descripcion': 'Encendido de la computadora'
        },
        'Gaming intensivo': {
            'temp_inicial': 45.0,
            'carga_inicial': 95.0,
            'descripcion': 'Juego con gráficos intensivos'
        },
        'Trabajo de oficina': {
            'temp_inicial': 35.0,
            'carga_inicial': 25.0,
            'descripcion': 'Uso típico de oficina'
        },
        'Renderizado': {
            'temp_inicial': 50.0,
            'carga_inicial': 100.0,
            'descripcion': 'Renderizado de video prolongado'
        }
    }
    
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    axes = axes.flatten()
    
    for i, (nombre, datos) in enumerate(escenarios.items()):
        print(f"Simulando escenario: {nombre}")
        print(f"  {datos['descripcion']}")
        
        # Crear sistema optimizado para el escenario
        if 'gaming' in nombre.lower():
            config = obtener_configuracion('gaming')
        elif 'oficina' in nombre.lower():
            config = obtener_configuracion('oficina')
        else:
            config = obtener_configuracion('por_defecto')
        
        sistema = SistemaControlVentilador()
        sistema.Kp = config.controlador['Kp']
        sistema.Ki = config.controlador['Ki']
        sistema.Kd = config.controlador['Kd']
        sistema.temp_inicial = datos['temp_inicial']
        sistema.carga_procesador = datos['carga_inicial']
        
        sistema.setup_controlador()
        sistema.setup_planta()
        
        # Simular escenario
        t, temp, ref, temp_amb, carga = sistema.simular_con_perturbaciones(tiempo_final=25)
        
        # Graficar
        ax = axes[i]
        ax.plot(t, temp, 'b-', linewidth=2, label='Temperatura CPU')
        ax.plot(t, ref, 'r--', linewidth=2, label='Referencia')
        ax.axhline(y=85, color='red', linestyle=':', alpha=0.7, label='Límite térmico')
        
        ax.set_title(f'{nombre}\n{datos["descripcion"]}')
        ax.set_xlabel('Tiempo [s]')
        ax.set_ylabel('Temperatura [°C]')
        ax.legend()
        ax.grid(True)
        
        # Calcular estadísticas
        temp_max = np.max(temp)
        temp_promedio = np.mean(temp)
        tiempo_estabilizacion = len(t) * 0.1  # Aproximado
        
        print(f"  Temperatura máxima: {temp_max:.1f}°C")
        print(f"  Temperatura promedio: {temp_promedio:.1f}°C")
        print(f"  Tiempo de estabilización: ~{tiempo_estabilizacion:.1f}s")
        print()
    
    plt.tight_layout()
    plt.savefig('escenarios_reales.png', dpi=300, bbox_inches='tight')
    plt.show()

def main():
    """Función principal del ejemplo"""
    print("=== ANÁLISIS COMPLETO DEL SISTEMA DE CONTROL ===\n")
    
    # 1. Comparar configuraciones
    comparar_configuraciones()
    
    # 2. Analizar sintonización PID
    analizar_sintonizacion_pid()
    
    # 3. Simular escenarios reales
    simular_escenarios_reales()
    
    print("=== ANÁLISIS COMPLETADO ===")
    print("Se han generado los siguientes archivos:")
    print("  - comparacion_configuraciones.png")
    print("  - analisis_sintonizacion_pid.png")
    print("  - escenarios_reales.png")

if __name__ == "__main__":
    main() 