import psutil
import time
import statistics
import math

def get_correlation(x, y):
    """
    Calcula el coeficiente de correlación de Pearson entre dos listas.
    """
    if len(x) != len(y) or len(x) < 2:
        return 0
    
    n = len(x)
    mean_x = sum(x) / n
    mean_y = sum(y) / n
    
    num = sum((x[i] - mean_x) * (y[i] - mean_y) for i in range(n))
    den_x = sum((x[i] - mean_x)**2 for i in range(n))
    den_y = sum((y[i] - mean_y)**2 for i in range(n))
    
    den = math.sqrt(den_x * den_y)
    if den == 0:
        return 0
    return num / den

def collect_advanced_data(samples=30, interval=0.2):
    """
    Recolecta múltiples métricas del sistema.
    """
    print(f"Recolectando datos avanzados ({samples} muestras)...")
    data = {
        'cpu_overall': [],
        'cpu_cores': [], # Lista de listas
        'ram_percent': [],
        'disk_io': [] # Bytes leídos/escritos (delta)
    }
    
    # Inicializar cores
    num_cores = psutil.cpu_count()
    for _ in range(num_cores):
        data['cpu_cores'].append([])

    last_disk = psutil.disk_io_counters()
    
    for _ in range(samples):
        # 1. CPU Overall
        data['cpu_overall'].append(psutil.cpu_percent(interval=interval))
        
        # 2. CPU Per Core
        cores_usage = psutil.cpu_percent(percpu=True)
        for i, val in enumerate(cores_usage):
            data['cpu_cores'][i].append(val)
            
        # 3. RAM usage
        data['ram_percent'].append(psutil.virtual_memory().percent)
        
        # 4. Disk IO (Delta)
        current_disk = psutil.disk_io_counters()
        delta_io = (current_disk.read_bytes + current_disk.write_bytes) - \
                   (last_disk.read_bytes + last_disk.write_bytes)
        data['disk_io'].append(delta_io / 1024) # KB
        last_disk = current_disk
        
    return data

def show_advanced_stats(data):
    """
    Muestra análisis estadístico avanzado.
    """
    print("\n" + "="*60)
    print("   MONITOR DE SISTEMA AVANZADO - ANÁLISIS ESTADÍSTICO")
    print("="*60)

    # 1. CPU Overall Analysis
    cpu = data['cpu_overall']
    print(f"\n[CPU TOTAL] (n={len(cpu)})")
    print(f"  Media: {statistics.mean(cpu):.2f}% | Mediana: {statistics.median(cpu):.2f}%")
    
    # Percentiles (Manual o usando quantiles si disponible en Python 3.8+)
    p25, p50, p75 = statistics.quantiles(cpu, n=4)
    print(f"  Percentiles: P25={p25:.1f}%, P50={p50:.1f}%, P75={p75:.1f}%")
    print(f"  Desviación Estándar: {statistics.stdev(cpu):.4f}")

    # 2. Per-Core Skewness (Análisis de balanceo)
    print("\n[ANÁLISIS DE CARGA POR NÚCLEO]")
    core_means = [statistics.mean(core) for core in data['cpu_cores']]
    max_core = max(core_means)
    min_core = min(core_means)
    print(f"  Media más alta (Core {core_means.index(max_core)}): {max_core:.2f}%")
    print(f"  Media más baja  (Core {core_means.index(min_core)}): {min_core:.2f}%")
    print(f"  Rango Inter-núcleos (Variable de balanceo): {max_core - min_core:.2f}%")

    # 3. Correlation CPU vs RAM
    ram = data['ram_percent']
    corr_cpu_ram = get_correlation(cpu, ram)
    print(f"\n[CORRELACIÓN]")
    print(f"  Coeficiente de Pearson (CPU vs RAM): {corr_cpu_ram:.4f}")
    if abs(corr_cpu_ram) > 0.7:
        type_corr = "Fuerte"
    elif abs(corr_cpu_ram) > 0.3:
        type_corr = "Moderada"
    else:
        type_corr = "Débil o inexistente"
    print(f"  Interpretación: Correlación {type_corr}")

    # 4. DISK IO Analysis
    disk = data['disk_io']
    print(f"\n[ACTIVIDAD DE DISCO (KB/intervalo)]")
    print(f"  Máximo: {max(disk):.2f} KB | Mínimo: {min(disk):.2f} KB")
    print(f"  Varianza: {statistics.variance(disk):.2f}")

    # Histograma de CPU
    print("\n--- Distribución de Frecuencia CPU Total ---")
    buckets = range(0, 101, 10)
    for i in range(len(buckets)-1):
        low, high = buckets[i], buckets[i+1]
        count = len([x for x in cpu if low <= x < high])
        if high == 100: count += len([x for x in cpu if x == 100])
        print(f"{low:3}-{high:3}% | {'#' * count} ({count})")

if __name__ == "__main__":
    try:
        # Recolección
        system_data = collect_advanced_data(samples=30, interval=0.2)
        
        # Análisis
        show_advanced_stats(system_data)
        
    except KeyboardInterrupt:
        print("\nPrueba detenida.")
    except Exception as e:
        print(f"\nOcurrió un error: {e}")
        print("Tip: Instala psutil con 'pip install psutil'")
