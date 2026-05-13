# src/service_registry.py — Реестр сервисов (загрузка из JSON)

import json
from pathlib import Path
from typing import Dict, List, Optional


class ServiceRegistry:
    """Реестр всех доступных сервисов для мониторинга"""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Инициализация реестра.
        
        Args:
            config_path: Путь к JSON файлу с конфигурацией.
                        По умолчанию ищет services_config.json в той же папке
        """
        if config_path is None:
            config_path = Path(__file__).parent / "services_config.json"
        
        self.config_path = Path(config_path)
        self._config: Dict = {}
        self._load_config()
    
    def _load_config(self):
        """Загружает конфигурацию из JSON файла"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self._config = json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"Конфигурация не найдена: {self.config_path}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Ошибка в JSON конфигурации: {e}")
    
    def get_categories(self) -> List[str]:
        """Возвращает список категорий"""
        return list(self._config.keys())
    
    def get_services_by_category(self, category: str) -> Dict[str, Dict]:
        """
        Возвращает все сервисы указанной категории.
        
        Args:
            category: Название категории (например, "Банки")
            
        Returns:
            Dict с сервисами: {"Название": {"host": "...", "path": "...", ...}}
        """
        return self._config.get(category, {})
    
    def get_service_config(self, service_name: str) -> Optional[Dict]:
        """
        Возвращает конфигурацию конкретного сервиса.
        
        Args:
            service_name: Название сервиса (например, "Сбербанк Онлайн")
            
        Returns:
            Dict с конфигом или None, если сервис не найден
        """
        for category, services in self._config.items():
            if service_name in services:
                return services[service_name]
        return None
    
    def get_all_services_flat(self) -> Dict[str, Dict]:
        """
        Возвращает все сервисы в одном словаре (плоская структура).
        
        Returns:
            Dict: {"Сбербанк Онлайн": {...}, "Т-Банк": {...}, ...}
        """
        flat = {}
        for category, services in self._config.items():
            flat.update(services)
        return flat
    
    def get_service_host(self, service_name: str) -> Optional[str]:
        """Быстрое получение хоста сервиса"""
        config = self.get_service_config(service_name)
        return config.get("host") if config else None
    
    def get_services_for_ui(self) -> Dict[str, List[str]]:
        """
        Возвращает структуру для UI (категория -> список названий).
        
        Returns:
            Dict: {"Банки": ["Сбербанк Онлайн", "Т-Банк", ...], ...}
        """
        return {
            category: list(services.keys())
            for category, services in self._config.items()
        }


#  Глобальный экземляр для удобного доступа
registry = ServiceRegistry()


# 🔧 Функции-помощники для быстрого доступа
def get_all_services() -> Dict[str, Dict]:
    """Получить все сервисы (плоский словарь)"""
    return registry.get_all_services_flat()


def get_categories() -> Dict[str, List[str]]:
    """Получить категории и сервисы для UI"""
    return registry.get_services_for_ui()


def get_service_info(name: str) -> Optional[Dict]:
    """Получить инфо о сервисе"""
    return registry.get_service_config(name)