import psutil  # Librería para obtener información del sistema (CPU, RAM, Disco, etc.)
import time
import statistics
import math
import matplotlib.pyplot as plt
import numpy as np

def get_correlation(x, y):
    """
    Calcula el coeficiente de correlación de Pearson entre dos listas.
    """
    # Verifica que ambas listas tengan el mismo tamaño y al menos 2 elementos
    if len(x) != len(y) or len(x) < 2:
        return 0
    
    n = len(x)
    
    # Calcula la media de ambas listas
    mean_x = sum(x) / n
    mean_y = sum(y) / n
    
    # Calcula el numerador de la fórmula de Pearson
    num = sum((x[i] - mean_x) * (y[i] - mean_y) for i in range(n))
    
    # Calcula las desviaciones cuadráticas para el denominador
    den_x = sum((x[i] - mean_x)**2 for i in range(n))
    den_y = sum((y[i] - mean_y)**2 for i in range(n))
    
    den = math.sqrt(den_x * den_y)
    
    # Evita división por cero
    if den == 0:
        return 0
    
    return num / den  # Retorna coeficiente entre -1 y 1

def collect_advanced_data(samples=30, interval=0.2):
    """
    Recolecta múltiples métricas del sistema.
    """
    print(f"Recolectando datos avanzados ({samples} muestras)...")
    
    # Diccionario donde se almacenarán todas las métricas
    data = {
        'cpu_overall': [],   # Lista para uso total de CPU
        'cpu_cores': [],     # Lista de listas para uso por núcleo
        'ram_percent': [],   # Lista para porcentaje de RAM usada
        'disk_io': []        # Lista para actividad de disco (delta en KB)
    }
    
    # Obtiene el número de núcleos lógicos del procesador
    # cpu_count() devuelve la cantidad de cores disponibles
    num_cores = psutil.cpu_count()
    
    # Inicializa una lista vacía para cada núcleo
    for _ in range(num_cores):
        data['cpu_cores'].append([])

    # Obtiene estadísticas acumuladas de disco desde que inició el sistema
    # disk_io_counters() devuelve lectura y escritura totales (en bytes)
    last_disk = psutil.disk_io_counters()
    
    for _ in range(samples):
        
        # CPU Overall
        # cpu_percent(interval=interval)
        # - Espera el tiempo indicado (interval)
        # - Calcula el porcentaje promedio de uso en ese periodo
        data['cpu_overall'].append(psutil.cpu_percent(interval=interval))
        
        # CPU Per Core
        # percpu=True hace que devuelva una lista con el uso de cada núcleo
        cores_usage = psutil.cpu_percent(percpu=True)
        
        # Guarda el uso de cada núcleo en su respectiva lista
        for i, val in enumerate(cores_usage):
            data['cpu_cores'][i].append(val)
            
        # RAM usage
        # virtual_memory() devuelve información completa de memoria
        # .percent devuelve el porcentaje de RAM utilizada
        data['ram_percent'].append(psutil.virtual_memory().percent)
        
        # Disk IO (Delta)
        # Obtiene nuevamente los contadores acumulativos del disco
        current_disk = psutil.disk_io_counters()
        
        # Como los valores son acumulativos, se calcula la diferencia
        # entre la medición actual y la anterior para saber cuánto
        # se usó durante este intervalo
        delta_io = (current_disk.read_bytes + current_disk.write_bytes) - \
                   (last_disk.read_bytes + last_disk.write_bytes)
        
        # Se convierte de bytes a KB
        data['disk_io'].append(delta_io / 1024) # KB
        
        # Se actualiza la referencia para la siguiente iteración
        last_disk = current_disk
        
    return data  # Retorna todas las métricas recolectadas

def show_advanced_stats(data):
    """
    Muestra análisis estadístico avanzado.
    """
    print("\n" + "="*60)
    print("   MONITOR DE SISTEMA AVANZADO - ANÁLISIS ESTADÍSTICO")
    print("="*60)

    # CPU Overall Analysis
    cpu = data['cpu_overall']
    print(f"\n[CPU TOTAL] (n={len(cpu)})")
    
    # Media y mediana del uso de CPU
    print(f"  Media: {statistics.mean(cpu):.2f}% | Mediana: {statistics.median(cpu):.2f}%")
    
    # Calcula cuartiles (percentiles 25, 50, 75)
    p25, p50, p75 = statistics.quantiles(cpu, n=4)
    print(f"  Percentiles: P25={p25:.1f}%, P50={p50:.1f}%, P75={p75:.1f}%")
    
    # Desviación estándar (variabilidad)
    print(f"  Desviación Estándar: {statistics.stdev(cpu):.4f}")

    # Per-Core Analysis (balanceo de carga)
    print("\n[ANÁLISIS DE CARGA POR NÚCLEO]")
    
    # Calcula la media de uso para cada núcleo
    core_means = [statistics.mean(core) for core in data['cpu_cores']]
    
    max_core = max(core_means)
    min_core = min(core_means)
    
    print(f"  Media más alta (Core {core_means.index(max_core)}): {max_core:.2f}%")
    print(f"  Media más baja  (Core {core_means.index(min_core)}): {min_core:.2f}%")
    
    # Diferencia entre núcleo más y menos usado
    print(f"  Rango Inter-núcleos (Variable de balanceo): {max_core - min_core:.2f}%")

    # Correlation CPU vs RAM
    ram = data['ram_percent']
    
    # Se calcula correlación usando función personalizada
    corr_cpu_ram = get_correlation(cpu, ram)
    
    print(f"\n[CORRELACIÓN]")
    print(f"  Coeficiente de Pearson (CPU vs RAM): {corr_cpu_ram:.4f}")
    
    # Clasificación de la fuerza de la correlación
    if abs(corr_cpu_ram) > 0.7:
        type_corr = "Fuerte"
    elif abs(corr_cpu_ram) > 0.3:
        type_corr = "Moderada"
    else:
        type_corr = "Débil o inexistente"
    
    print(f"  Interpretación: Correlación {type_corr}")

    # DISK IO Analysis
    disk = data['disk_io']
    print(f"\n[ACTIVIDAD DE DISCO (KB/intervalo)]")
    
    # Máximo, mínimo y varianza de actividad de disco
    print(f"  Máximo: {max(disk):.2f} KB | Mínimo: {min(disk):.2f} KB")
    print(f"  Varianza: {statistics.variance(disk):.2f}")

    # Histograma manual de CPU
    print("\n--- Distribución de Frecuencia CPU Total ---")
    
    buckets = range(0, 101, 10)
    
    for i in range(len(buckets)-1):
        low, high = buckets[i], buckets[i+1]
        
        # Cuenta cuántos valores caen en cada rango
        count = len([x for x in cpu if low <= x < high])
        
        # Incluye el 100% en el último rango
        if high == 100:
            count += len([x for x in cpu if x == 100])
        
        print(f"{low:3}-{high:3}% | {'#' * count} ({count})")

def plot_system_metrics(data):
    """
    Genera un dashboard gráfico con las métricas recolectadas.
    """
    print("\nGenerando salida gráfica...")
    
    # Configuración de estilo premium
    plt.style.use('seaborn-v0_8-darkgrid')
    fig, axs = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle('Métricas de Rendimiento del Sistema', fontsize=20, fontweight='bold', color='#2c3e50')
    
    # Colores elegantes
    colors = ['#3498db', '#e74c3c', '#2ecc71', '#f1c40f']

    # 1. Series Temporales: CPU Overall vs RAM
    ax1 = axs[0, 0]
    samples = range(len(data['cpu_overall']))
    ax1.plot(samples, data['cpu_overall'], label='CPU Total (%)', color=colors[0], linewidth=2, marker='o', markersize=4)
    ax1.plot(samples, data['ram_percent'], label='RAM (%)', color=colors[1], linewidth=2, linestyle='--')
    ax1.set_title('Uso de CPU vs RAM en el Tiempo', fontsize=14, fontweight='semibold')
    ax1.set_xlabel('Muestra')
    ax1.set_ylabel('Porcentaje (%)')
    ax1.legend()
    ax1.set_ylim(0, 105)

    # 2. Análisis por Núcleo (Barras)
    ax2 = axs[0, 1]
    core_means = [statistics.mean(core) for core in data['cpu_cores']]
    core_labels = [f'Core {i}' for i in range(len(core_means))]
    bars = ax2.bar(core_labels, core_means, color=colors[2], alpha=0.8)
    ax2.set_title('Uso Promedio por Núcleo de CPU', fontsize=14, fontweight='semibold')
    ax2.set_ylabel('Uso Promedio (%)')
    ax2.set_ylim(0, 105)
    
    # Añadir etiquetas sobre las barras
    for bar in bars:
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height + 1, f'{height:.1f}%', ha='center', va='bottom', fontsize=10)

    # 3. Distribución de CPU (Histograma)
    ax3 = axs[1, 0]
    ax3.hist(data['cpu_overall'], bins=10, range=(0, 100), color=colors[3], edgecolor='white', alpha=0.7)
    ax3.set_title('Distribución de Frecuencia (CPU Total)', fontsize=14, fontweight='semibold')
    ax3.set_xlabel('Rango de Uso (%)')
    ax3.set_ylabel('Frecuencia')

    # 4. Actividad de Disco (Línea de área)
    ax4 = axs[1, 1]
    ax4.fill_between(samples, data['disk_io'], color=colors[0], alpha=0.3)
    ax4.plot(samples, data['disk_io'], color=colors[0], linewidth=1.5)
    ax4.set_title('Actividad de Disco (E/S)', fontsize=14, fontweight='semibold')
    ax4.set_xlabel('Muestra')
    ax4.set_ylabel('KB Transferidos')

    # Ajuste final
    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    print("Dashboard listo. Se abrirá una ventana con los gráficos.")
    plt.show()

if __name__ == "__main__":
    try:
        # Recolección de datos del sistema
        system_data = collect_advanced_data(samples=30, interval=0.2)
        
        # Análisis estadístico de los datos
        show_advanced_stats(system_data)
        
        # Generación de gráficos
        plot_system_metrics(system_data)
        
    except KeyboardInterrupt:
        print("\nPrueba detenida.")
        
    except Exception as e:
        print(f"\nOcurrió un error: {e}")
        print("Tip: Instala psutil con 'pip install psutil'")