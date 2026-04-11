import os
import ctypes
import sys
import subprocess
import re
import time
import requests
import platform
import threading
import importlib.util  # NOVO: Necessário para rodar scripts internos
import customtkinter as ctk
from dotenv import load_dotenv

# --- FUNÇÃO DE CAMINHO PARA RECURSOS ---
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

load_dotenv(resource_path('.env'))

# --- LÓGICA DE SISTEMA ---
def get_sys_info():
    info = {}
    try:
        info['win_version'] = f"{platform.system()} {platform.release()} (Build {platform.version()})"
        info['cpu'] = platform.processor()
        ram_cmd = subprocess.run(['wmic', 'computersystem', 'get', 'TotalPhysicalMemory'], 
                                 capture_output=True, text=True, shell=True)
        ram_match = re.search(r'\d+', ram_cmd.stdout)
        if ram_match:
            gb = int(ram_match.group()) / (1024**3)
            info['ram'] = f"{round(gb, 2)} GB"
        else:
            info['ram'] = "N/A"
        
        try:
            java_cmd = subprocess.run(['java', '-version'], capture_output=True, text=True, 
                                      stderr=subprocess.STDOUT, shell=True)
            java_ver = re.search(r'\"(.+?)\"', java_cmd.stdout)
            info['java'] = java_ver.group(1) if java_ver else "Não instalado"
        except:
            info['java'] = "Não instalado"
    except:
        pass
    return info

# --- INTERFACE GRÁFICA ---
class AppInstalador(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Instalador Inteligente v2.0")
        self.geometry("1000x600")
        ctk.set_appearance_mode("dark")

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # MENU LATERAL
        self.frame_menu = ctk.CTkFrame(self, width=300, corner_radius=0)
        self.frame_menu.grid(row=0, column=0, sticky="nsew")
        
        self.lbl_titulo = ctk.CTkLabel(self.frame_menu, text="CONFIGURAÇÃO", font=ctk.CTkFont(size=20, weight="bold"))
        self.lbl_titulo.pack(pady=20, padx=20)

        self.cnpj_var = ctk.StringVar()
        self.cnpj_var.trace_add("write", self.limitar_cnpj)
        self.entry_cnpj = ctk.CTkEntry(self.frame_menu, placeholder_text="00.000.000/0001-00", width=250, textvariable=self.cnpj_var)
        self.entry_cnpj.pack(pady=10, padx=20)

        self.lbl_scripts = ctk.CTkLabel(self.frame_menu, text="Scripts Disponíveis:", font=ctk.CTkFont(size=14))
        self.lbl_scripts.pack(pady=(20, 5))

        self.scroll_scripts = ctk.CTkScrollableFrame(self.frame_menu, width=250, label_text="Arquivos .md")
        self.scroll_scripts.pack(pady=10, padx=20, fill="both", expand=True)

        # CONSOLE
        self.frame_console = ctk.CTkFrame(self, fg_color="black")
        self.frame_console.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        
        self.txt_console = ctk.CTkTextbox(self.frame_console, fg_color="black", text_color="#00FF00", 
                                         font=("Consolas", 12), corner_radius=5)
        self.txt_console.pack(fill="both", expand=True, padx=5, pady=5)

        self.listar_arquivos()

    def limitar_cnpj(self, *args):
        texto = self.cnpj_var.get()
        if len(texto) > 18: self.cnpj_var.set(texto[:18])

    def listar_arquivos(self):
        diretorio = resource_path('MD')
        if not os.path.exists(diretorio):
            self.escrever_log(f"⚠️ Pasta MD não encontrada")
            return
        
        arquivos = [f for f in os.listdir(diretorio) if f.endswith('.md')]
        for nome_arq in arquivos:
            btn = ctk.CTkButton(self.scroll_scripts, text=nome_arq.upper(), 
                                command=lambda a=nome_arq: self.iniciar_thread_instalacao(a))
            btn.pack(pady=5, fill="x")

    def escrever_log(self, texto):
        # Garante que o texto seja string e adiciona quebra de linha
        self.txt_console.insert("end", f"{str(texto)}\n")
        self.txt_console.see("end")

    def iniciar_thread_instalacao(self, arquivo):
        cnpj = self.entry_cnpj.get().strip()
        if not cnpj:
            self.escrever_log("❌ ERRO: Digite o CNPJ antes de iniciar.")
            return
        self.txt_console.delete("1.0", "end")
        t = threading.Thread(target=self.executar_script, args=(arquivo, cnpj))
        t.start()

    # --- NOVO MÉTODO: EXECUTA SCRIPT PYTHON INTERNO ---
    def rodar_python_interno(self, caminho_relativo):
        """Executa scripts da pasta tools sem abrir novo terminal, enviando prints para o console"""
        try:
            caminho_abs = resource_path(caminho_relativo)
            if not os.path.exists(caminho_abs):
                self.escrever_log(f"❌ Script não encontrado: {caminho_relativo}")
                return False

            spec = importlib.util.spec_from_file_location("ferramenta_interna", caminho_abs)
            modulo = importlib.util.module_from_spec(spec)
            
            # Redireciona o print do script secundário para o console da nossa App
            import builtins
            original_print = builtins.print
            builtins.print = self.escrever_log 

            spec.loader.exec_module(modulo)
            
            if hasattr(modulo, "main"):
                modulo.main()
            
            # Restaura o print original
            builtins.print = original_print
            return True
        except Exception as e:
            self.escrever_log(f"❌ Erro na ferramenta interna: {e}")
            return False

    def executar_script(self, arquivo, cnpj):
        sucesso_geral = True
        logs_erro = []
        caminho_md = resource_path(os.path.join('MD', arquivo))

        try:
            with open(caminho_md, 'r', encoding='utf-8') as f:
                content = f.read()

            # REGEX ATUALIZADO: Suporta execute_python
            blocks = re.findall(r"```(powershell|cmd|execute_python)\s+(.*?)```", content, re.DOTALL)
            CREATE_NO_WINDOW = 0x08000000

            for shell_type, block_content in blocks:
                if shell_type == "execute_python":
                    # Chama o executor interno de Python
                    res = self.rodar_python_interno(block_content.strip())
                    if not res: 
                        sucesso_geral = False
                        break
                else:
                    # Lógica padrão para CMD e PowerShell
                    lines = block_content.strip().split('\n')
                    for line in lines:
                        if not line.strip(): continue
                        self.escrever_log(f" > Executando: {line[:60]}...")
                        
                        cmd = ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", line] if shell_type == "powershell" else line
                        
                        result = subprocess.run(cmd, capture_output=True, text=True, shell=True, creationflags=CREATE_NO_WINDOW)

                        if result.returncode != 0:
                            sucesso_geral = False
                            erro = result.stderr if result.stderr else result.stdout
                            self.escrever_log(f"    ❌ ERRO: {erro.strip()}")
                            logs_erro.append(f"LINHA: {line} | ERRO: {erro}")
                            break
                    if not sucesso_geral: break

            status = "success" if sucesso_geral else "error"
            self.escrever_log(f"\n{'✅ SUCESSO' if sucesso_geral else '⚠️ ERRO'} NA INSTALAÇÃO.")
            self.enviar_post(cnpj, status, arquivo, "\n".join(logs_erro))

        except Exception as e:
            self.escrever_log(f"❌ FALHA CRÍTICA: {e}")

    def enviar_post(self, cnpj, status, arquivo, erro):
        webhook = os.getenv("WEBHOOKPAINEL")
        if not webhook: return
        payload = {
            "cnpjCliente": cnpj, "status": status, "software": arquivo.upper(),
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"), "log_erro": erro, **get_sys_info()
        }
        try: requests.post(webhook, json=payload, timeout=10)
        except: pass

def is_admin():
    try: return ctypes.windll.shell32.IsUserAnAdmin()
    except: return False

if __name__ == "__main__":
    if not is_admin():
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
    else:
        app = AppInstalador()
        app.mainloop()