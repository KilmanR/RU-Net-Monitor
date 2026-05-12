# main.py — основной скрипт запуска бенчмарка
# Автоматически определяет провайдера, замеряет скорость сервисов,
# выводит статистику и сохраняет результаты в CSV

import config
from src.core import NetworkBenchmarker, get_current_isp
from src.reporters import print_benchmark_stats, save_to_csv
from rich.console import Console


def main():
    """
    Основная функция бенчмарка.
    
    Последовательность действий:
    1. Определяет текущего интернет-провайдера
    2. Замеряет скорость каждого сервиса из конфига (N повторов)
    3. Выводит статистику (среднее/мин/макс/джиттер)
    4. Сохраняет результаты в отдельные CSV файлы
    """
    console = Console()
    
    # 🌐 Автоматически определяем провайдера по текущему IP
    network_name = get_current_isp()
    console.print(f"📡 Обнаруженная сеть: {network_name}", style="bold cyan")
    
    # Создаём замерщик с таймаутом из конфига
    bench = NetworkBenchmarker(timeout=config.config.default_timeout)
    
    # Словарь для сбора всех результатов (сервис → список замеров)
    all_results = {}
    
    # Проходимся по всем целям из конфигурации
    for target in config.config.targets:
        console.print(
            f"\n🔍 Проверка: {target.name} ({config.config.repeats} повторов)...",
            style="italic"
        )
        
        # Делаем N повторов для статистической значимости
        raw_results = []
        for i in range(config.config.repeats):
            console.print(f"  [{i+1}/{config.config.repeats}] Замер...", style="dim")
            
            # Замеряем скорость
            res = bench.measure_single(
                name=target.name,
                host=target.host,
                path=target.path,
                port=target.port
            )
            raw_results.append(res)
            
        # Сохраняем результаты для экспорта
        all_results[target.name] = raw_results
        
        # Выводим статистику по сервису (среднее/мин/макс/джиттер)
        print_benchmark_stats(target.name, raw_results)
        
    # Корректно закрываем соединения
    bench.close()
    
    # 💾 Сохраняем результаты в CSV (отдельный файл на каждый сервис)
    save_to_csv(all_results, network_name=network_name)
    
    console.print("\n✅ Все замеры завершены.", style="bold green")


if __name__ == "__main__":
    main()