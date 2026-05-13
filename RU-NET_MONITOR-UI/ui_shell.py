# ui_shell.py — Главный файл приложения (v2.0 compact)
import customtkinter as ctk, threading, tkinter.messagebox as messagebox
from src.ui_components import CategoryBuilder, SERVICE_MAP
from src.network_monitor import ServiceMonitor

class MonitorUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("RU-Net-Monitor v2.0"); self.geometry("900x800"); self.minsize(650, 600)
        self.last_test_results = []; ctk.set_appearance_mode("Dark"); ctk.set_default_color_theme("blue")
        self.grid_columnconfigure(1, weight=2); self.grid_columnconfigure(0, weight=1); self.grid_rowconfigure(1, weight=1)
        self.lbl_title = ctk.CTkLabel(self, text="🚀 RU-Net-Monitor v2.0", font=ctk.CTkFont(size=24, weight="bold"))
        self.lbl_title.grid(row=0, column=0, columnspan=2, padx=20, pady=(15, 10), sticky="w")
        self.frame_left = ctk.CTkFrame(self, corner_radius=10, fg_color="gray15")
        self.frame_left.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        self.scroll_categories = ctk.CTkScrollableFrame(self.frame_left, width=280, label_text="Сервисы")
        self.scroll_categories.pack(fill="both", expand=True, padx=10, pady=(10, 5))
        self.category_builder = CategoryBuilder(self.scroll_categories, on_checkbox_change=self.update_counter)
        self.category_builder.build_all()
        self.frame_info = ctk.CTkFrame(self.frame_left, fg_color="#2c3e50", corner_radius=8)
        self.frame_info.pack(fill="x", padx=10, pady=10)
        self.lbl_counter = ctk.CTkLabel(self.frame_info, text="Выбрано: 0", font=ctk.CTkFont(size=14, weight="bold"), text_color="#2ecc71")
        self.lbl_counter.pack(pady=(5, 0))
        self.lbl_isp = ctk.CTkLabel(self.frame_info, text="📡 Провайдер: определение...", font=ctk.CTkFont(size=12), text_color="#3498db", wraplength=260)
        self.lbl_isp.pack(pady=5); self.after(100, self.detect_isp)
        self.btn_speedtest = ctk.CTkButton(self.frame_info, text="⚡ Быстрый тест скорости", command=self.run_simple_speedtest, fg_color="#3498db", hover_color="#2980b9", height=35)
        self.btn_speedtest.pack(fill="x", padx=5, pady=5)
        self.lbl_speedtest_result = ctk.CTkLabel(self.frame_info, text="", font=ctk.CTkFont(size=11), text_color="#f39c12")
        self.lbl_speedtest_result.pack(pady=(0, 5))
        self.frame_right = ctk.CTkFrame(self, corner_radius=10); self.frame_right.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")
        self.frame_right.grid_rowconfigure(0, weight=1); self.frame_right.grid_columnconfigure(0, weight=1)
        self.text_log = ctk.CTkTextbox(self.frame_right, corner_radius=10, state="disabled", font=ctk.CTkFont(size=12))
        self.text_log.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.frame_controls = ctk.CTkFrame(self.frame_right, height=80, fg_color="transparent")
        self.frame_controls.grid(row=1, column=0, padx=10, pady=10, sticky="ew")
        self.frame_controls.grid_columnconfigure(0, weight=1); self.frame_controls.grid_columnconfigure(1, weight=1); self.frame_controls.grid_columnconfigure(2, weight=1)
        frm_set = ctk.CTkFrame(self.frame_controls, fg_color="gray20", corner_radius=10); frm_set.grid(row=0, column=0, sticky="nsew", padx=5)
        ctk.CTkLabel(frm_set, text="Повторов:", font=ctk.CTkFont(size=13)).grid(row=0, column=0, padx=5, pady=5)
        self.var_repeats = ctk.IntVar(value=3); ctk.CTkEntry(frm_set, textvariable=self.var_repeats, width=50).grid(row=0, column=1, padx=5, pady=5)
        ctk.CTkLabel(frm_set, text="Таймаут (сек):", font=ctk.CTkFont(size=13)).grid(row=1, column=0, padx=5, pady=5)
        self.var_timeout = ctk.IntVar(value=3); ctk.CTkEntry(frm_set, textvariable=self.var_timeout, width=50).grid(row=1, column=1, padx=5, pady=5)
        self.btn_run = ctk.CTkButton(self.frame_controls, text="▶ Запустить тест", fg_color="#2ecc71", hover_color="#27ae60", height=50, font=ctk.CTkFont(size=16, weight="bold"), command=self.start_test_thread)
        self.btn_run.grid(row=0, column=1, sticky="nsew", padx=5)
        self.btn_save = ctk.CTkButton(self.frame_controls, text="💾 Сохранить CSV", command=self.save_results, fg_color="#3498db", hover_color="#2980b9", height=50, font=ctk.CTkFont(size=16), state="disabled")
        self.btn_save.grid(row=0, column=2, sticky="nsew", padx=5)

    def log(self, msg): self.text_log.configure(state="normal"); self.text_log.insert("end", msg + "\n"); self.text_log.see("end"); self.text_log.configure(state="disabled")
    def update_counter(self): self.lbl_counter.configure(text=f"Выбрано: {self.category_builder.count_selected()} сервисов")
    
    def detect_isp(self):
        def _detect():
            try:
                import httpx
                # Пробуем 3 разных источника
                for api in ["https://api.ipify.org?format=json", "http://ip-api.com/json/", "https://ifconfig.me/ip"]:
                    try:
                        r = httpx.get(api, timeout=5.0)
                        if r.status_code == 200:
                            d = r.json() if "json" in api else {"ip": r.text.strip(), "isp": "Detected"}
                            # ✅ Универсальное получение IP (query, ip, или текст)
                            ip = d.get("query") or d.get("ip") or "Не определён"
                            isp = d.get("isp") or d.get("org") or "Определено"
                            self.after(0, lambda i=isp, p=ip: self.lbl_isp.configure(text=f"📡 {i}\n🌐 IP: {p}"))
                            return
                    except: continue
                self.after(0, lambda: self.lbl_isp.configure(text="📡 Не определено\n🌐 IP: -"))
            except: self.after(0, lambda: self.lbl_isp.configure(text="📡 Ошибка\n🌐 IP: -"))
        threading.Thread(target=_detect, daemon=True).start()
    def run_simple_speedtest(self):
        self.btn_speedtest.configure(state="disabled", text="⏳ Тестирование..."); self.lbl_speedtest_result.configure(text="")
        def _test():
            try:
                import httpx, time; self.after(0, lambda: self.log("📊 Запуск быстрого теста скорости..."))
                start = time.time(); response = httpx.get("https://speed.cloudflare.com/__down?bytes=25000000", timeout=30, follow_redirects=True); elapsed = time.time() - start
                size_kb = len(response.content) / 1024; speed_mbps = (size_kb * 8) / (elapsed * 1000)
                self.after(0, lambda: self.lbl_speedtest_result.configure(text=f"⚡ {speed_mbps:.1f} Мбит/с | {elapsed*1000:.0f} мс", text_color="#2ecc71"))
                self.after(0, lambda: self.log(f"✅ Скорость: {speed_mbps:.1f} Мбит/с"))
            except Exception as e:
                self.after(0, lambda: self.lbl_speedtest_result.configure(text=f"❌ Ошибка: {str(e)[:30]}", text_color="#e74c3c"))
                self.after(0, lambda: self.log(f"❌ Ошибка теста скорости: {e}"))
            finally: self.after(0, lambda: self.btn_speedtest.configure(state="normal", text="⚡ Быстрый тест скорости"))
        threading.Thread(target=_test, daemon=True).start()

    def start_test_thread(self):
        self.btn_run.configure(state="disabled", fg_color="gray50", text="⏳ Тестирую..."); self.log("=" * 50); self.log("🚀 Запуск полного тестирования...")
        threading.Thread(target=self.run_tests_logic).start()

    def run_tests_logic(self):
        try:
            selected = self.category_builder.get_selected_services()
            if not selected: self.log("⚠️ Ничего не выбрано!"); self.after(0, self.reset_button); return
            monitor, repeats = ServiceMonitor(timeout=self.var_timeout.get()), self.var_repeats.get(); all_results = []
            for name in selected:
                if name in SERVICE_MAP:
                    target = SERVICE_MAP[name]; self.log(f"\n🔍 Тестируем: {name} ({target['host']})")
                    result = monitor.test_service(name=name, host=target['host'], path=target['path'], repeats=repeats); all_results.append(result)
                    if result['success']: self.log(f"  ✅ Среднее: {result['avg']:.1f} мс | Min: {result['min']:.1f} | Max: {result['max']:.1f}")
                    else: self.log(f"  ❌ Не удалось получить данные"); self.log(f"     🔍 Ошибка: {result.get('error', '')[:100]}")
            self.last_test_results = all_results; monitor.close(); self.log("\n" + "=" * 50); self.log("✅ Все тесты завершены!")
        finally: self.after(0, self.reset_button); self.after(0, lambda: self.btn_save.configure(state="normal"))

    def save_results(self):
        try:
            from src.reporters import save_results_to_csv
            if self.last_test_results:
                filepath = save_results_to_csv(self.last_test_results); self.log(f"💾 Результаты сохранены: {filepath}")
                messagebox.showinfo("Экспорт", f"Результаты сохранены в:\n{filepath}")
            else: messagebox.showwarning("Нет данных", "Сначала запустите тестирование")
        except Exception as e: self.log(f"❌ Ошибка сохранения: {e}")

    def reset_button(self): self.btn_run.configure(state="normal", fg_color="#2ecc71", text="▶ Запустить тест")

if __name__ == "__main__": app = MonitorUI(); app.mainloop()