# Sistema de control de velocidad de FAN y temperatura de CPU

## Trabajo Práctico - Teoría de control - UTN FRBA - Prof. Civale

Simulador de un sistema de control PID para la gestión térmica de una CPU mediante control de velocidad de ventilador. El sistema incluye detección de fallas, perturbaciones EMI/RFI, y análisis en tiempo real del comportamiento del controlador.

## Requisitos

- Python 3.7+.
- Bibliotecas Python:
  - numpy
  - matplotlib
  - tkinter

## Instalación

### 1. Clonar el repositorio

Abrir una consola y ejecutar el siguiente comando:

```sh
git clone https://github.com/marciondg/utn-frba-tdc-tp.git
cd utn-frba-tdc-tp
```

### 2. Instalar dependencias

Desde la misma consola ejecutar:

```bash
pip install numpy matplotlib
```

### 3. Ejecutar simulador

En la consola, ubicarse a la altura raíz del proyecto y ejecutar:

```bash
python simulacion.py
```

## Guía de uso

La interfaz del simulador está dividida en dos secciones principales:

#### Panel de Control

El panel de control contiene dos pestañas:

**Sistema**

Configuración de los parámetros fundamentales del controlador:

- **Temperatura objetivo (°C)**: Temperatura que el sistema debe mantener (por defecto: 65°C)
- **Temperatura ambiente (°C)**: Temperatura del entorno (por defecto: 22°C)
- **Umbral de error (°C)**: Zona muerta donde no se aplica control (por defecto: 3°C)
- **Ganancia Proporcional (Kp)**: Ganancia del controlador proporcional (por defecto: 15)
- **Ganancia Integral (Ki)**: Ganancia del controlador integral (por defecto: 0)
- **Ganancia Derivativa (Kd)**: Ganancia del controlador derivativo (por defecto: 0)
- **Tiempo de muestreo (s)**: Intervalo entre mediciones (por defecto: 0.5s)
- **Tiempo total (s)**: Duración total de la simulación (por defecto: 500s)
- **RPM mínimo**: Velocidad mínima del ventilador (por defecto: 600 RPM)
- **RPM máximo**: Velocidad máxima del ventilador (por defecto: 3000 RPM)
- **RPM nominal**: Velocidad inicial del ventilador (por defecto: 1500 RPM)
- **Generación de calor (°C/s)**: Calor generado por la CPU (por defecto: 1.0°C/s)

Esta pestaña cuenta con el botón para iniciar la simulación y un log con información detallada de la ejecución de la simulación.

**Perturbaciones**

Se pueden establecer perturbaciones durante la ejecución de la simulación. Las mismas pueden ser por interferencia electromagnetica o un pico de carga de trabajo:
- **Inicio de EMI (s)**: Momento en que comienza la interferencia electromagnética
- **Duración de EMI (s)**: Tiempo que dura la interferencia
- **Magnitud EMI (RPM)**: Intensidad de la interferencia en RPM
- **Inicio perturbación de carga (s)**: Momento en que cambia la carga de trabajo
- **Duración perturbación de carga (s)**: Tiempo que dura el cambio de carga
- **Magnitud perturbación de carga (°C/s)**: Incremento en la generación de calor

#### Gráficos

La simulación muestra cuatro gráficos:

1. **Temperatura de la CPU**: Muestra la temperatura actual vs. la referencia
2. **Error**: Diferencia entre temperatura objetivo y actual
3. **Acción de Control**: Señal de control aplicada por el PID
4. **RPM del Ventilador**: Velocidad actual del ventilador