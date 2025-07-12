## Trabajo práctico de Teoría de control

#### UTN FRBA 2025 1C

#### Sistema de control de velocidad de un ventilador de computadora

## Requisitos

- Python instalado.
- Las siguientes bibliotecas de Python:
  - numpy
  - matplotlib

## Instalación

### Paso 1: Clonar el repositorio

Abrir una consola y ejecutar el siguiente comando:

```sh
git clone https://github.com/marciondg/utn-frba-tdc-tp.git
```

### Paso 2: Instalar las bibliotecas requeridas

Desde la misma consola ejecutar:

```sh
pip install numpy matplotlib
```

### Paso 3: Ejecutar el programa

En la consola, ubicarse a la altura raíz del proyecto y ejecutar:

```sh
python simulacion.py
```

### Paso 4: Cómo usar el programa

Al ejecutar el programa, se abrirá una ventana gráfica con la interfaz del simulador. La interfaz está dividida en dos secciones principales:

#### Panel de Control

El panel de control contiene dos pestañas:

**Pestaña "Sistema":**
- **Temperatura objetivo (°C)**: Temperatura que el sistema debe mantener (por defecto: 65°C)
- **Temperatura ambiente (°C)**: Temperatura del entorno (por defecto: 22°C)
- **Umbral de error (°C)**: Zona muerta donde no se aplica control (por defecto: 3°C)
- **Ganancia Proporcional (Kp)**: Ganancia del controlador proporcional (por defecto: 15)
- **Ganancia Integral (Ki)**: Ganancia del controlador integral (por defecto: 2)
- **Ganancia Derivativa (Kd)**: Ganancia del controlador derivativo (por defecto: 0.01)
- **Tiempo de muestreo (s)**: Intervalo entre mediciones (por defecto: 0.5s)
- **Tiempo total (s)**: Duración total de la simulación (por defecto: 500s)
- **RPM mínimo**: Velocidad mínima del ventilador (por defecto: 600 RPM)
- **RPM máximo**: Velocidad máxima del ventilador (por defecto: 3000 RPM)
- **RPM nominal**: Velocidad inicial del ventilador (por defecto: 1500 RPM)
- **Generación de calor (°C/s)**: Calor generado por la CPU (por defecto: 1.0°C/s)
- **Coef. disipación (°C/s/RPM)**: Eficiencia del ventilador (por defecto: 0.001°C/s/RPM)

**Pestaña "Perturbaciones":**
Se pueden establecer perturbaciones durante la ejecución de la simulación. Las mismas pueden ser por interferencia electromagnetica o un pico de carga de trabajo.
- **Inicio de EMI (s)**: Momento en que comienza la interferencia electromagnética
- **Duración de EMI (s)**: Tiempo que dura la interferencia
- **Magnitud EMI (RPM)**: Intensidad de la interferencia en RPM
- **Inicio perturbación de carga (s)**: Momento en que cambia la carga de trabajo
- **Duración perturbación de carga (s)**: Tiempo que dura el cambio de carga
- **Magnitud perturbación de carga (°C/s)**: Incremento en la generación de calor

#### Área de Gráficos

La simulación muestra cuatro gráficos en tiempo real:

1. **Temperatura de la CPU**: Muestra la temperatura actual vs. la referencia
2. **Error**: Diferencia entre temperatura objetivo y actual
3. **Acción de Control**: Señal de control aplicada por el PID
4. **RPM del Ventilador**: Velocidad actual del ventilador

#### Funcionalidades

- **Ejecutar Simulación**: Botón que inicia la simulación con los parámetros configurados
- **Log de resultados**: Muestra información detallada de la simulación en tiempo real
- **Detección de fallas**: El sistema detecta automáticamente cuando no puede mantener el control

