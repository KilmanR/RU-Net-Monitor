# src/ui_components.py — UI компоненты (compact)
import customtkinter as ctk
from typing import Dict, Callable
from .service_registry import get_categories, get_all_services_flat
CATEGORIES, SERVICE_MAP = get_categories(), get_all_services_flat()
class CategoryBuilder:
    def __init__(self, parent_frame, on_checkbox_change: Callable):
        self.parent, self.on_change, self.widgets = parent_frame, on_checkbox_change, {}
    def build_all(self):
        for cat_name, services in CATEGORIES.items(): self._create_category(cat_name, services)
    def _create_category(self, cat_name: str, services: list):
        cat_container = ctk.CTkFrame(self.parent, fg_color="transparent"); cat_container.pack(fill="x", pady=3)
        btn_toggle = ctk.CTkButton(cat_container, text=f"▶ {cat_name}", command=lambda name=cat_name: self.toggle_section(name), fg_color="#34495e", hover_color="#4a6278", anchor="w", font=ctk.CTkFont(size=15, weight="bold"), height=40, text_color="#ecf0f1")
        btn_toggle.pack(fill="x", pady=1); services_frame = ctk.CTkFrame(cat_container, fg_color="gray20")
        self.widgets[cat_name] = {"toggle_btn": btn_toggle, "services_frame": services_frame, "is_open": False, "checkboxes": {}}
        for svc in services:
            var = ctk.BooleanVar(value=False); cb = ctk.CTkCheckBox(services_frame, text=svc, variable=var, command=self.on_change, font=ctk.CTkFont(size=13))
            cb.pack(anchor="w", padx=15, pady=3); self.widgets[cat_name]["checkboxes"][svc] = var
    def toggle_section(self, cat_name: str):
        data = self.widgets[cat_name]; data["is_open"] = not data["is_open"]
        if data["is_open"]: data["services_frame"].pack(fill="x", pady=3, padx=2); data["toggle_btn"].configure(text=f"▼ {cat_name}")
        else: data["services_frame"].pack_forget(); data["toggle_btn"].configure(text=f"▶ {cat_name}")
    def get_selected_services(self) -> list:
        selected = []
        for cat_data in self.widgets.values():
            for svc, var in cat_data["checkboxes"].items():
                if var.get(): selected.append(svc)
        return selected
    def count_selected(self) -> int: return len(self.get_selected_services())