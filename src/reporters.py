# src/reporters.py — модуль для вывода результатов и статистики

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from typing import List
import statistics
import csv
from datetime import datetime
from pathlib import Path
from .core import BenchmarkResult

console = Console()

def print_benchmark_stats(service_name: str, results: List[BenchmarkResult]):
    """
    Анализирует результаты повторов и выводит статистику.
    """
    if not results:
        console.print(f"⚠️ Нет данных для {service_name}", style="red")
        return

    # Берём только успешные замеры для статистики
    successful = [r for r in results if r.success]
    
    if not successful:
        console.print(Panel(f"❌ Все запросы к {service_name} провалились", style="red"))
        return

    times = [r.total_time_ms for r in successful]
    avg_t = statistics.mean(times)
    min_t = min(times)
    max_t = max(times)
    # Джиттер (стандартное отклонение). Если замер 1, джиттер = 0
    jitter = statistics.stdev(times) if len(times) > 1 else 0.0

    table = Table(title=f"📊 {service_name}", show_header=True, header_style="bold magenta")
    table.add_column("Метрика", style="cyan")
    table.add_column("Значение", justify="right")
    table.add_column("Оценка")

    def get_quality(val, low=150, high=400):
        if val < low: return Text("🟢 Отлично", style="green")
        elif val < high: return Text("🟡 Нормально", style="yellow")
        return Text("🔴 Плохо", style="red")

    table.add_row("Среднее время", f"{avg_t:.1f} мс", get_quality(avg_t))
    table.add_row("Минимум", f"{min_t:.1f} мс", "")
    table.add_row("Максимум", f"{max_t:.1f} мс", "")
    table.add_row("Джиттер (σ)", f"{jitter:.1f} мс", get_quality(jitter, low=10, high=30))
    table.add_row("Успешных / Всего", f"{len(successful)} / {len(results)}", "")

    console.print(table)

def save_to_csv(all_results: dict, network_name: str = "default"):
    """
    Сохраняет результаты в отдельные CSV файлы для каждого сервиса.
    Каждый файл дополняется новыми данными (append mode).
    
    Args:
        all_results: dict вида {"Название сервиса": [BenchmarkResult, ...], ...}
        network_name: имя сети/оператора (для сравнения Билайн vs Сбер)
    """
    # Создаём папку results, если нет
    results_dir = Path("results")
    results_dir.mkdir(exist_ok=True)
    
    # Словарь для маппинга имён сервисов в имена файлов
    # Заменяем пробелы и спецсимволы на подчёркивания
    def sanitize_name(name: str) -> str:
        return name.lower().replace(" ", "_").replace(".", "").replace("(", "").replace(")", "")
    
    for service_name, results in all_results.items():
        # Формируем имя файла
        safe_name = sanitize_name(service_name)
        filename = results_dir / f"{safe_name}.csv"
        
        # Проверяем, существует ли файл (нужен ли заголовок)
        file_exists = filename.exists()
        
        # Открываем в режиме append ('a')
        with open(filename, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # Пишем заголовок только если файл новый
            if not file_exists:
                writer.writerow([
                    "Timestamp",
                    "Network",        # ← Новая колонка для оператора
                    "Total_Time_ms",
                    "Status_Code",
                    "Success",
                    "Error"
                ])
            
            # Записываем все результаты
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            for res in results:
                writer.writerow([
                    timestamp,
                    network_name,
                    f"{res.total_time_ms:.2f}",
                    res.status_code,
                    res.success,
                    res.error
                ])
        
        console.print(f"💾 {service_name}: +{len(results)} записей → {filename}", style="dim")
    
    console.print(f"\n✅ Все результаты сохранены (сеть: {network_name})", style="bold green")