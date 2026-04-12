import os
import sys
import winreg
import ctypes
from dotenv import load_dotenv

# --- FUNÇÃO DE CAMINHO PARA RECURSOS ---
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# Carrega o .env localizado na raiz do executável
load_dotenv(resource_path('.env'))

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def criar_odbc(odbc_name, base, usuario_sql, senha_sql, servidor_sql):
    """
    Cria uma fonte de dados ODBC no DSN de usuário (HKEY_CURRENT_USER)
    """
    if not odbc_name or not servidor_sql:
        return False, "❌ Nome do ODBC ou Servidor não configurado no .env"

    try:
        # Chave principal do ODBC no DSN de usuário
        odbc_key_path = f"SOFTWARE\\ODBC\\ODBC.INI\\{odbc_name}"

        # Criar chave principal do ODBC
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, odbc_key_path) as key:
            winreg.SetValueEx(key, "Server", 0, winreg.REG_SZ, servidor_sql)
            winreg.SetValueEx(key, "LastUser", 0, winreg.REG_SZ, usuario_sql)
            winreg.SetValueEx(key, "PWD", 0, winreg.REG_SZ, senha_sql)
            winreg.SetValueEx(key, "Database", 0, winreg.REG_SZ, base)
            winreg.SetValueEx(key, "Description", 0, winreg.REG_SZ, f"Conexão {odbc_name}")
            winreg.SetValueEx(key, "Driver", 0, winreg.REG_SZ, "C:\\Windows\\System32\\sqlsrv32.dll")
            winreg.SetValueEx(key, "Trusted_Connection", 0, winreg.REG_SZ, "No") # Força uso de usuário/senha do SQL

        # Registrar na lista de fontes de dados do usuário
        dsn_list_path = "SOFTWARE\\ODBC\\ODBC.INI\\ODBC Data Sources"
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, dsn_list_path) as key:
            winreg.SetValueEx(key, odbc_name, 0, winreg.REG_SZ, "SQL Server")

        return True, f"✅ ODBC '{odbc_name}' criado com sucesso!"

    except Exception as e:
        return False, f"❌ Erro ao criar ODBC: {str(e)}"

def main():
    print("--- Iniciando Configuração de ODBC ---")
    
    if not is_admin():
        print("❌ Erro: Permissões de administrador insuficientes para manipular o registro.")
        return

    # Pega as variáveis do .env
    nome    = os.getenv("ODBC_NAME")
    banco   = os.getenv("BASE")
    user    = os.getenv("SA_USER", "sa") # Usando SA_USER ou sa por padrão
    senha   = os.getenv("SA_PASSWORD")
    server  = os.getenv("SERVIDOR_SQL", f".\\{os.getenv('INSTANCE_NAME', 'SQLEXPRESS')}")

    # Executa a criação
    sucesso, mensagem = criar_odbc(nome, banco, user, senha, server)
    
    print(mensagem)

if __name__ == "__main__":
    main()