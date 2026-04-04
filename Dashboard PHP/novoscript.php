<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Instalador | Script Architect</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.1/font/bootstrap-icons.css">
    <link rel="stylesheet" href="assets/css/novoscript.css?v=1.1">
</head>
<body>

<nav class="navbar d-flex justify-content-between align-items-center">
    <div class="d-flex align-items-center">
        <a href="index.php" class="text-decoration-none text-dark me-3">
            <i class="bi bi-arrow-left fs-5"></i>
        </a>
        <h5 class="mb-0 fw-bold">Script Architect <span class="text-primary">AI</span></h5>
    </div>
    <div class="header-actions">
        <button class="btn btn-light border btn-sm" onclick="location.reload()">Limpar</button>
        <button id="btnDownload" class="btn btn-dark btn-sm d-none" onclick="downloadMD()">
            <i class="bi bi-download me-1"></i> Baixar Arquivo .md
        </button>
    </div>
</nav>

<div class="main-wrapper">
    <div class="config-panel">
        <div class="mb-4">
            <label class="form-label">IDENTIFICADOR DO SCRIPT</label>
            <input type="text" id="nomeSistema" class="input-modern w-100" placeholder="ex: instalacao_vendas_sql">
        </div>

        <div class="mb-3">
            <label class="form-label">DESCREVA OS PASSOS DA INSTALAÇÃO</label>
            <textarea id="descricaoIA" class="input-modern w-100" 
                placeholder="Ex: Crie a pasta C:\Sistema, dentro dela crie um .env com as chaves DB=123 e baixe o executável de http://link.com/app.exe"></textarea>
        </div>
        
        <p class="text-muted small">
            <i class="bi bi-info-circle me-1"></i> A IA formatará automaticamente os blocos <code>cmd</code> e <code>powershell</code> para o instalador.
        </p>

        <button class="btn-generate" id="btnGerar" onclick="gerarMarkdown()">
            <i class="bi bi-magic me-2"></i> Gerar Roteiro de Instalação
        </button>
    </div>

    <div class="preview-panel">
        <div class="loader-overlay" id="loader">
            <div class="spinner-border text-primary mb-3" role="status"></div>
            <span class="fw-medium text-secondary">Gemini 2.5 criando estrutura...</span>
        </div>

        <div class="card-preview">
            <div class="p-3 border-bottom d-flex justify-content-between align-items-center bg-white">
                <span class="small fw-bold text-muted text-uppercase">Preview do Markdown</span>
                <span id="statusIcon" class="text-success d-none small fw-bold"><i class="bi bi-check2-all"></i> PRONTO</span>
            </div>
            
            <div id="outputArea" class="code-container">
                <div class="text-center mt-5 text fw-light">
                    <i class="bi bi-code-square fs-1 mb-3 d-block"></i>
                    Aguardando descrição para gerar o código técnico...
                </div>
            </div>
        </div>
    </div>
</div>

<script src="assets/js/novoscript.js?v=1.2"></script>
</body>
</html>
