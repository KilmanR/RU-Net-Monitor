# config.py — настройки и цели замеров

from dataclasses import dataclass, field
from typing import List


@dataclass
class TargetConfig:
    """Конфигурация одной цели для замера"""
    name: str
    host: str
    path: str = "/"
    port: int = 443
    timeout: float = 5.0


@dataclass
class GlobalConfig:
    """Глобальные настройки"""
    repeats: int = 5
    default_timeout: float = 5.0
    verbose: bool = False
    
    targets: List[TargetConfig] = field(default_factory=list)
    
    def __post_init__(self):
        if not self.targets:
            self.targets = [
                # === Мессенджеры и коммуникации ===
                TargetConfig(
                    name="Яндекс.Такси",
                    host="taxi.yandex.ru",
                    path="/",
                    port=443
                ),
                TargetConfig(
                    name="Мессенджер Макс",
                    host="web.max.ru",
                    path="/",
                    port=443
                ),
                TargetConfig(
                    name="VK (мессенджер)",
                    host="vk.com",
                    path="/",
                    port=443
                ),
                
                # === AI и ассистенты ===
                TargetConfig(
                    name="Qwen AI (чат)",
                    host="chat.qwen.ai",
                    path="/",
                    port=443
                ),
                
                # === Разработка и код ===
                TargetConfig(
                    name="GitHub",
                    host="github.com",
                    path="/",
                    port=443
                ),
                TargetConfig(
                    name="GitVerse (РФ)",
                    host="gitverse.ru",
                    path="/",
                    port=443
                ),
                
                # === Банки и финансы ===
                TargetConfig(
                    name="Сбербанк Онлайн",
                    host="online.sberbank.ru",
                    path="/",
                    port=443
                ),
                
                # === Почта и медиа ===
                TargetConfig(
                    name="Почта Рамблер",
                    host="mail.rambler.ru",
                    path="/",
                    port=443
                ),
                TargetConfig(
                    name="RuTube",
                    host="rutube.ru",
                    path="/",
                    port=443
                ),
            ]


config = GlobalConfig()