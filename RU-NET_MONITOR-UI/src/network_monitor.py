# src/network_monitor.py — Мониторинг сервисов

import time
from typing import List, Dict
from src.core import NetworkBenchmarker, BenchmarkResult


class ServiceMonitor:
    """Мониторинг выбранных сервисов"""
    
    def __init__(self, timeout: float = 5.0):
        self.benchmarker = NetworkBenchmarker(timeout=timeout)
    
    def test_service(self, name: str, host: str, path: str = "/", repeats: int = 3) -> Dict:
        """Тестирует один сервис с подробным логом ошибок"""
        results = []
        last_error = None
        
        for i in range(repeats):
            time.sleep(0.2)
            try:
                res = self.benchmarker.measure_single(name=name, host=host, path=path)
                results.append(res)
                if res.error:
                    last_error = res.error
            except Exception as e:
                last_error = str(e)
                results.append(None)
        
        # Считаем статистику
        successful_times = [r.total_time_ms for r in results if r and r.success]
        
        if successful_times:
            return {
                'name': name,
                'host': host,
                'avg': sum(successful_times) / len(successful_times),
                'min': min(successful_times),
                'max': max(successful_times),
                'success': True,
                'results': results
            }
        else:
            # Возвращаем последнюю ошибку для лога
            return {
                'name': name,
                'host': host,
                'avg': 0,
                'min': 0,
                'max': 0,
                'success': False,
                'error': last_error or "Неизвестная ошибка",
                'results': results
            }
    def close(self):
        """Закрывает соединения"""
        if hasattr(self.benchmarker, 'close'):
            self.benchmarker.close()