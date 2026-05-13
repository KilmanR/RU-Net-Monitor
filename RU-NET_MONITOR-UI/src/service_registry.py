# src/service_registry.py — Реестр сервисов (compact)
import json
from pathlib import Path
from typing import Dict, List, Optional

class ServiceRegistry:
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = Path(config_path) if config_path else Path(__file__).parent / "services_config.json"
        self._config: Dict = {}
        self._load_config()
    def _load_config(self):
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f: self._config = json.load(f)
        except FileNotFoundError: raise FileNotFoundError(f"Конфигурация не найдена: {self.config_path}")
        except json.JSONDecodeError as e: raise ValueError(f"Ошибка в JSON конфигурации: {e}")
    def get_categories(self) -> List[str]: return list(self._config.keys())
    def get_services_by_category(self, category: str) -> Dict[str, Dict]: return self._config.get(category, {})
    def get_service_config(self, service_name: str) -> Optional[Dict]:
        for category, services in self._config.items():
            if service_name in services: return services[service_name]
        return None
    def get_all_services_flat(self) -> Dict[str, Dict]:
        flat = {}
        for category, services in self._config.items(): flat.update(services)
        return flat
    def get_service_host(self, service_name: str) -> Optional[str]:
        config = self.get_service_config(service_name)
        return config.get("host") if config else None
    def get_services_for_ui(self) -> Dict[str, List[str]]:
        return {category: list(services.keys()) for category, services in self._config.items()}

registry = ServiceRegistry()

def get_all_services() -> Dict[str, Dict]: return registry.get_all_services_flat()
def get_all_services_flat() -> Dict[str, Dict]: return registry.get_all_services_flat()
def get_categories() -> Dict[str, List[str]]: return registry.get_services_for_ui()
def get_service_info(name: str) -> Optional[Dict]: return registry.get_service_config(name)