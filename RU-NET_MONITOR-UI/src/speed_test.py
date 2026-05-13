# src/speed_test.py — Тест скорости (Final Compact)
import httpx, time
from typing import Tuple
class SpeedTester:
    @staticmethod
    def detect_isp(timeout: float = 5.0) -> Tuple[str, str]:
        try:
            r = httpx.get("http://ip-api.com/json/?fields=isp,query", timeout=timeout); r.raise_for_status(); d = r.json()
            return d.get("isp", "Неизвестно"), d.get("query", "Не определён")
        except: return "Не удалось определить", "-"
    
    @staticmethod
    def test_download_speed(url: str = "https://speed.cloudflare.com/__down?bytes=25000000", timeout: float = 15.0) -> Tuple[float, float, int]:
        try:
            start = time.time()
            r = httpx.get(url, timeout=timeout, headers={"User-Agent": "Mozilla/5.0 (RU-Net-Monitor)"}, follow_redirects=True); r.raise_for_status()
            elapsed = time.time() - start; size_mb = len(r.content) / 1024 / 1024
            return (size_mb * 8) / elapsed, elapsed * 1000, int(len(r.content) / 1024)
        except: return 0.0, 0.0, 0