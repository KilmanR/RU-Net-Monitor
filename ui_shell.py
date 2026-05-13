import customtkinter as ctk
import sys
import os

# Добавляем корень проекта в путь поиска модулей
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import tkinter as tk
import threading
import time
import httpx

#  Словарь сервисов
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

class MonitorUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("RU-Net-Monitor v2.0")
        self.geometry("900x800")
        self.minsize(650, 600)
        
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("blue")
        
        self.grid_columnconfigure(1, weight=2)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.lbl_title = ctk.CTkLabel(self, text="🚀 RU-Net-Monitor v2.0", 
                                       font=ctk.CTkFont(size=24, weight="bold"))
        self.lbl_title.grid(row=0, column=0, columnspan=2, padx=20, pady=(15, 10), sticky="w")

        # ЛЕВАЯ ПАНЕЛЬ
        self.frame_left = ctk.CTkFrame(self, corner_radius=10, fg_color="gray15")
        self.frame_left.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        
        self.scroll_categories = ctk.CTkScrollableFrame(self.frame_left, width=280, label_text="Сервисы")
        self.scroll_categories.pack(fill="both", expand=True, padx=10, pady=(10, 5))
        
        self.widgets = {}
        self.build_categories()
        
        #  ИНФОРМАЦИОННАЯ ПАНЕЛЬ ВНИЗУ (вместо простого счётчика)
        self.frame_info = ctk.CTkFrame(self.frame_left, fg_color="#2c3e50", corner_radius=8)
        self.frame_info.pack(fill="x", padx=10, pady=10)
        
        # Счётчик
        self.lbl_counter = ctk.CTkLabel(
            self.frame_info, 
            text="Выбрано: 0", 
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#2ecc71"
        )
        self.lbl_counter.pack(pady=(5, 0))
        
        # Провайдер
        self.lbl_isp = ctk.CTkLabel(
            self.frame_info, 
            text="📡 Провайдер: определение...", 
            font=ctk.CTkFont(size=12),
            text_color="#3498db",
            wraplength=260
        )
        self.lbl_isp.pack(pady=5)
        
        # Кнопка быстрого теста скорости
        self.btn_speedtest = ctk.CTkButton(
            self.frame_info,
            text="⚡ Быстрый тест скорости",
            command=self.run_simple_speedtest,
            fg_color="#3498db",
            hover_color="#2980b9",
            height=35
        )
        self.btn_speedtest.pack(fill="x", padx=5, pady=5)
        
        # Результат speedtest
        self.lbl_speedtest_result = ctk.CTkLabel(
            self.frame_info,
            text="",
            font=ctk.CTkFont(size=11),
            text_color="#f39c12"
        )
        self.lbl_speedtest_result.pack(pady=(0, 5))

        # ПРАВАЯ ПАНЕЛЬ
        self.frame_right = ctk.CTkFrame(self, corner_radius=10)
        self.frame_right.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")
        self.frame_right.grid_rowconfigure(0, weight=1)
        self.frame_right.grid_columnconfigure(0, weight=1)

        self.text_log = ctk.CTkTextbox(self.frame_right, corner_radius=10, state="disabled", font=ctk.CTkFont(size=12))
        self.text_log.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        self.frame_controls = ctk.CTkFrame(self.frame_right, height=80, fg_color="transparent")
        self.frame_controls.grid(row=1, column=0, padx=10, pady=10, sticky="ew")
        self.frame_controls.grid_columnconfigure(0, weight=1)
        self.frame_controls.grid_columnconfigure(1, weight=1)

        frm_set = ctk.CTkFrame(self.frame_controls, fg_color="gray20", corner_radius=10)
        frm_set.grid(row=0, column=0, sticky="nsew", padx=5)
        
        ctk.CTkLabel(frm_set, text="Повторов:", font=ctk.CTkFont(size=13)).grid(row=0, column=0, padx=5, pady=5)
        self.var_repeats = ctk.IntVar(value=3)
        ctk.CTkEntry(frm_set, textvariable=self.var_repeats, width=50).grid(row=0, column=1, padx=5, pady=5)
        
        ctk.CTkLabel(frm_set, text="Таймаут (сек):", font=ctk.CTkFont(size=13)).grid(row=1, column=0, padx=5, pady=5)
        self.var_timeout = ctk.IntVar(value=3)
        ctk.CTkEntry(frm_set, textvariable=self.var_timeout, width=50).grid(row=1, column=1, padx=5, pady=5)

        self.btn_run = ctk.CTkButton(
            self.frame_controls, 
            text="▶ Запустить тест", 
            fg_color="#2ecc71", 
            hover_color="#27ae60",
            height=50,
            font=ctk.CTkFont(size=16, weight="bold"),
            command=self.start_test_thread
        )
        self.btn_run.grid(row=0, column=1, sticky="nsew", padx=5)

        # Определяем провайдера при старте
        self.after(100, self.detect_isp)

    def log(self, msg):
        self.text_log.configure(state="normal")
        self.text_log.insert("end", msg + "\n")
        self.text_log.see("end")
        self.text_log.configure(state="disabled")

    def update_counter(self):
        count = sum(1 for cat in self.widgets.values() for var in cat["checkboxes"].values() if var.get())
        self.lbl_counter.configure(text=f"Выбрано: {count} сервисов")

    def detect_isp(self):
        """Определяет провайдера по IP"""
        try:
            self.lbl_isp.configure(text="📡 Провайдер: определение...")
            response = httpx.get("http://ip-api.com/json/?fields=isp,query", timeout=5.0)
            data = response.json()
            isp = data.get("isp", "Неизвестно")
            ip = data.get("ip", "")
            self.lbl_isp.configure(text=f"📡 {isp}\n🌐 IP: {ip}")
        except Exception as e:
            self.lbl_isp.configure(text="📡 Провайдер: не определён")

    def run_simple_speedtest(self):
        """Простой тест скорости (скачивание 1MB файла)"""
        self.btn_speedtest.configure(state="disabled", text="⏳ Тестирование...")
        self.lbl_speedtest_result.configure(text="")
        
        def test():
            try:
                # Скачиваем 1MB тестовый файл (или любой большой файл)
                # Используем Яндекс (стабильный)
                start = time.time()
                response = httpx.get("https://yandex.ru", timeout=10)
                elapsed = time.time() - start
                
                # Примерный расчёт скорости (размер ответа / время)
                size_kb = len(response.content) / 1024
                speed_mbps = (size_kb * 8) / (elapsed * 1000)  # Мбит/с
                
                self.after(0, lambda: self.lbl_speedtest_result.configure(
                    text=f" {speed_mbps:.1f} Мбит/с | {elapsed*1000:.0f} мс"
                ))
            except Exception as e:
                self.after(0, lambda: self.lbl_speedtest_result.configure(text="❌ Ошибка теста"))
            finally:
                self.after(0, lambda: self.btn_speedtest.configure(state="normal", text="⚡ Быстрый тест скорости"))
        
        threading.Thread(target=test).start()

    def build_categories(self):
        for cat_name, services in CATEGORIES.items():
            cat_container = ctk.CTkFrame(self.scroll_categories, fg_color="transparent")
            cat_container.pack(fill="x", pady=3)
            
            # 🔧 УВЕЛИЧЕННЫЙ ШРИФТ И ЦВЕТ
            btn_toggle = ctk.CTkButton(
                cat_container, 
                text=f"▶ {cat_name}",
                command=lambda name=cat_name: self.toggle_section(name),
                fg_color="#34495e",  # Тёмно-синий
                hover_color="#4a6278",
                anchor="w",
                font=ctk.CTkFont(size=15, weight="bold"),  # Крупный жирный
                height=40,
                text_color="#ecf0f1"  # Светлый текст
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
                cb = ctk.CTkCheckBox(services_frame, text=svc, variable=var, command=self.update_counter,
                                     font=ctk.CTkFont(size=13))
                cb.pack(anchor="w", padx=15, pady=3)
                self.widgets[cat_name]["checkboxes"][svc] = var

    def toggle_section(self, cat_name):
        data = self.widgets[cat_name]
        data["is_open"] = not data["is_open"]
        if data["is_open"]:
            data["services_frame"].pack(fill="x", pady=3, padx=2)
            data["toggle_btn"].configure(text=f"▼ {cat_name}")
        else:
            data["services_frame"].pack_forget()
            data["toggle_btn"].configure(text=f"▶ {cat_name}")

    def start_test_thread(self):
        self.btn_run.configure(state="disabled", fg_color="gray50", text="⏳ Тестирую...")
        self.log("=" * 50)
        self.log("🚀 Запуск полного тестирования...")
        
        thread = threading.Thread(target=self.run_tests_logic)
        thread.start()

    def run_tests_logic(self):
        try:
            selected_names = []
            for cat_name, data in self.widgets.items():
                for svc, var in data["checkboxes"].items():
                    if var.get():
                        selected_names.append(svc)
            
            if not selected_names:
                self.log("⚠️ Ничего не выбрано! Отметьте сервисы.")
                self.after(0, self.reset_button)
                return

            from src.core import NetworkBenchmarker
            
            repeats = self.var_repeats.get()
            timeout = self.var_timeout.get()
            
            bench = NetworkBenchmarker(timeout=timeout)
            
            for name in selected_names:
                if name in SERVICE_MAP:
                    target = SERVICE_MAP[name]
                    self.log(f"\n🔍 Тестируем: {name} ({target['host']})")
                    
                    raw_results = []
                    for i in range(repeats):
                        time.sleep(0.2)
                        res = bench.measure_single(name=name, host=target["host"], path=target["path"])
                        raw_results.append(res)
                        
                    times = [r.total_time_ms for r in raw_results if r.success]
                    if times:
                        avg = sum(times) / len(times)
                        self.log(f"  ✅ Среднее: {avg:.1f} мс | Min: {min(times):.1f} | Max: {max(times):.1f}")
                    else:
                        self.log(f"  ❌ Не удалось получить данные")
            
            bench.close()
            self.log("\n" + "=" * 50)
            self.log("✅ Все тесты завершены!")
            
        finally:
            self.after(0, self.reset_button)

    def reset_button(self):
        self.btn_run.configure(state="normal", fg_color="#2ecc71", text="▶ Запустить тест")

if __name__ == "__main__":
    app = MonitorUI()
    app.mainloop()