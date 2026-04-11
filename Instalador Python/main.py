import os
import ctypes
import sys
import subprocess
import re
import time
import requests
import platform
import threading
import customtkinter as ctk
from dotenv import load_dotenv

# --- FUNÇÃO DE CAMINHO PARA RECURSOS (ESSENCIAL PARA PYINSTALLER) ---
def resource_path(relative_path):
    """ Retorna o caminho absoluto para o recurso, funcionando no script e no .exe """
    try:
        # O PyInstaller cria uma pasta temporária e armazena o caminho em _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

# Carrega o .env usando o caminho interno do executável
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

        # Configuração de Grid
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- LADO ESQUERDO: MENU ---
        self.frame_menu = ctk.CTkFrame(self, width=300, corner_radius=0)
        self.frame_menu.grid(row=0, column=0, sticky="nsew")
        
        self.lbl_titulo = ctk.CTkLabel(self.frame_menu, text="CONFIGURAÇÃO", font=ctk.CTkFont(size=20, weight="bold"))
        self.lbl_titulo.pack(pady=20, padx=20)

        # Campo CNPJ com Limitação
        self.cnpj_var = ctk.StringVar()
        self.cnpj_var.trace_add("write", self.limitar_cnpj)

        self.entry_cnpj = ctk.CTkEntry(
            self.frame_menu, 
            placeholder_text="00.000.000/0001-00", 
            width=250,
            textvariable=self.cnpj_var
        )
        self.entry_cnpj.pack(pady=10, padx=20)

        self.lbl_scripts = ctk.CTkLabel(self.frame_menu, text="Scripts Disponíveis:", font=ctk.CTkFont(size=14))
        self.lbl_scripts.pack(pady=(20, 5))

        self.scroll_scripts = ctk.CTkScrollableFrame(self.frame_menu, width=250, label_text="Arquivos .md")
        self.scroll_scripts.pack(pady=10, padx=20, fill="both", expand=True)

        # --- LADO DIREITO: CONSOLE ---
        self.frame_console = ctk.CTkFrame(self, fg_color="black")
        self.frame_console.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        
        self.txt_console = ctk.CTkTextbox(self.frame_console, fg_color="black", text_color="#00FF00", 
                                         font=("Consolas", 12), corner_radius=5)
        self.txt_console.pack(fill="both", expand=True, padx=5, pady=5)

        # Carregar arquivos
        self.listar_arquivos()

    def limitar_cnpj(self, *args):
        texto = self.cnpj_var.get()
        if len(texto) > 18:
            self.cnpj_var.set(texto[:18])

    def listar_arquivos(self):
        # USA O CAMINHO INTERNO DO EXECUTÁVEL
        diretorio = resource_path('MD')
        
        if not os.path.exists(diretorio):
            self.escrever_log(f"⚠️ Pasta MD não encontrada em: {diretorio}")
            return
        
        arquivos = [f for f in os.listdir(diretorio) if f.endswith('.md')]
        
        if not arquivos:
            self.escrever_log("ℹ️ Nenhum arquivo .md encontrado na pasta interna.")

        for nome_arq in arquivos:
            btn = ctk.CTkButton(self.scroll_scripts, text=nome_arq.upper(), 
                                command=lambda a=nome_arq: self.iniciar_thread_instalacao(a))
            btn.pack(pady=5, fill="x")

    def escrever_log(self, texto):
        self.txt_console.insert("end", f"{texto}\n")
        self.txt_console.see("end")

    def iniciar_thread_instalacao(self, arquivo):
        cnpj = self.entry_cnpj.get().strip()
        if not cnpj:
            self.escrever_log("❌ ERRO: Digite o CNPJ antes de iniciar.")
            return

        self.txt_console.delete("1.0", "end")
        self.escrever_log(f"🚀 Iniciando processo: {arquivo}")
        
        t = threading.Thread(target=self.executar_script, args=(arquivo, cnpj))
        t.start()

    def executar_script(self, arquivo, cnpj):
        sucesso_geral = True
        logs_erro = []
        
        # USA O CAMINHO INTERNO PARA LER O CONTEÚDO DO MD
        caminho_md = resource_path(os.path.join('MD', arquivo))

        try:
            with open(caminho_md, 'r', encoding='utf-8') as f:
                content = f.read()

            blocks = re.findall(r"```(powershell|cmd)\s+(.*?)```", content, re.DOTALL)

            CREATE_NO_WINDOW = 0x08000000 # Evita que janelas de terminal "pisquem"

            for shell_type, block_content in blocks:
                lines = block_content.strip().split('\n')
                for line in lines:
                    if not line.strip(): continue
                    
                    self.escrever_log(f"  > Executando: {line[:60]}...")
                    
                    if shell_type == "powershell":
                        cmd = ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", line]
                    else:
                        cmd = line

                    result = subprocess.run(cmd, capture_output=True, text=True, 
                                            shell=True, creationflags=CREATE_NO_WINDOW)

                    if result.returncode != 0:
                        sucesso_geral = False
                        erro = result.stderr if result.stderr else result.stdout
                        self.escrever_log(f"    ❌ ERRO: {erro.strip()}")
                        logs_erro.append(f"LINHA: {line} | ERRO: {erro}")
                        break
                if not sucesso_geral: break

            if sucesso_geral:
                self.escrever_log("\n✅ PROCESSO CONCLUÍDO COM SUCESSO!")
                status = "success"
            else:
                self.escrever_log("\n⚠️ PROCESSO FINALIZADO COM ERROS.")
                status = "error"

            self.enviar_post(cnpj, status, arquivo, "\n".join(logs_erro))

        except Exception as e:
            self.escrever_log(f"❌ FALHA CRÍTICA AO LER MD: {e}")

    def enviar_post(self, cnpj, status, arquivo, erro):
        webhook = os.getenv("WEBHOOKPAINEL")
        if not webhook: return
        
        sys_info = get_sys_info()
        payload = {
            "cnpjCliente": cnpj, "status": status, 
            "software": arquivo.upper(), "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "log_erro": erro, **sys_info
        }
        try:
            requests.post(webhook, json=payload, timeout=10)
            self.escrever_log("📡 Dados enviados ao painel de controle.")
        except:
            self.escrever_log("📡 Falha ao comunicar com o Webhook.")

def is_admin():
    try: return ctypes.windll.shell32.IsUserAnAdmin()
    except: return False

if __name__ == "__main__":
    if not is_admin():
        # Relança como administrador
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
    else:
        app = AppInstalador()
        app.mainloop()