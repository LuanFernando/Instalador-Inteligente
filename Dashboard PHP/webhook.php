<?php
// Configurações iniciais
$logFile = 'instalacoes_log.txt';
$timezone = new DateTimeZone('America/Sao_Paulo');
$now = new DateTime('now', $timezone);

// 1. Captura o corpo da requisição (JSON bruto)
$jsonRaw = file_get_contents('php://input');

// 2. Decodifica o JSON para um array associativo
$data = json_decode($jsonRaw, true);

// Verifica se o JSON é válido
if ($data) {
    $cnpjCliente = $data['cnpjCliente'] ?? 'N/A';
    $status    = $data['status']    ?? 'unknown';
    $software  = $data['software']  ?? 'N/A';
    $logErro   = $data['log_erro']  ?? 'Nenhum erro reportado.';
    
    // Captura dos novos dados técnicos enviados pelo Python
    $osDetail  = $data['win_version'] ?? 'N/A';
    $cpu       = $data['cpu']         ?? 'N/A';
    $ram       = $data['ram']         ?? 'N/A';
    $java      = $data['java']        ?? 'N/A';
    
    $dataHora  = $now->format('d/m/Y H:i:s');

    // 3. Formata a mensagem para o arquivo .txt
    // Mantenha os rótulos em CAIXA ALTA para facilitar o Regex do Dashboard
    $entry  = "====================================================\n";
    $entry .= "DATA/HORA: $dataHora\n";
    $entry .= "CLIENTE CNPJ: $cnpjCliente\n";
    $entry .= "SOFTWARE: $software\n";
    $entry .= "STATUS: " . strtoupper($status) . "\n";
    $entry .= "SISTEMA: $osDetail\n";
    $entry .= "CPU: $cpu\n";
    $entry .= "RAM: $ram\n";
    $entry .= "JAVA: $java\n";
    
    // Se for erro, adicionamos os detalhes no final
    if ($status === 'error' || !empty($logErro)) {
        $entry .= "DETALHES DO ERRO:\n$logErro\n";
    }
    
    $entry .= "====================================================\n\n";

    // 4. Salva no arquivo (FILE_APPEND para não sobrescrever)
    if (file_put_contents($logFile, $entry, FILE_APPEND)) {
        http_response_code(200);
        echo json_encode(["status" => "success", "message" => "Log técnico registrado"]);
    } else {
        http_response_code(500);
        echo json_encode(["status" => "error", "message" => "Erro de escrita no servidor"]);
    }
} else {
    http_response_code(400);
    echo json_encode(["status" => "error", "message" => "Payload JSON inválido"]);
}