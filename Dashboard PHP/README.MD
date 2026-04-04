## INSTALADOR INTELIGENTE

# Sobre o Projeto

O Instalador Inteligente é uma solução genérica para automação de instalação e configuração de softwares, projetada para ser utilizada por empresas que desejam padronizar, escalar e monitorar seus processos de deploy.

A plataforma foi construída para ser flexível, extensível e orientada à automação, permitindo que diferentes tipos de sistemas sejam instalados de forma simples e controlada.

# Arquitetura da Solução

O projeto é dividido em duas principais frentes:

# 1. Instalador (Python - CLI)

Executado via terminal (CMD / PowerShell)
Responsável por:
Ler scripts de instalação definidos em arquivos .md
Executar comandos automaticamente
Registrar logs de sucesso e erro
Enviar resultados para o dashboard via webhook

# 2. Dashboard (PHP)

Interface web para monitoramento das instalações
Atualização automática a cada 30 segundos
Funcionalidades:
Visualização em tempo real das instalações
Histórico de execuções
Exibição detalhada de erros
Integração com IA para sugestão de soluções
Criação assistida de scripts de instalação

# Recursos com Inteligência Artificial

O sistema conta com suporte à IA para aumentar a produtividade:

# Diagnóstico de Erros

Quando uma instalação falha:

O erro é exibido no dashboard
A IA pode ser utilizada para:
Interpretar o erro
Sugerir possíveis soluções
Acelerar o suporte técnico

# Geração de Scripts

O dashboard permite gerar scripts automaticamente com base em linguagem natural.

- Exemplo:

Entrada:

Crie uma pasta chamada MEUSISTEMA no C:
Dentro da pasta MEUSISTEMA adicione uma subpasta CONFIG, e dentro um .env

Saída gerada:

mkdir C:\MEUSISTEMA
mkdir C:\MEUSISTEMA\CONFIG
echo. > "C:\MEUSISTEMA\CONFIG\.env"

# Estrutura de Scripts

Os scripts de instalação são definidos em arquivos .md, permitindo:

Fácil leitura e manutenção
Versionamento
Padronização dos processos de instalação

# Configuração Importante

# WEBHOOK DO PAINEL

Para que o sistema funcione corretamente, é obrigatório configurar no python:

WEBHOOKPAINEL = URL_DO_DASHBOARD_PHP

- Essa URL é responsável por receber:

Status de sucesso
Logs de erro
Informações da execução

Sem essa configuração, o monitoramento não funcionará corretamente.

# RUN

- composer install
