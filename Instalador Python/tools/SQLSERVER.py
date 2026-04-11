import subprocess
import os
import sys
import time
import ctypes
import requests
import zipfile  # NOVO: Para manipular arquivos comprimidos
from dotenv import load_dotenv

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

load_dotenv(resource_path('.env'))

# Configurações
INSTANCE_NAME = os.getenv("INSTANCE_NAME", "SQLEXPRESS")
SA_PASSWORD   = os.getenv("SA_PASSWORD", "Senha@123")
SQL_URL       = os.getenv("SQL_URL", "http://localhost:3232/download/SQLEXPR_x64_PTB.zip")

TEMP_DIR      = r"C:\temp"
ZIP_DESTINO   = os.path.join(TEMP_DIR, "SQL_SERVER.zip")
# O instalador .exe que resultará da extração
SQL_INSTALLER_PATH = os.path.join(TEMP_DIR, "SQLEXPR_x64_PTB.exe")

HIDDEN_CONSOLE = 0x08000000

def download_arquivo(url, destino):
    if not os.path.exists(TEMP_DIR):
        os.makedirs(TEMP_DIR)
        
    print(f"--- Iniciando Download do SQL Server (.zip) ---")
    try:
        response = requests.get(url, stream=True, timeout=30)
        total_size = int(response.headers.get('content-length', 0))
        
        if response.status_code != 200:
            print(f"❌ Erro no Servidor: Status {response.status_code}")
            return False

        downloaded = 0
        with open(destino, "wb") as file:
            for data in response.iter_content(chunk_size=1024*1024):
                file.write(data)
                downloaded += len(data)
                if total_size > 0:
                    percent = int((downloaded / total_size) * 100)
                    if percent % 10 == 0:
                        print(f"📥 Baixando ZIP: {percent}% ({downloaded // (1024*1024)}MB / {total_size // (1024*1024)}MB)")
        
        print("✅ Download do ZIP concluído!")
        return True
    except Exception as e:
        print(f"❌ Erro no download: {e}")
        return False

def extrair_zip(caminho_zip, destino_pasta):
    print(f"--- Extraindo instalador... ---")
    try:
        with zipfile.ZipFile(caminho_zip, 'r') as zip_ref:
            zip_ref.extractall(destino_pasta)
        print("✅ Extração concluída!")
        return True
    except Exception as e:
        print(f"❌ Erro ao extrair ZIP: {e}")
        return False

def instalar_sql():
    print(f"--- Iniciando Instalação do SQL Server ({INSTANCE_NAME}) ---")
    if not os.path.exists(SQL_INSTALLER_PATH):
        print(f"❌ Erro: Instalador {SQL_INSTALLER_PATH} não encontrado após extração!")
        return False

    comando = [
        SQL_INSTALLER_PATH, "/Q", "/ACTION=Install", "/FEATURES=SQLEngine",
        f"/INSTANCENAME={INSTANCE_NAME}", "/SECURITYMODE=SQL", f"/SAPWD={SA_PASSWORD}",
        "/SQLSVCACCOUNT=NT AUTHORITY\\SYSTEM", "/SQLSYSADMINACCOUNTS=Administrators",
        "/TCPENABLED=1", "/NPENABLED=1", "/IACCEPTSQLSERVERLICENSETERMS"
    ]
    try:
        subprocess.run(comando, check=True, creationflags=HIDDEN_CONSOLE)
        print("✅ Instalação do motor concluída.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Falha na instalação: {e}")
        return False

def configurar_sa():
    print("--- Ativando usuário 'sa' ---")
    instancia = f".\\{INSTANCE_NAME}"
    comandos_sql = f"ALTER LOGIN sa ENABLE; ALTER LOGIN sa WITH PASSWORD = '{SA_PASSWORD}';"
    comando = ["sqlcmd", "-S", instancia, "-E", "-Q", comandos_sql]
    subprocess.run(comando, shell=True, creationflags=HIDDEN_CONSOLE)

def reiniciar_servico():
    service = f"MSSQL${INSTANCE_NAME}"
    print(f"--- Reiniciando serviço {service} ---")
    subprocess.run(f"net stop {service} /y", shell=True, creationflags=HIDDEN_CONSOLE)
    time.sleep(5)
    subprocess.run(f"net start {service}", shell=True, creationflags=HIDDEN_CONSOLE)

def main():
    if not ctypes.windll.shell32.IsUserAnAdmin():
        print("❌ Execute como administrador!")
        return

    # 1. Download do ZIP
    if download_arquivo(SQL_URL, ZIP_DESTINO):
        
        # 2. Extração do ZIP
        if extrair_zip(ZIP_DESTINO, TEMP_DIR):
            
            # 3. Instalação do .exe extraído
            if instalar_sql():
                print("Aguardando motor subir (20s)...")
                time.sleep(20)
                
                configurar_sa()
                reiniciar_servico()
                
                # Opcional: Limpeza
                try:
                    os.remove(ZIP_DESTINO)
                    # os.remove(SQL_INSTALLER_PATH)
                    print("🧹 Limpeza de arquivos temporários concluída.")
                except: pass
                
                print("🚀 PROCESSO SQL SERVER FINALIZADO!")

if __name__ == "__main__":
    main()