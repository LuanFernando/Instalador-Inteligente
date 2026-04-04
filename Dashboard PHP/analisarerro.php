<?php

require __DIR__ . '/vendor/autoload.php';

use Dotenv\Dotenv;

// Caminho da pasta onde está o .env
$dotenv = Dotenv::createImmutable(__DIR__);
$dotenv->load();

header('Content-Type: application/json');

$apiKey  = $_ENV['APIKEY']; // Pegue em: https://aistudio.google.com/
$jsonRaw = file_get_contents('php://input');
$data = json_decode($jsonRaw, true);

if (isset($data['erro'])) {
    $erroBruto = $data['erro'];
    
    // Prompt estratégico para a LLM
    $prompt = "Você é um especialista em suporte técnico Windows. 
               Analise o seguinte erro de instalação e forneça:
               1. Causa provável.
               2. O comando exato para resolver (PowerShell ou CMD).
               Erro: " . $erroBruto;

    $url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key=" . $apiKey;

    $payload = [
        "contents" => [
            ["parts" => [["text" => $prompt]]]
        ]
    ];

    $ch = curl_init($url);
	curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, false);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    curl_setopt($ch, CURLOPT_POST, true);
    curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode($payload));
    curl_setopt($ch, CURLOPT_HTTPHEADER, ['Content-Type: application/json']);
    
    $response = curl_exec($ch);
    $result = json_decode($response, true);
    
    // Extrai apenas o texto da resposta
    $textoIA = $result['candidates'][0]['content']['parts'][0]['text'] ?? "Não foi possível analisar o erro.";
    
    echo json_encode(["analise" => $textoIA]);
}