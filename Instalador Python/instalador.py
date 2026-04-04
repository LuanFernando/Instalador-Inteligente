import os
import ctypes
import sys
import subprocess
import re
import time
import requests
import json
import platform
from dotenv import load_dotenv

# Carrega as variáveis do arquivo .env
load_dotenv()

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def get_sys_info():
    """Coleta informações técnicas da máquina do cliente."""
    info = {}
    try:
        info['win_version'] = f"{platform.system()} {platform.release()} (Build {platform.version()})"
        info['cpu'] = platform.processor()
        
        # Memória RAM
        ram_cmd = subprocess.run(['wmic', 'computersystem', 'get', 'TotalPhysicalMemory'], capture_output=True, text=True)
        ram_match = re.search(r'\d+', ram_cmd.stdout)
        if ram_match:
            gb = int(ram_match.group()) / (1024**3)
            info['ram'] = f"{round(gb, 2)} GB"
        else:
            info['ram'] = "N/A"

        # Versão do Java
        try:
            java_cmd = subprocess.run(['java', '-version'], capture_output=True, text=True, stderr=subprocess.STDOUT)
            java_ver = re.search(r'\"(.+?)\"', java_cmd.stdout)
            info['java'] = java_ver.group(1) if java_ver else "Não instalado"
        except:
            info['java'] = "Não instalado"
    except Exception as e:
        print(f"Erro ao coletar info do sistema: {e}")
    return info

def enviar_notificacao_post(cnpj_cliente, status, nome_arquivo, erro_detalhado=""):
    webHookPainel = os.getenv("WEBHOOKPAINEL")
    if not webHookPainel:
        return

    sys_info = get_sys_info()
    payload = {
        "cnpjCliente": cnpj_cliente,
        "status": status,
        "software": nome_arquivo.replace('.md', '').upper(),
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "log_erro": erro_detalhado,
        "win_version": sys_info.get('win_version'),
        "cpu": sys_info.get('cpu'),
        "ram": sys_info.get('ram'),
        "java": sys_info.get('java')
    }
    
    try:
        print(f"\n[Monitor] Enviando status ({status}) ao dashboard...")
        requests.post(webHookPainel, json=payload, timeout=20)
    except:
        print("❌ Falha ao reportar para o servidor.")

def run_single_line(line, shell_type="powershell"):
    line = line.strip()
    if not line or line.startswith("#"):
        return True, ""

    print(f"   > Executando: {line}")

    if shell_type == "powershell":
        cmd_to_run = ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", line]
    else:
        cmd_to_run = line

    result = subprocess.run(cmd_to_run, capture_output=True, text=True, shell=True)
    
    if result.returncode != 0:
        erro_bruto = result.stderr if result.stderr else result.stdout
        return False, erro_bruto.strip()
    
    return True, ""

def parse_and_execute(nome_arquivo, cnpj_cliente):
    sucesso_geral = True
    logs_acumulados = []
    
    # AJUSTE: Busca o arquivo dentro da pasta MD
    caminho_completo = os.path.join('MD', nome_arquivo)
    
    try:
        with open(caminho_completo, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"❌ Erro ao abrir {nome_arquivo}: {e}")
        return

    blocks = re.findall(r"```(powershell|cmd)\s+(.*?)```", content, re.DOTALL)

    for shell_type, block_content in blocks:
        lines = block_content.strip().split('\n')
        for line in lines:
            sucesso, erro = run_single_line(line, shell_type)
            if not sucesso:
                sucesso_geral = False
                logs_acumulados.append(f"FALHA: [{line}] | ERRO: {erro}")
                print(f"   ❌ Erro na linha.")
                break 
        if not sucesso_geral: break

    status_final = "success" if sucesso_geral else "error"
    enviar_notificacao_post(cnpj_cliente, status_final, nome_arquivo, "\n".join(logs_acumulados))

if __name__ == "__main__":
    if not is_admin():
        print("!" * 50 + "\nERRO: EXECUTE COMO ADMINISTRADOR\n" + "!" * 50)
        input("Pressione Enter para sair...")
        sys.exit()

    print("\n==== INSTALADOR INTELIGENTE ====")
    cnpj_cliente = input("Digite o CNPJ do Cliente: ").strip()
    diretorio_md = 'MD'

    while True:
        if not os.path.exists(diretorio_md):
            print(f"Pasta '{diretorio_md}' não encontrada.")
            break

        arquivos = [f for f in os.listdir(diretorio_md) if f.endswith('.md')]

        if not arquivos:
            print("Nenhum arquivo .md na pasta MD.")
            break

        print(f"\n[MENU] CLIENTE: {cnpj_cliente}")
        for i, arquivo in enumerate(arquivos, 1):
            print(f"[{i}] {arquivo.upper()}")
        print("[0] Sair")
        
        escolha = input("\nOpção: ")
        if escolha == '0':
            os.system('cls' if os.name == 'nt' else 'clear')
            print("Finalizando... Até breve!")
            time.sleep(2)
            break
        
        try:
            idx = int(escolha) - 1
            if 0 <= idx < len(arquivos):
                parse_and_execute(arquivos[idx], cnpj_cliente)
                print("\nConcluído.")
                input("Enter para voltar...")
        except ValueError:
            print("Opção inválida.")