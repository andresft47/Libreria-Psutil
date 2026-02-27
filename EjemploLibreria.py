import psutil  # Librería para obtener información del sistema (CPU, RAM, Disco, etc.)
import time
import statistics
import math

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
    
    # 🔹 Obtiene el número de núcleos lógicos del procesador
    # cpu_count() devuelve la cantidad de cores disponibles
    num_cores = psutil.cpu_count()
    
    # Inicializa una lista vacía para cada núcleo
    for _ in range(num_cores):
        data['cpu_cores'].append([])

    # 🔹 Obtiene estadísticas acumuladas de disco desde que inició el sistema
    # disk_io_counters() devuelve lectura y escritura totales (en bytes)
    last_disk = psutil.disk_io_counters()
    
    for _ in range(samples):
        
        # 1️⃣ CPU Overall
        # cpu_percent(interval=interval)
        # - Espera el tiempo indicado (interval)
        # - Calcula el porcentaje promedio de uso en ese periodo
        data['cpu_overall'].append(psutil.cpu_percent(interval=interval))
        
        # 2️⃣ CPU Per Core
        # percpu=True hace que devuelva una lista con el uso de cada núcleo
        cores_usage = psutil.cpu_percent(percpu=True)
        
        # Guarda el uso de cada núcleo en su respectiva lista
        for i, val in enumerate(cores_usage):
            data['cpu_cores'][i].append(val)
            
        # 3️⃣ RAM usage
        # virtual_memory() devuelve información completa de memoria
        # .percent devuelve el porcentaje de RAM utilizada
        data['ram_percent'].append(psutil.virtual_memory().percent)
        
        # 4️⃣ Disk IO (Delta)
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

    # 1️⃣ CPU Overall Analysis
    cpu = data['cpu_overall']
    print(f"\n[CPU TOTAL] (n={len(cpu)})")
    
    # Media y mediana del uso de CPU
    print(f"  Media: {statistics.mean(cpu):.2f}% | Mediana: {statistics.median(cpu):.2f}%")
    
    # Calcula cuartiles (percentiles 25, 50, 75)
    p25, p50, p75 = statistics.quantiles(cpu, n=4)
    print(f"  Percentiles: P25={p25:.1f}%, P50={p50:.1f}%, P75={p75:.1f}%")
    
    # Desviación estándar (variabilidad)
    print(f"  Desviación Estándar: {statistics.stdev(cpu):.4f}")

    # 2️⃣ Per-Core Analysis (balanceo de carga)
    print("\n[ANÁLISIS DE CARGA POR NÚCLEO]")
    
    # Calcula la media de uso para cada núcleo
    core_means = [statistics.mean(core) for core in data['cpu_cores']]
    
    max_core = max(core_means)
    min_core = min(core_means)
    
    print(f"  Media más alta (Core {core_means.index(max_core)}): {max_core:.2f}%")
    print(f"  Media más baja  (Core {core_means.index(min_core)}): {min_core:.2f}%")
    
    # Diferencia entre núcleo más y menos usado
    print(f"  Rango Inter-núcleos (Variable de balanceo): {max_core - min_core:.2f}%")

    # 3️⃣ Correlation CPU vs RAM
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

    # 4️⃣ DISK IO Analysis
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

if __name__ == "__main__":
    try:
        # Recolección de datos del sistema
        system_data = collect_advanced_data(samples=30, interval=0.2)
        
        # Análisis estadístico de los datos
        show_advanced_stats(system_data)
        
    except KeyboardInterrupt:
        print("\nPrueba detenida.")
        
    except Exception as e:
        print(f"\nOcurrió un error: {e}")
        print("Tip: Instala psutil con 'pip install psutil'")