// 1. Auto-refresh inteligente com contador visual
let timeLeft = 30;
const refreshElement = document.querySelector(".refresh-indicator");

if (refreshElement) {
  setInterval(() => {
    timeLeft--;
    if (timeLeft <= 0) {
      window.location.reload();
    }
    refreshElement.innerHTML = `<i class="bi bi-arrow-clockwise"></i> Atualizando em ${timeLeft}s...`;
  }, 1000);
}

/**
 * 2. Integração com Gemini (Evoluída com Contexto de Hardware)
 * @param {HTMLElement} botao - O botão clicado
 * @param {string} erroTexto - O log de erro capturado
 * @param {string} ram - RAM do cliente
 * @param {string} java - Versão do Java
 * @param {string} sistema - Versão do Windows
 */
function analisarComIA(
  botao,
  erroTexto,
  ram = "N/A",
  java = "N/A",
  sistema = "N/A",
) {
  // Seleciona o container de resultado (próximo ao botão)
  const container =
    botao.nextElementSibling ||
    botao.parentElement.querySelector(".resultado-ia-container");

  // UI Feedback
  botao.disabled = true;
  botao.innerHTML =
    '<span class="spinner-border spinner-border-sm"></span> Diagnosticando...';
  container.innerHTML =
    '<div class="text-muted"><i class="bi bi-cpu-fill"></i> Cruzando dados de hardware e logs...</div>';

  // Enviamos o erro + contexto técnico para uma análise precisa
  fetch("analisarerro.php", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      erro: erroTexto,
      contexto: {
        memoria_ram: ram,
        versao_java: java,
        sistema_operacional: sistema,
      },
    }),
  })
    .then((response) => {
      if (!response.ok) throw new Error("Erro no servidor PHP");
      return response.json();
    })
    .then((data) => {
      // Formata a resposta da IA (Substituindo quebras de linha e negritos simples)
      const analiseFormatada = data.analise
        .replace(/\n/g, "<br>")
        .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>");

      container.innerHTML = `
            <div class="ai-box p-3 mt-2 shadow-sm border-start border-primary border-4 bg-white">
                <div class="d-flex align-items-center mb-2">
                    <i class="bi bi-robot me-2 text-primary fs-5"></i>
                    <strong class="text-primary text-uppercase small">Parecer da IA MQ Soft</strong>
                </div>
                <div class="small text-dark lh-base">${analiseFormatada}</div>
                <hr class="my-2 opacity-25">
                <div class="x-small text-muted" style="font-size: 0.7rem;">
                    Análise baseada em ${ram} RAM e log de terminal.
                </div>
            </div>`;

      botao.innerHTML = '<i class="bi bi-arrow-repeat"></i> Reanalisar';
      botao.disabled = false;
    })
    .catch((err) => {
      console.error("Erro IA:", err);
      container.innerHTML = `
            <div class="alert alert-warning mt-2 small">
                <i class="bi bi-exclamation-triangle"></i> Não foi possível obter o diagnóstico agora.
            </div>`;
      botao.disabled = false;
      botao.innerHTML = '<i class="bi bi-magic"></i> Tentar Novamente';
    });
}
