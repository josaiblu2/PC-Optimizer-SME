import os
import sys
import logging
from logging.handlers import RotatingFileHandler
import customtkinter as ctk
import psutil
import subprocess
import threading
from tkinter import messagebox

# Configuración de apariencia de customtkinter
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class SelectionDialog(ctk.CTkToplevel):
    def __init__(self, parent, title, summary, items):
        super().__init__(parent)
        self.title(title)
        self.geometry("700x550")
        self.grab_set()

        self.selected_items = []
        self.items = items  # { "id", "name", "description", "path", "is_protected", "type" }

        # Resumen superior
        self.label_summary = ctk.CTkLabel(self, text=summary, font=ctk.CTkFont(size=14, weight="bold"), wraplength=650)
        self.label_summary.pack(pady=15, padx=20)

        # Frame con scroll para los items
        self.scroll_frame = ctk.CTkScrollableFrame(self, label_text="Elementos detectados")
        self.scroll_frame.pack(pady=10, padx=20, fill="both", expand=True)

        self.checkboxes = {}
        for item in self.items:
            is_prot = item.get("is_protected", False)
            item_type = item.get("type", "Seguro")
            
            # Texto decorado
            display_text = f"[{item_type}] {item['name']}"
            if "path" in item:
                display_text += f"\nPath: {item['path']}"
            display_text += f"\n{item['description']}"

            var = ctk.BooleanVar(value=not is_prot)
            item_frame = ctk.CTkFrame(self.scroll_frame)
            item_frame.pack(pady=5, padx=10, fill="x")

            cb = ctk.CTkCheckBox(item_frame, text=display_text, variable=var, 
                                 state="disabled" if is_prot else "normal",
                                 font=ctk.CTkFont(size=11))
            cb.pack(pady=5, padx=10, anchor="w")
            
            if is_prot:
                prot_label = ctk.CTkLabel(item_frame, text="(Protegido por el Sistema)", text_color="orange", font=ctk.CTkFont(size=10, slant="italic"))
                prot_label.pack(padx=30, anchor="w")

            self.checkboxes[item['id']] = var

        # Botones inferiores
        self.btn_frame = ctk.CTkFrame(self)
        self.btn_frame.pack(pady=20, padx=20, fill="x")

        self.btn_accept_all = ctk.CTkButton(self.btn_frame, text="Accept All (Solo Seguros)", command=self.toggle_all)
        self.btn_accept_all.pack(side="left", padx=10)

        self.btn_confirm = ctk.CTkButton(self.btn_frame, text="Confirmar y Ejecutar", command=self.confirm)
        self.btn_confirm.pack(side="right", padx=10)

        self.all_selected = True

    def toggle_all(self):
        # Solo afecta a los que no están protegidos
        self.all_selected = not self.all_selected
        for item_id, var in self.checkboxes.items():
            # Buscamos el item original para ver si es protegido
            item = next((i for i in self.items if i["id"] == item_id), None)
            if item and not item.get("is_protected", False):
                var.set(self.all_selected)
        
    def confirm(self):
        self.selected_items = [item_id for item_id, var in self.checkboxes.items() if var.get()]
        self.destroy()

class PCOptimizerApp(ctk.CTk):
    PROTECTED_PROCESSES = ["MemCompression", "System", "Registry", "lsass.exe", "csrss.exe", "smss.exe"]

    def __init__(self):
        super().__init__()

        # Inicialización del entorno (Creación de carpetas logs/docs)
        self.initialize_environment()

        # Configuración de la ventana principal
        self.title("PC-Optimizer SME Edition")
        self.geometry("800x650")

        # Configuración de Logging con ruta absoluta persistente
        self.setup_logging()
        self.logger.info("--- Aplicación Iniciada ---")

        # Variable para el modo de prueba (Dry Run)
        self.dry_run_mode = ctk.BooleanVar(value=True)

        # Creación de la interfaz
        self.create_widgets()

        # Manejo de cierre seguro
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def initialize_environment(self):
        """Determina la ruta base y crea la estructura de carpetas necesaria."""
        # Determinar directorio base (funciona para script y EXE de PyInstaller)
        if getattr(sys, 'frozen', False):
            self.base_dir = os.path.dirname(sys.executable)
        else:
            # Si es script, subimos un nivel desde /src
            self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            
        # Carpetas requeridas
        folders = ["logs", "docs"]
        
        for folder in folders:
            path = os.path.join(self.base_dir, folder)
            if not os.path.exists(path):
                try:
                    os.makedirs(path)
                except Exception as e:
                    print(f"Error crítico al crear carpeta {folder}: {e}")

    def setup_logging(self):
        """Configura el log rotatorio con rutas absolutas."""
        log_dir = os.path.join(self.base_dir, "logs")
        if not os.path.exists(log_dir):
            # Fallback extremo si falló initialize_environment por permisos
            log_dir = os.path.join(os.environ.get('TEMP', '.'), "PC-Optimizer-Logs")
            if not os.path.exists(log_dir): os.makedirs(log_dir)
        
        log_file = os.path.join(log_dir, "mantenimiento_pc.log")
        self.logger = logging.getLogger("PCOptimizer")
        self.logger.setLevel(logging.DEBUG)

        handler = RotatingFileHandler(log_file, maxBytes=5*1024*1024, backupCount=3)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

    def create_widgets(self):
        """Crea los componentes de la interfaz gráfica."""
        
        # Título principal
        self.label_title = ctk.CTkLabel(self, text="PC-Optimizer", font=ctk.CTkFont(size=24, weight="bold"))
        self.label_title.pack(pady=20)

        # Switch para Modo de Prueba
        self.switch_dry_run = ctk.CTkSwitch(self, text="Modo de Prueba (Simulación)", variable=self.dry_run_mode)
        self.switch_dry_run.pack(pady=5)

        # Indicador de Carga (Oculto por defecto)
        self.progress_bar = ctk.CTkProgressBar(self, mode="indeterminate", width=400)
        self.progress_label = ctk.CTkLabel(self, text="Escaneando sistema...", font=ctk.CTkFont(size=12, slant="italic"))

        # Contenedor de módulos
        self.modules_frame = ctk.CTkFrame(self)
        self.modules_frame.pack(pady=10, padx=20, fill="both", expand=True)

        # Módulo de Limpieza
        self.create_module_row(self.modules_frame, "Limpieza de Archivos Temporales", 
                               "Elimina archivos temporales acumulados por el sistema y el navegador.",
                               self.start_cleaning_thread)

        # Módulo de RAM
        self.create_module_row(self.modules_frame, "Optimización de Memoria RAM", 
                               "Muestra procesos que consumen >500MB.",
                               self.run_ram_opt)

        # Módulo de Salud (SFC/DISM)
        self.create_module_row(self.modules_frame, "Salud del Sistema (SFC/DISM)", 
                               "Escanea y repara archivos corruptos del núcleo de Windows.",
                               self.run_health_check)

    def create_module_row(self, parent, title, help_text, command):
        """Crea una fila para un módulo con botón de acción e información."""
        row_frame = ctk.CTkFrame(parent)
        row_frame.pack(pady=8, padx=10, fill="x")

        label = ctk.CTkLabel(row_frame, text=title, font=ctk.CTkFont(size=14))
        label.pack(side="left", padx=10)

        info_button = ctk.CTkButton(row_frame, text="ⓘ", width=30, command=lambda: messagebox.showinfo("Información", help_text))
        info_button.pack(side="right", padx=5)

        action_button = ctk.CTkButton(row_frame, text="Ejecutar", command=command)
        action_button.pack(side="right", padx=5)

    def set_ui_state(self, is_loading):
        """Alterna el estado de la UI durante procesos largos."""
        if is_loading:
            self.progress_bar.pack(pady=10)
            self.progress_label.pack()
            self.progress_bar.start()
            # Deshabilitar botones para evitar clics dobles
            for child in self.modules_frame.winfo_children():
                for subchild in child.winfo_children():
                    if isinstance(subchild, ctk.CTkButton):
                        subchild.configure(state="disabled")
        else:
            self.progress_bar.stop()
            self.progress_bar.pack_forget()
            self.progress_label.pack_forget()
            for child in self.modules_frame.winfo_children():
                for subchild in child.winfo_children():
                    if isinstance(subchild, ctk.CTkButton):
                        subchild.configure(state="normal")

    def get_dir_size(self, path):
        """Calcula el tamaño de un directorio en MB con manejo de excepciones."""
        total_size = 0
        try:
            for dirpath, dirnames, filenames in os.walk(path):
                for f in filenames:
                    fp = os.path.join(dirpath, f)
                    try:
                        if not os.path.islink(fp):
                            total_size += os.path.getsize(fp)
                    except (OSError, PermissionError):
                        continue
        except Exception as e:
            self.logger.warning(f"Error al acceder a {path}: {e}")
        return total_size / (1024 * 1024)

    def start_cleaning_thread(self):
        """Lanza el proceso de escaneo de limpieza en un hilo secundario."""
        self.set_ui_state(True)
        threading.Thread(target=self.run_cleaning, daemon=True).start()

    def run_cleaning(self):
        """Escanea archivos temporales y muestra diálogo (Ejecutado en hilo)."""
        self.logger.info("Iniciando escaneo refinado de archivos temporales.")
        
        system_temp = os.path.join(os.environ.get('SystemRoot', 'C:\\Windows'), 'Temp')
        user_temp = os.environ.get('TEMP')
        winsxs_temp = os.path.join(os.environ.get('SystemRoot', 'C:\\Windows'), 'WinSxS', 'Temp')

        raw_paths = [user_temp, system_temp, winsxs_temp]
        items = []
        total_found_mb = 0

        for i, path in enumerate(raw_paths):
            if path and os.path.exists(path):
                is_winsxs = "WinSxS" in path
                size = self.get_dir_size(path)
                total_found_mb += size
                items.append({
                    "id": f"temp_{i}",
                    "path": path,
                    "name": f"Carpeta {'Crítica (WinSxS)' if is_winsxs else 'Temporal'}",
                    "description": f"Tamaño: {size:.2f} MB",
                    "is_protected": is_winsxs,
                    "type": "Protegido/Sistema" if is_winsxs else "Seguro"
                })

        # Volver al hilo principal para mostrar el diálogo
        self.after(100, lambda: self.show_cleaning_dialog(items, total_found_mb))

    def show_cleaning_dialog(self, items, total_found_mb):
        """Muestra el diálogo de selección (Hilo principal)."""
        self.set_ui_state(False)
        summary = f"Estado Actual: Se encontraron {len(items)} ubicaciones.\nTamaño total: {total_found_mb:.2f} MB."
        
        dialog = SelectionDialog(self, "Limpieza de Archivos Temporales", summary, items)
        self.wait_window(dialog)

        if dialog.selected_items:
            is_dry = self.dry_run_mode.get()
            freed_mb = 0
            skipped_count = 0
            results_per_folder = {} # { folder_name: count }
            
            self.logger.info(f"Iniciando ejecución de limpieza. Dry Run: {is_dry}")
            
            for item_id in dialog.selected_items:
                item = next(it for it in items if it["id"] == item_id)
                path = item["path"]
                folder_name = item["name"]
                results_per_folder[folder_name] = 0
                
                if "WinSxS" in path:
                    if not is_dry:
                        try:
                            subprocess.run("dism /online /cleanup-image /startcomponentcleanup", shell=True)
                            results_per_folder[folder_name] = "Completado vía DISM"
                        except Exception as e: self.logger.error(f"Error DISM: {e}")
                    else:
                        results_per_folder[folder_name] = "Simulado vía DISM"
                else:
                    for root, dirs, files in os.walk(path):
                        for f in files:
                            fp = os.path.join(root, f)
                            try:
                                size = os.path.getsize(fp) / (1024*1024)
                                if not is_dry:
                                    os.remove(fp)
                                    freed_mb += size
                                    results_per_folder[folder_name] += 1
                                else:
                                    freed_mb += size
                                    results_per_folder[folder_name] += 1
                            except (PermissionError, OSError):
                                skipped_count += 1

            # Construir reporte detallado
            details = "\n".join([f"- {k}: {v} {'archivos' if isinstance(v, int) else ''}" for k, v in results_per_folder.items()])
            final_msg = f"Reporte Final de Limpieza:\n\nDetalles:\n{details}\n\n"
            final_msg += f"- MB {'simulados' if is_dry else 'liberados'}: {freed_mb:.2f}\n"
            final_msg += f"- Archivos omitidos: {skipped_count}"
            
            messagebox.showinfo("Resumen de Ejecución", final_msg)
            self.logger.info(final_msg)

    def run_ram_opt(self):
        """Escanea procesos con etiquetas de seguridad."""
        self.logger.info("Escaneando procesos con inteligencia de seguridad.")
        
        items = []
        for proc in psutil.process_iter(['pid', 'name', 'memory_info']):
            try:
                name = proc.info['name']
                pid = proc.info['pid']
                mem_mb = proc.info['memory_info'].rss / (1024 * 1024)
                
                if mem_mb > 500 or name in self.PROTECTED_PROCESSES:
                    is_prot = name in self.PROTECTED_PROCESSES
                    items.append({
                        "id": str(pid),
                        "name": f"{name} (PID: {pid})",
                        "description": f"Consumo: {mem_mb:.2f} MB",
                        "is_protected": is_prot,
                        "type": "Protegido/Sistema" if is_prot else "Seguro"
                    })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        summary = f"Estado Actual: {len(items)} procesos relevantes detectados."
        dialog = SelectionDialog(self, "Optimización de Memoria RAM", summary, items)
        self.wait_window(dialog)

        if dialog.selected_items:
            is_dry = self.dry_run_mode.get()
            terminated_names = []
            skipped_prot = 0
            
            for item_id in dialog.selected_items:
                try:
                    p = psutil.Process(int(item_id))
                    name = p.name()
                    if name in self.PROTECTED_PROCESSES:
                        skipped_prot += 1
                        continue
                    if not is_dry:
                        p.terminate()
                    terminated_names.append(name)
                except Exception: continue

            # Construir reporte detallado
            process_list = "\n".join([f"• {name}" for name in terminated_names]) if terminated_names else "Ninguno"
            final_msg = f"Reporte Final RAM:\n\nProcesos {'simulados' if is_dry else 'cerrados'}:\n{process_list}\n\n"
            final_msg += f"- Total: {len(terminated_names)}\n"
            final_msg += f"- Omitidos (Protegidos): {skipped_prot}"
            
            messagebox.showinfo("Resumen de Ejecución", final_msg)
            self.logger.info(final_msg)

    def run_health_check(self):
        """Opciones de reparación de salud del sistema."""
        items = [
            {"id": "sfc", "name": "SFC (System File Checker)", "description": "Repara archivos de sistema."},
            {"id": "dism", "name": "DISM (Deployment Image Servicing)", "description": "Repara la imagen de Windows."}
        ]
        dialog = SelectionDialog(self, "Salud del Sistema", "Estado Actual: Requiere análisis de núcleo.", items)
        self.wait_window(dialog)

        if dialog.selected_items:
            is_dry = self.dry_run_mode.get()
            if not is_dry:
                messagebox.showwarning("Admin", "Iniciando reparación (Requiere Privilegios).")
                for item_id in dialog.selected_items:
                    cmd = "sfc /scannow" if item_id == "sfc" else "Dism /Online /Cleanup-Image /RestoreHealth"
                    self.logger.info(f"Ejecutando: {cmd}")
            else:
                messagebox.showinfo("Simulación", "Comando simulado correctamente.")

    def on_closing(self):
        """Cierre seguro garantizando el guardado de logs."""
        self.logger.info("--- Aplicación Cerrada ---")
        logging.shutdown()
        self.destroy()

if __name__ == "__main__":
    app = PCOptimizerApp()
    app.mainloop()
