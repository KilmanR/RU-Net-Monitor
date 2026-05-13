# ui_shell.py — Главный файл приложения

import customtkinter as ctk
import threading
from src.ui_components import CategoryBuilder, SERVICE_MAP
from src.speed_test import SpeedTester
from src.network_monitor import ServiceMonitor


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

        # Заголовок
        self.lbl_title = ctk.CTkLabel(
            self, text="🚀 RU-Net-Monitor v2.0",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        self.lbl_title.grid(row=0, column=0, columnspan=2, padx=20, pady=(15, 10), sticky="w")

        # ЛЕВАЯ ПАНЕЛЬ
        self.frame_left = ctk.CTkFrame(self, corner_radius=10, fg_color="gray15")
        self.frame_left.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        
        self.scroll_categories = ctk.CTkScrollableFrame(
            self.frame_left, width=280, label_text="Сервисы"
        )
        self.scroll_categories.pack(fill="both", expand=True, padx=10, pady=(10, 5))
        
        # Создаём категории через билдер
        self.category_builder = CategoryBuilder(
            self.scroll_categories,
            on_checkbox_change=self.update_counter
        )
        self.category_builder.build_all()
        
        # ИНФОРМАЦИОННАЯ ПАНЕЛЬ
        self.frame_info = ctk.CTkFrame(self.frame_left, fg_color="#2c3e50", corner_radius=8)
        self.frame_info.pack(fill="x", padx=10, pady=10)
        
        self.lbl_counter = ctk.CTkLabel(
            self.frame_info,
            text="Выбрано: 0",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#2ecc71"
        )
        self.lbl_counter.pack(pady=(5, 0))
        
        self.lbl_isp = ctk.CTkLabel(
            self.frame_info,
            text="📡 Провайдер: определение...",
            font=ctk.CTkFont(size=12),
            text_color="#3498db",
            wraplength=260
        )
        self.lbl_isp.pack(pady=5)
        
        self.btn_speedtest = ctk.CTkButton(
            self.frame_info,
            text="⚡ Быстрый тест скорости",
            command=self.run_simple_speedtest,
            fg_color="#3498db",
            hover_color="#2980b9",
            height=35
        )
        self.btn_speedtest.pack(fill="x", padx=5, pady=5)
        
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

        self.text_log = ctk.CTkTextbox(
            self.frame_right, corner_radius=10, state="disabled",
            font=ctk.CTkFont(size=12)
        )
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
        count = self.category_builder.count_selected()
        self.lbl_counter.configure(text=f"Выбрано: {count} сервисов")

    def detect_isp(self):
        """Определяет провайдера и IP"""
        def _detect():
            try:
                import httpx
                response = httpx.get(
                    "http://ip-api.com/json/?fields=isp,query",
                    timeout=5.0
                )
                data = response.json()
                isp = data.get("isp", "Неизвестно")
                ip = data.get("query", "Не определён")
                self.after(0, lambda: self.lbl_isp.configure(text=f"📡 {isp}\n🌐 IP: {ip}"))
            except Exception as e:
                self.after(0, lambda: self.lbl_isp.configure(text=f"📡 Ошибка определения\n🌐 IP: -"))
        
        threading.Thread(target=_detect, daemon=True).start()


    def run_simple_speedtest(self):
        """Тест скорости скачивания"""
        self.btn_speedtest.configure(state="disabled", text="⏳ Тестирование...")
        self.lbl_speedtest_result.configure(text="")
        
        def _test():
            try:
                import httpx
                import time
                
                self.after(0, lambda: self.log("📊 Запуск быстрого теста скорости..."))
                
                # Тестируем пинг и загрузку
                start = time.time()
                response = httpx.get("https://yandex.ru", timeout=10, follow_redirects=True)
                elapsed = time.time() - start
                
                # Получаем размер ответа
                size_bytes = len(response.content)
                size_kb = size_bytes / 1024
                size_mb = size_kb / 1024
                
                # Считаем скорость: (размер в битах) / (время в секундах)
                speed_mbps = (size_kb * 8) / (elapsed * 1000)
                
                result_text = f"⚡ {speed_mbps:.1f} Мбит/с | {elapsed*1000:.0f} мс"
                self.after(0, lambda: self.lbl_speedtest_result.configure(
                    text=result_text, 
                    text_color="#2ecc71"  # Зелёный цвет
                ))
                self.after(0, lambda: self.log(f"✅ Скорость: {speed_mbps:.1f} Мбит/с"))
                
            except Exception as e:
                error_msg = f"❌ Ошибка: {str(e)[:30]}"
                self.after(0, lambda: self.lbl_speedtest_result.configure(
                    text=error_msg,
                    text_color="#e74c3c"  # Красный цвет
                ))
                self.after(0, lambda: self.log(f"❌ Ошибка теста скорости: {e}"))
            finally:
                self.after(0, lambda: self.btn_speedtest.configure(
                    state="normal", 
                    text="⚡ Быстрый тест скорости"
                ))
        
        threading.Thread(target=_test, daemon=True).start()

    def start_test_thread(self):
        self.btn_run.configure(state="disabled", fg_color="gray50", text="⏳ Тестирую...")
        self.log("=" * 50)
        self.log("🚀 Запуск полного тестирования...")
        
        thread = threading.Thread(target=self.run_tests_logic)
        thread.start()

    def run_tests_logic(self):
        try:
            selected = self.category_builder.get_selected_services()
            
            if not selected:
                self.log("⚠️ Ничего не выбрано! Отметьте сервисы.")
                self.after(0, self.reset_button)
                return

            monitor = ServiceMonitor(timeout=self.var_timeout.get())
            repeats = self.var_repeats.get()
            
            for name in selected:
                if name in SERVICE_MAP:
                    target = SERVICE_MAP[name]
                    self.log(f"\n🔍 Тестируем: {name} ({target['host']})")
                    
                    result = monitor.test_service(
                        name=name,
                        host=target['host'],
                        path=target['path'],
                        repeats=repeats
                    )
                    
                if result['success']:
                    self.log(f"  ✅ Среднее: {result['avg']:.1f} мс | "
                            f"Min: {result['min']:.1f} | Max: {result['max']:.1f}")
                else:
                    error_msg = result.get('error', 'Неизвестная ошибка')
                    self.log(f"  ❌ Не удалось получить данные")
                    self.log(f"     🔍 Ошибка: {error_msg[:100]}")
            
            monitor.close()
            self.log("\n" + "=" * 50)
            self.log("✅ Все тесты завершены!")
            
        finally:
            self.after(0, self.reset_button)

    def reset_button(self):
        self.btn_run.configure(state="normal", fg_color="#2ecc71", text="▶ Запустить тест")


if __name__ == "__main__":
    app = MonitorUI()
    app.mainloop()