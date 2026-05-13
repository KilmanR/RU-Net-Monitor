# src/ui_components.py — UI компоненты
# src/ui_components.py — UI компоненты

import customtkinter as ctk
from typing import Dict, Callable
from src.service_registry import get_categories, get_all_services


# 📋 Получаем данные из реестра
CATEGORIES = get_categories()
SERVICE_MAP = get_all_services()

# 📋 Конфигурация категорий и сервисов
SERVICE_MAP = {
    "Сбербанк Онлайн": {"host": "online.sberbank.ru", "path": "/"},
    "Т-Банк": {"host": "www.tinkoff.ru", "path": "/"},
    "Альфа-Банк": {"host": "alfabank.ru", "path": "/"},
    "ВТБ Онлайн": {"host": "vtb.ru", "path": "/"},
    "Газпромбанк": {"host": "gazprombank.ru", "path": "/"},
    "Почта Mail.ru": {"host": "mail.ru", "path": "/"},
    "Почта Рамблер": {"host": "mail.rambler.ru", "path": "/"},
    "Яндекс.Почта": {"host": "mail.yandex.ru", "path": "/"},
    "VK Почта": {"host": "mail.vk.com", "path": "/"},
    "Яндекс.Диск": {"host": "disk.yandex.ru", "path": "/"},
    "Облако Mail.ru": {"host": "cloud.mail.ru", "path": "/"},
    "СберДиск": {"host": "sberbank.ru", "path": "/"},
    "VK Облако": {"host": "cloud.vk.com", "path": "/"},
    "Мессенджер Макс": {"host": "web.max.ru", "path": "/"},
    "VK Мессенджер": {"host": "vk.com", "path": "/"},
    "ICQ New": {"host": "icq.com", "path": "/"},
    "Viber": {"host": "viber.com", "path": "/"},
    "WhatsApp Web": {"host": "web.whatsapp.com", "path": "/"},
    "Яндекс.Музыка": {"host": "music.yandex.ru", "path": "/"},
    "VK Музыка": {"host": "vk.com", "path": "/audio"},
    "RuTube": {"host": "rutube.ru", "path": "/"},
    "VK Видео": {"host": "vk.com", "path": "/video"},
    "Яндекс.Дзен": {"host": "dzen.ru", "path": "/"},
    "GigaChat": {"host": "developers.sber.ru", "path": "/"},
    "Алиса": {"host": "alice.yandex.ru", "path": "/"},
    "Qwen AI": {"host": "chat.qwen.ai", "path": "/"},
    "DeepSeek": {"host": "chat.deepseek.com", "path": "/"},
    "YandexGPT": {"host": "cloud.yandex.ru", "path": "/"}
}

CATEGORIES = {
    "Банки": list(SERVICE_MAP.keys())[:5],
    "Почта": list(SERVICE_MAP.keys())[5:9],
    "Хранилища": list(SERVICE_MAP.keys())[9:13],
    "Мессенджеры": list(SERVICE_MAP.keys())[13:18],
    "Медиа": list(SERVICE_MAP.keys())[18:23],
    "ИИ": list(SERVICE_MAP.keys())[23:]
}


class CategoryBuilder:
    """Создатель раскрывающихся категорий"""
    
    def __init__(self, parent_frame, on_checkbox_change: Callable):
        self.parent = parent_frame
        self.on_change = on_checkbox_change
        self.widgets: Dict = {}
    
    def build_all(self):
        """Создаёт все категории"""
        for cat_name, services in CATEGORIES.items():
            self._create_category(cat_name, services)
    
    def _create_category(self, cat_name: str, services: list):
        """Создаёт одну категорию"""
        cat_container = ctk.CTkFrame(self.parent, fg_color="transparent")
        cat_container.pack(fill="x", pady=3)
        
        btn_toggle = ctk.CTkButton(
            cat_container,
            text=f"▶ {cat_name}",
            command=lambda name=cat_name: self.toggle_section(name),
            fg_color="#34495e",
            hover_color="#4a6278",
            anchor="w",
            font=ctk.CTkFont(size=15, weight="bold"),
            height=40,
            text_color="#ecf0f1"
        )
        btn_toggle.pack(fill="x", pady=1)
        
        services_frame = ctk.CTkFrame(cat_container, fg_color="gray20")
        
        self.widgets[cat_name] = {
            "toggle_btn": btn_toggle,
            "services_frame": services_frame,
            "is_open": False,
            "checkboxes": {}
        }
        
        for svc in services:
            var = ctk.BooleanVar(value=False)
            cb = ctk.CTkCheckBox(
                services_frame,
                text=svc,
                variable=var,
                command=self.on_change,
                font=ctk.CTkFont(size=13)
            )
            cb.pack(anchor="w", padx=15, pady=3)
            self.widgets[cat_name]["checkboxes"][svc] = var
    
    def toggle_section(self, cat_name: str):
        """Открывает/закрывает раздел"""
        data = self.widgets[cat_name]
        data["is_open"] = not data["is_open"]
        
        if data["is_open"]:
            data["services_frame"].pack(fill="x", pady=3, padx=2)
            data["toggle_btn"].configure(text=f"▼ {cat_name}")
        else:
            data["services_frame"].pack_forget()
            data["toggle_btn"].configure(text=f"▶ {cat_name}")
    
    def get_selected_services(self) -> list:
        """Возвращает список выбранных сервисов"""
        selected = []
        for cat_data in self.widgets.values():
            for svc, var in cat_data["checkboxes"].items():
                if var.get():
                    selected.append(svc)
        return selected
    
    def count_selected(self) -> int:
        """Считает количество выбранных"""
        return len(self.get_selected_services())