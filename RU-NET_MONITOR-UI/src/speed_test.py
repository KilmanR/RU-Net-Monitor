# src/speed_test.py — Тест скорости интернета и определение провайдера

import httpx
import time
from typing import Tuple, Optional


class SpeedTester:
    """Класс для теста скорости и определения провайдера"""
    
    @staticmethod
    def detect_isp(timeout: float = 5.0) -> Tuple[str, str]:
        """
        Определяет провайдера и IP адрес.
        
        Returns:
            (isp_name, ip_address) - кортеж из названия провайдера и IP
        """
        try:
            response = httpx.get(
                "http://ip-api.com/json/?fields=isp,query",
                timeout=timeout
            )
            response.raise_for_status()
            data = response.json()
            
            isp = data.get("isp", "Неизвестно")
            ip = data.get("ip", "Не определён")
            
            return isp, ip
            
        except Exception as e:
            return "Не удалось определить", "-"
    
    @staticmethod
    def test_download_speed(url: str = "https://yandex.ru", timeout: float = 10.0) -> Tuple[float, float, int]:
        """
        Простой тест скорости скачивания.
        
        Args:
            url: URL для теста (должен отдавать большой файл или страницу)
            timeout: Максимальное время теста
            
        Returns:
            (speed_mbps, latency_ms, size_kb) - скорость в Мбит/с, задержка в мс, размер в КБ
        """
        try:
            start_time = time.time()
            
            response = httpx.get(url, timeout=timeout)
            response.raise_for_status()
            
            elapsed_time = time.time() - start_time
            size_bytes = len(response.content)
            size_kb = size_bytes / 1024
            
            # Скорость в Мбит/с
            speed_mbps = (size_kb * 8) / (elapsed_time * 1000)
            
            # Задержка (примерно)
            latency_ms = elapsed_time * 1000
            
            return speed_mbps, latency_ms, size_kb
            
        except Exception as e:
            return 0.0, 0.0, 0