#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de Prueba de Instalación
Sistema de Control de Ventilador de CPU
Teoría de Control - UTN FRBA

Este script verifica que todas las dependencias estén instaladas correctamente
y ejecuta una simulación básica de prueba.
"""

import sys

def verificar_dependencias():
    """Verifica que todas las dependencias estén instaladas"""
    print("=== VERIFICACIÓN DE DEPENDENCIAS ===\n")
    
    dependencias = [
        ('numpy', 'NumPy'),
        ('matplotlib', 'Matplotlib'),
        ('scipy', 'SciPy'),
        ('control', 'Python Control Systems Library')
    ]
    
    dependencias_ok = True
    
    for modulo, nombre in dependencias:
        try:
            __import__(modulo)
            print(f"✓ {nombre} - OK")
        except ImportError as e:
            print(f"✗ {nombre} - ERROR: {e}")
            dependencias_ok = False
    
    print()
    
    if dependencias_ok:
        print("✓ Todas las dependencias están instaladas correctamente")
        return True
    else:
        print("✗ Faltan dependencias. Ejecuta: pip install -r requirements.txt")
        return False

def prueba_simulacion_basica():
    """Ejecuta una simulación básica de prueba"""
    print("=== PRUEBA DE SIMULACIÓN BÁSICA ===\n")
    
    try:
        from simulacion_control_ventilador import SistemaControlVentilador
        
        # Crear sistema
        sistema = SistemaControlVentilador()
        print("✓ Sistema de control creado correctamente")
        
        # Análisis de estabilidad
        estabilidad = sistema.analizar_estabilidad()
        print(f"✓ Análisis de estabilidad completado")
        print(f"  - Sistema estable: {'SÍ' if estabilidad['estable'] else 'NO'}")
        print(f"  - Margen de fase: {estabilidad['margen_fase']:.1f}°")
        
        # Simulación rápida
        t, temp, ref = sistema.simular_respuesta_escalon(tiempo_final=5)
        print(f"✓ Simulación de respuesta al escalón completada")
        print(f"  - Puntos simulados: {len(t)}")
        print(f"  - Temperatura final: {temp[-1]:.1f}°C")
        
        # Calcular métricas
        metricas = sistema.calcular_metricas_desempeno(t, temp, ref)
        print(f"✓ Métricas de desempeño calculadas")
        print(f"  - Error estado estacionario: {metricas['error_estado_estacionario']:.2f}°C")
        print(f"  - Tiempo de establecimiento: {metricas['tiempo_establecimiento']:.2f}s")
        
        return True
        
    except Exception as e:
        print(f"✗ Error en la simulación: {e}")
        return False

def prueba_configuraciones():
    """Prueba las configuraciones predefinidas"""
    print("\n=== PRUEBA DE CONFIGURACIONES ===\n")
    
    try:
        from configuracion_parametros import obtener_configuracion, CONFIGURACIONES
        
        print(f"✓ Configuraciones disponibles: {len(CONFIGURACIONES)}")
        
        for nombre in CONFIGURACIONES.keys():
            config = obtener_configuracion(nombre)
            print(f"  - {nombre}: Kp={config.controlador['Kp']}, Ki={config.controlador['Ki']}, Kd={config.controlador['Kd']}")
        
        return True
        
    except Exception as e:
        print(f"✗ Error en configuraciones: {e}")
        return False

def main():
    """Función principal de prueba"""
    print("SCRIPT DE PRUEBA - SISTEMA DE CONTROL DE VENTILADOR")
    print("=" * 60)
    print()
    
    # Verificar dependencias
    if not verificar_dependencias():
        print("\n❌ PRUEBA FALLIDA: Dependencias faltantes")
        sys.exit(1)
    
    # Prueba de simulación
    if not prueba_simulacion_basica():
        print("\n❌ PRUEBA FALLIDA: Error en simulación")
        sys.exit(1)
    
    # Prueba de configuraciones
    if not prueba_configuraciones():
        print("\n❌ PRUEBA FALLIDA: Error en configuraciones")
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("🎉 TODAS LAS PRUEBAS EXITOSAS")
    print("El sistema está listo para usar!")
    print("\nPróximos pasos:")
    print("1. Ejecutar: python simulacion_control_ventilador.py")
    print("2. Ejecutar: python ejemplo_comparacion.py")
    print("3. Experimentar con diferentes configuraciones")
    print("=" * 60)

if __name__ == "__main__":
    main() 