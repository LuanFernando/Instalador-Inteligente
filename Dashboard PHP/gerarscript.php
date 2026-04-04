<?php
require __DIR__ . '/vendor/autoload.php';

use Dotenv\Dotenv;

// Caminho da pasta onde está o .env
$dotenv = Dotenv::createImmutable(__DIR__);
$dotenv->load();

header('Content-Type: application/json');

$apiKey  = $_ENV['APIKEY']; // Pegue em: https://aistudio.google.com/

// Entrada do usuário
$jsonRaw = file_get_contents('php://input');
$data = json_decode($jsonRaw, true);

// Função para forçar saída padrão CMD
function formatarSaidaCmd($texto) {
    $texto = trim($texto);

    // Remove blocos markdown existentes
    $texto = preg_replace('/```(cmd|powershell)?/i', '', $texto);

    // Quebra linhas
    $linhas = explode("\n", $texto);
    $comandos = [];

    foreach ($linhas as $linha) {
        $linha = trim($linha);

        // Filtra comandos válidos básicos
        if (!empty($linha) && preg_match('/^(mkdir|echo|copy|move|del|type|curl|powershell)/i', $linha)) {
            $comandos[] = $linha;
        }
    }

    // Caso não venha nada válido, evita retorno vazio
    if (empty($comandos)) {
        return "```cmd\necho Nenhum comando válido gerado\n```";
    }

    return "```cmd\n" . implode("\n", $comandos) . "\n```";
}

// Validação de entrada
if (!isset($data['descricao']) || empty($data['descricao'])) {
    echo json_encode([
        "error" => "Parâmetro 'descricao' é obrigatório"
    ]);
    exit;
}

// Prompt otimizado
$prompt = "Atue como um Especialista em Automação de Sistemas Windows.

Sua tarefa é converter a DESCRIÇÃO fornecida em uma sequência lógica de comandos para o Prompt de Comando (CMD). 
Siga rigorosamente estas diretrizes:

1. Formatação: Responda exclusivamente com um bloco de código iniciado por ```cmd.

2. Silêncio Total: Não inclua introduções, explicações, avisos ou notas de rodapé. A saída deve conter apenas código.

3. Sintaxe: Um comando por linha. Use comandos nativos do CMD ou chame o PowerShell via powershell -Command '...' para operações complexas (como instalações e verificações condicionais).

4. Resiliência: Se a descrição solicitar a instalação de uma ferramenta, use o winget com os parâmetros --accept-source-agreements --accept-package-agreements para evitar interrupções interativas.

5. Downloads: Caso precise baixar algo sem URL específica, utilize o winget search ou comandos de busca via PowerShell para identificar e instalar a versão mencionada.

6. Caminhos: Use barras invertidas duplas \\ ou caminhos entre aspas para evitar erros de diretório.

EXEMPLO DE SAÍDA:
```cmd
mkdir C:\\PASTA
mkdir C:\\PASTA\\SUBPASTA
powershell -Command 'if (!(Get-Command docker -ErrorAction SilentlyContinue)) { winget install -e --id Docker.DockerDesktop --accept-source-agreements --accept-package-agreements; Start-Process 'C:\Program Files\Docker\Docker\Docker Desktop.exe'; while (!(docker info 2>nul)) { Start-Sleep -Seconds 5 } } else { echo 'Docker detectado' }'
docker pull php:8.2-apache
docker rm -f meu-servidor-php
docker run -d --name meu-servidor-php -p 8080:80 php:8.2-apache
DESCRIÇÃO:
" . $data['descricao'];

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

// Erro CURL
if (curl_errno($ch)) {
echo json_encode([
"error" => "Erro CURL: " . curl_error($ch)
]);
curl_close($ch);
exit;
}

curl_close($ch);

// Decodifica resposta
$result = json_decode($response, true);

// Extrai texto da IA
$markdownRaw = $result['candidates'][0]['content']['parts'][0]['text'] ?? "";

// Sanitiza e padroniza saída
$markdownGerado = formatarSaidaCmd($markdownRaw);

// Retorno final
echo json_encode([
"markdown" => $markdownGerado
]);
