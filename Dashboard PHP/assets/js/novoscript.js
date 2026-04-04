let markdownConteudo = "";

function gerarMarkdown() {
  const desc = document.getElementById("descricaoIA").value;
  const btn = document.getElementById("btnGerar");
  const loader = document.getElementById("loader");
  const outputArea = document.getElementById("outputArea");
  const btnDownload = document.getElementById("btnDownload");

  if (!desc) return alert("Por favor, descreva os passos da instalação.");

  // UI Feedback
  loader.style.display = "flex";
  btn.disabled = true;

  fetch("gerarscript.php", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ descricao: desc }),
  })
    .then((r) => r.json())
    .then((data) => {
      console.table(data.markdown);
      if (data.markdown) {
        markdownConteudo = data.markdown;
        // Renderiza o markdown de forma limpa
        outputArea.innerHTML = `<pre><code>${markdownConteudo}</code></pre>`;
        btnDownload.classList.remove("d-none");
        const statusIcon = document.getElementById("statusIcon");

        if (statusIcon) {
          statusIcon.classList.remove("d-none");
          statusIcon.innerHTML = '<i class="bi bi-check2-all"></i> PRONTO';
        }
      } else {
        outputArea.innerHTML = `<p class="text-danger">Erro: ${data.markdown}</p>`;
      }
    })
    .catch((err) => {
      console.log(err);
      outputArea.innerHTML = `<p class="text-danger">Erro crítico na comunicação com o PHP.</p>`;
    })
    .finally(() => {
      loader.style.display = "none";
      btn.disabled = false;
    });
}

function downloadMD() {
  const nome = document.getElementById("nomeSistema").value || "automacao_mq";
  const blob = new Blob([markdownConteudo], { type: "text/markdown" });
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `${nome}.md`;
  a.click();
}
