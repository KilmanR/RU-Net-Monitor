# src/network_monitor.py — Мониторинг сервисов (compact)
import time, random
from typing import Dict
from .core import NetworkBenchmarker, BenchmarkResult
class ServiceMonitor:
    def __init__(self, timeout: float = 5.0): self.benchmarker = NetworkBenchmarker(timeout=timeout)
    def test_service(self, name: str, host: str, path: str = "/", repeats: int = 3) -> Dict:
        results, last_error = [], None
        for _ in range(repeats):
            time.sleep(random.uniform(1.0, 3.0))
            try:
                res = self.benchmarker.measure_single(name=name, host=host, path=path); results.append(res)
                if res.error: last_error = res.error
            except Exception as e: last_error = str(e); results.append(None)
        successful = [r.total_time_ms for r in results if r and r.success]
        if successful:
            return {'name': name, 'host': host, 'avg': sum(successful)/len(successful), 'min': min(successful), 'max': max(successful), 'success': True, 'results': results}
        else:
            return {'name': name, 'host': host, 'avg': 0, 'min': 0, 'max': 0, 'success': False, 'error': last_error or "Неизвестная ошибка", 'results': results}
    def close(self):
        if hasattr(self.benchmarker, 'close'): self.benchmarker.close()