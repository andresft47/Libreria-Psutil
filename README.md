# Monitor de Sistema con Analisis Estadistico

Este programa recolecta metricas en tiempo real del sistema (CPU, RAM y Disco) utilizando la libreria psutil, realiza un analisis estadistico descriptivo y genera un dashboard grafico con los resultados.

## Requisitos Previos

Es necesario tener instalado Python 3.x en el sistema.

### Instalacion de Dependencias

Para ejecutar el codigo, debe instalar las siguientes librerias mediante pip:

```bash
pip install psutil matplotlib numpy
```

## Estructura y Funcionamiento del Codigo

El programa se divide en las siguientes etapas:

### 1. Recoleccion de Datos (collect_advanced_data)
El script toma 30 muestras con un intervalo de 0.2 segundos entre cada una. Durante este proceso se obtienen:
- Porcentaje de uso total de la CPU.
- Uso individual de cada nucleo del procesador.
- Porcentaje de memoria RAM en uso.
- Actividad de lectura/escritura en disco (calculando el delta entre mediciones).

### 2. Analisis Estadistico (show_advanced_stats)
Una vez recolectados los datos, se procesan utilizando la libreria statistics de Python para mostrar en la terminal:
- CPU: Media, mediana, desviacion estandar y percentiles (P25, P50, P75).
- Nucleos: Identificacion del nucleo con mayor y menor carga para evaluar el balanceo.
- Correlacion: Calculo del coeficiente de correlacion de Pearson entre el uso de CPU y RAM.
- Disco: Valor maximo, minimo y varianza de la actividad.
- Distribucion: Un histograma de texto que muestra la frecuencia de uso de la CPU.

### 3. Visualizacion Grafica (plot_system_metrics)
Finalmente, se genera una ventana con cuatro graficos integrados:
- Uso de CPU vs RAM: Grafico de lineas temporal.
- Uso por Nucleo: Grafico de barras con el promedio de cada core.
- Histograma de CPU: Distribucion de frecuencia del porcentaje de uso.
- Actividad de Disco: Grafico de area que muestra los picos de transferencia.

## Instrucciones de Uso

1. Abra una terminal en la carpeta donde se encuentra el archivo.
2. Ejecute el comando:
   ```bash
   python EjemploLibreria.py
   ```
3. Espere aproximadamente 6 segundos mientras se recolectan las muestras.
4. Revise el analisis detallado en la consola.
5. Cierre la ventana de los graficos para terminar la ejecucion del programa.
