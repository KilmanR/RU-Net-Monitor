# src/core.py — ядро замера (compact)
import httpx
from dataclasses import dataclass
@dataclass
class BenchmarkResult:
    name: str; host: str; total_time_ms: float; status_code: int; success: bool; error: str = ""
class NetworkBenchmarker:
    def __init__(self, timeout: float = 5.0):
        self.timeout = timeout
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36", "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8", "Accept-Language": "ru-RU,ru;q=0.9,en;q=0.7"}
        self.client = httpx.Client(headers=headers, timeout=httpx.Timeout(timeout), follow_redirects=True, verify=True)
    def measure_single(self, name: str, host: str, path: str = "/", port: int = 443) -> BenchmarkResult:
        url = f"https://{host}:{port}{path}"
        try:
            response = self.client.get(url)
            elapsed_ms = response.elapsed.total_seconds() * 1000
            return BenchmarkResult(name=name, host=host, total_time_ms=elapsed_ms, status_code=response.status_code, success=response.status_code < 400)
        except httpx.RequestError as e:
            return BenchmarkResult(name=name, host=host, total_time_ms=0.0, status_code=0, success=False, error=str(e))
    def close(self): self.client.close()
def get_current_isp(timeout: float = 3.0) -> str:
    try:
        response = httpx.get("http://ip-api.com/json/?fields=isp,org,as", timeout=timeout); response.raise_for_status(); data = response.json()
        isp_name = data.get("isp") or data.get("org") or data.get("as")
        return isp_name if isp_name else "Unknown_ISP"
    except: return "Unknown_Network"