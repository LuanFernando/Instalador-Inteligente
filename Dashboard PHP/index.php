<?php
$logFile = 'instalacoes_log.txt';
$logs = [];

if (file_exists($logFile)) {
    $content = file_get_contents($logFile);
    $entries = explode("====================================================", $content);
    
    foreach ($entries as $entry) {
        $entry = trim($entry);
        if (empty($entry)) continue;

        // Captura básica
        preg_match('/DATA\/HORA: (.*)/', $entry, $dataHora);
        preg_match('/CLIENTE CNPJ: (.*)/', $entry, $cnpjCliente);
        preg_match('/SOFTWARE: (.*)/', $entry, $software);
        preg_match('/STATUS: (.*)/', $entry, $status);
        
        // Captura de Hardware e Sistema (Novos campos)
        preg_match('/SISTEMA: (.*)/', $entry, $sistema);
        preg_match('/CPU: (.*)/', $entry, $cpu);
        preg_match('/RAM: (.*)/', $entry, $ram);
        preg_match('/JAVA: (.*)/', $entry, $java);
        
        $erro = "";
        if (strpos($entry, "DETALHES DO ERRO:") !== false) {
            $parts = explode("DETALHES DO ERRO:", $entry);
            $erro = trim($parts[1]);
        }

        $logs[] = [
            'data' => $dataHora[1] ?? 'N/A',
            'cliente' => $cnpjCliente[1] ?? 'N/A',
            'software' => $software[1] ?? 'N/A',
            'status' => trim($status[1] ?? 'UNKNOWN'),
            'sistema' => $sistema[1] ?? 'N/A',
            'cpu' => $cpu[1] ?? 'N/A',
            'ram' => $ram[1] ?? 'N/A',
            'java' => $java[1] ?? 'N/A',
            'erro' => $erro
        ];
    }
    $logs = array_reverse($logs);
}
?>

<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Instalador | Terminal Monitor</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.1/font/bootstrap-icons.css">
    <link rel="stylesheet" href="assets/css/index.css?v=1.1">
</head>
<body class="bg-light">

<nav class="navbar mb-4 sticky-top">
    <div class="container">
        <span class="navbar-brand mb-0 h1 fw-bold">
            <i class="bi bi-cpu text-primary"></i> Instalador <span class="fw-light text-muted">Monitor</span>
        </span>
        <div class="d-flex align-items-center gap-3">
            <a href="novoscript.php" class="btn btn-primary btn-sm">
                <i class="bi bi-magic"></i> Arquiteto de Script
            </a>
            <div class="refresh-indicator">
                <i class="bi bi-arrow-clockwise"></i> Atualizando em 30s...
            </div>
        </div>
    </div>
</nav>

<div class="container">
    <div class="row mb-4">
        <div class="col-md-3">
            <div class="card p-3 shadow-sm border-0">
                <small class="text-muted fw-bold text-uppercase" style="font-size: 0.65rem;">Instalações Hoje</small>
                <h3 class="fw-bold mb-0 text-primary"><?php echo count($logs); ?></h3>
            </div>
        </div>
    </div>

    <div class="row">
        <?php foreach ($logs as $index => $log): 
            $isError = (trim(strtolower($log['status'])) === 'error');
        ?>
        <div class="col-12">
            <div class="card install-card bg-white">
                <div class="card-body p-4">
                    <div class="d-flex align-items-start justify-content-between flex-wrap">
                        
                        <div class="d-flex">
                            <div class="me-4">
                                <i class="bi <?php echo $isError ? 'bi-x-circle-fill text-danger' : 'bi-check-circle-fill text-success'; ?> fs-1"></i>
                            </div>
                            <div>
                                <h5 class="mb-1 fw-bold"><?php echo htmlspecialchars($log['software']); ?></h5>
                                <div class="mb-2">
                                    <span class="sys-badge"><i class="bi bi-windows"></i> <?php echo $log['sistema']; ?></span>
                                    <span class="sys-badge"><i class="bi bi-memory"></i> RAM: <?php echo $log['ram']; ?></span>
                                    <span class="sys-badge"><i class="bi bi-speedometer2"></i> CPU: <?php echo substr($log['cpu'], 0, 20); ?>...</span>
                                    <span class="sys-badge"><i class="bi bi-code-slash"></i> Java: <?php echo $log['java']; ?></span>
                                </div>
                                <p class="mb-0 text-muted small">
                                    <strong>CNPJ: <?php echo $log['cliente']; ?></strong> • 
                                    <i class="bi bi-clock me-1"></i><?php echo $log['data']; ?>
                                </p>
                            </div>
                        </div>

                        <div class="text-end">
                            <div class="mb-2">
                                <span class="status-badge <?php echo $isError ? 'status-error' : 'status-success'; ?>">
                                    <?php echo $log['status']; ?>
                                </span>
                            </div>
                            <?php if ($isError): ?>
                                <button class="btn btn-sm btn-outline-dark" type="button" data-bs-toggle="collapse" data-bs-target="#err-<?php echo $index; ?>">
                                    <i class="bi bi-search"></i> Ver Erro
                                </button>
                            <?php endif; ?>
                        </div>
                    </div>
                </div>

                <?php if ($isError): ?>
                <div class="collapse" id="err-<?php echo $index; ?>">
                    <div class="card-footer border-0 bg-light p-4">
                        <div class="row">
                            <div class="col-md-7">
                                <p class="mb-2 fw-bold small text-uppercase text-danger"><i class="bi bi-terminal"></i> Log de Execução:</p>
                                <div class="log-terminal mb-3">
                                    <code><?php echo nl2br(htmlspecialchars($log['erro'])); ?></code>
                                </div>
                            </div>
                            <div class="col-md-5">
                                <p class="mb-2 fw-bold small text-uppercase text-primary"><i class="bi bi-robot"></i> Diagnóstico IA:</p>
                                <button class="btn btn-primary w-100 mb-2" onclick="analisarComIA(this, '<?php echo addslashes($log['erro']); ?>', '<?php echo $log['ram']; ?>', '<?php echo $log['java']; ?>')">
                                    <i class="bi bi-magic"></i> Perguntar ao Gemini
                                </button>
                                <div class="resultado-ia-container p-3 bg-white border rounded small text-muted" style="min-height: 100px;">
                                    Clique no botão para analisar as causas técnicas.
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                <?php endif; ?>
            </div>
        </div>
        <?php endforeach; ?>
    </div>
</div>

<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
<script src="assets/js/script.js?v=1.2"></script>
</body>
</html>