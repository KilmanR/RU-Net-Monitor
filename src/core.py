# src/core.py — ядро замера (простой режим)

import httpx
from dataclasses import dataclass
from typing import List

# ============================================================
# 🔧 БЛОК ОТЛАДКИ (включи/выключи одной строчкой)
# ============================================================
DEBUG = False  # ← поставь True, чтобы видеть каждое движение в консоли

def _log(msg: str):
    """Внутренняя функция для вывода отладочных сообщений"""
    if DEBUG:
        print(f"[DEBUG] {msg}")
# ============================================================


@dataclass
class BenchmarkResult:
    """Хранит результат замера одного сервиса"""
    name: str          # Название из конфига (например, "Яндекс.Taxi")
    host: str          # Домен
    total_time_ms: float  # Общее время запроса в миллисекундах
    status_code: int   # HTTP-код ответа (200, 301, 404 и т.д.)
    success: bool      # True если код < 400
    error: str = ""    # Текст ошибки, если запрос провалился


class NetworkBenchmarker:
    """
    Простой замерщик сетевых запросов.
    Использует httpx для отправки GET-запросов и фиксации общего времени отклика.
    """
    
    def __init__(self, timeout: float = 5.0):
        _log("Инициализация NetworkBenchmarker")
        
        # Создаём клиент один раз и переиспользуем его (keep-alive соединения)
        self.client = httpx.Client(
            timeout=httpx.Timeout(timeout),
            follow_redirects=True,  # Автоматически переходим по редиректам (301/302)
            http2=False             # Пока отключаем HTTP/2 для стабильности замеров
        )
        _log(f"Клиент создан. Timeout: {timeout}с, HTTP/2: False")
    
    def measure_single(self, name: str, host: str, path: str = "/", port: int = 443) -> BenchmarkResult:
        """
        Делает один запрос к цели и возвращает результат.
        """
        url = f"https://{host}:{port}{path}"
        _log(f"▶️  Замер: {name} ({url})")
        
        try:
            _log("📤 Отправка GET-запроса...")
            response = self.client.get(url)
            
            _log(f"📥 Ответ получен. Статус: {response.status_code}")
            
            # response.elapsed — встроенный таймер httpx (точнее, чем time.perf_counter)
            elapsed_ms = response.elapsed.total_seconds() * 1000
            _log(f"⏱️  Время отклика: {elapsed_ms:.2f} мс")
            
            result = BenchmarkResult(
                name=name,
                host=host,
                total_time_ms=elapsed_ms,
                status_code=response.status_code,
                success=response.status_code < 400
            )
            
            _log(f"✅ Результат сформирован: success={result.success}")
            return result
            
        except httpx.RequestError as e:
            # Сетевая ошибка: таймаут, DNS не найден, соединение сброшено
            _log(f"❌ Ошибка сети: {e}")
            return BenchmarkResult(
                name=name, host=host, total_time_ms=0.0,
                status_code=0, success=False, error=str(e)
            )
            
    def close(self):
        """Корректно закрываем пул соединений"""
        _log("🔚 Закрытие клиента и освобождение ресурсов")
        self.client.close()

def get_current_isp(timeout: float = 3.0) -> str:
    """
    Автоматически определяет текущего интернет-провайдера.
    Использует бесплатный ip-api.com (не требует ключей).
    """
    try:
        # Быстрый запрос к публичному API
        response = httpx.get(
            "http://ip-api.com/json/?fields=isp,org,as", 
            timeout=timeout
        )
        response.raise_for_status()
        data = response.json()
        
        # Берём самое читаемое поле
        isp_name = data.get("isp") or data.get("org") or data.get("as")
        return isp_name if isp_name else "Unknown_ISP"
        
    except Exception:
        # Если API недоступен или нет сети — не ломаем бенчмарк
        return "Unknown_Network"