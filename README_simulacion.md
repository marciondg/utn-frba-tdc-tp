# Simulación del Sistema de Control de Ventilador de CPU

## Descripción del Proyecto

Este proyecto implementa una simulación completa del sistema de control de velocidad del ventilador de CPU para el trabajo práctico de Teoría de Control de UTN FRBA.

### Componentes del Sistema

El sistema modelado incluye todos los componentes del diagrama de bloques:

1. **Controlador Digital PID** - Controla la velocidad del ventilador
2. **Actuador PWM** - Modula la velocidad del ventilador
3. **Planta Térmica** - Proceso de disipación de calor del CPU
4. **Transductor** - Sensor de temperatura (DTS)
5. **Perturbaciones** - Temperatura ambiente y carga del procesador
6. **Carga** - Computadora que genera calor

## Estructura de Archivos

```
├── simulacion_control_ventilador.py    # Simulación principal
├── configuracion_parametros.py         # Configuración de parámetros
├── ejemplo_comparacion.py              # Ejemplos de análisis
├── requirements.txt                    # Dependencias
└── README_simulacion.md               # Este archivo
```

## Instalación

### 1. Instalar Python
Asegúrate de tener Python 3.8 o superior instalado.

### 2. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 3. Verificar instalación
```bash
python -c "import numpy, matplotlib, scipy, control; print('Todas las dependencias instaladas correctamente')"
```

## Uso del Sistema

### Simulación Básica

Para ejecutar la simulación básica:

```bash
python simulacion_control_ventilador.py
```

Esto generará:
- Análisis de estabilidad del sistema
- Respuesta al escalón
- Simulación con perturbaciones
- Gráficos de Bode y lugar de las raíces

### Comparación de Configuraciones

Para comparar diferentes configuraciones del controlador:

```bash
python ejemplo_comparacion.py
```

Esto ejecutará:
- Comparación de configuraciones predefinidas
- Análisis de sintonización PID
- Simulación de escenarios reales

### Configuraciones Disponibles

El sistema incluye configuraciones predefinidas:

- **`por_defecto`** - Configuración balanceada
- **`conservadora`** - Respuesta lenta pero estable
- **`agresiva`** - Respuesta rápida
- **`gaming`** - Optimizada para gaming
- **`servidor`** - Para servidores con carga constante
- **`oficina`** - Para uso de oficina

### Personalizar Parámetros

Para usar una configuración específica:

```python
from configuracion_parametros import obtener_configuracion
from simulacion_control_ventilador import SistemaControlVentilador

# Obtener configuración
config = obtener_configuracion('gaming')

# Crear sistema
sistema = SistemaControlVentilador()
sistema.Kp = config.controlador['Kp']
sistema.Ki = config.controlador['Ki']
sistema.Kd = config.controlador['Kd']

# Recalcular y simular
sistema.setup_controlador()
sistema.setup_planta()
t, temp, ref = sistema.simular_respuesta_escalon()
```

## Análisis Disponibles

### 1. Análisis de Estabilidad
- Margen de ganancia y fase
- Ubicación de polos
- Criterio de estabilidad

### 2. Métricas de Desempeño
- Error en estado estacionario
- Tiempo de establecimiento
- Sobreimpulso
- Tiempo de subida

### 3. Respuesta Temporal
- Respuesta al escalón
- Respuesta con perturbaciones
- Simulación de escenarios reales

### 4. Análisis Frecuencial
- Diagramas de Bode
- Lugar geométrico de las raíces

## Parámetros del Sistema

### Controlador PID
- `Kp`: Ganancia proporcional (por defecto: 2.0)
- `Ki`: Ganancia integral (por defecto: 0.5)
- `Kd`: Ganancia derivativa (por defecto: 0.1)
- `Ts`: Período de muestreo (por defecto: 0.1s)

### Planta Térmica
- `R_th`: Resistencia térmica (por defecto: 2.0 °C/W)
- `C_th`: Capacitancia térmica (por defecto: 50.0 J/°C)

### Actuador PWM
- `K_pwm`: Ganancia PWM (por defecto: 100 RPM/%PWM)
- `tau_pwm`: Constante de tiempo (por defecto: 0.1s)

## Resultados y Gráficos

La simulación genera varios archivos PNG con los resultados:

1. **`respuesta_escalon.png`** - Respuesta al escalón de referencia
2. **`simulacion_perturbaciones.png`** - Respuesta con perturbaciones
3. **`bode_lazo_abierto.png`** - Diagramas de Bode
4. **`lugar_raices.png`** - Lugar geométrico de las raíces
5. **`comparacion_configuraciones.png`** - Comparación de configuraciones
6. **`analisis_sintonizacion_pid.png`** - Análisis de parámetros PID
7. **`escenarios_reales.png`** - Simulación de escenarios reales

## Experimentación

### Modificar Parámetros del PID

```python
# Crear configuración personalizada
config = ConfiguracionSistema()
config.controlador['Kp'] = 3.0  # Aumentar ganancia proporcional
config.controlador['Ki'] = 0.8  # Aumentar ganancia integral
config.controlador['Kd'] = 0.2  # Aumentar ganancia derivativa
```

### Simular Diferentes Escenarios

```python
# Escenario de alta carga
sistema.carga_procesador = 100.0  # 100W
sistema.temp_ambiente = 35.0      # 35°C ambiente
sistema.temp_referencia = 70.0    # Objetivo 70°C
```

### Analizar Perturbaciones

```python
# Perturbaciones variables
temp_ambiente_variable = 25 + 10 * np.sin(0.1 * t)
carga_variable = 50 * (1 + 0.5 * np.sin(0.05 * t))
```

## Interpretación de Resultados

### Métricas de Desempeño

- **Error estado estacionario < 2°C**: Buen seguimiento
- **Tiempo establecimiento < 10s**: Respuesta rápida
- **Sobreimpulso < 20%**: Respuesta controlada
- **Margen de fase > 45°**: Sistema estable

### Análisis de Estabilidad

- **Polos con parte real negativa**: Sistema estable
- **Margen de ganancia > 6dB**: Robustez adecuada
- **Margen de fase > 45°**: Estabilidad robusta

## Troubleshooting

### Error de importación de `control`
```bash
pip install slycot  # Dependencia adicional
pip install control --upgrade
```

### Gráficos no se muestran
```python
import matplotlib
matplotlib.use('TkAgg')  # O 'Qt5Agg'
```

### Simulación muy lenta
- Reducir `tiempo_simulacion` en configuración
- Aumentar `paso_integracion`
- Usar menos puntos en el análisis

## Extensiones Posibles

1. **Control adaptativo** - Ajuste automático de parámetros
2. **Filtros de ruido** - Reducir ruido del sensor
3. **Saturación del actuador** - Límites físicos del PWM
4. **Modelo no lineal** - Efectos de convección natural
5. **Control predictivo** - MPC para optimización

## Referencias

- Franklin, G. F., Powell, J. D., & Emami-Naeini, A. (2014). *Feedback Control of Dynamic Systems*
- Ogata, K. (2010). *Modern Control Engineering*
- Documentación de Python Control Systems Library

## Contacto

Para dudas sobre la implementación, consultar la documentación del código o contactar al equipo de desarrollo.

---

**Teoría de Control - UTN FRBA**  
**Trabajo Práctico 2025** 