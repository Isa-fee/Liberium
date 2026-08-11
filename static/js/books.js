const modal = document.getElementById("modal-avaliacao");
const abrirModal = document.getElementById("abrir-modal-avaliacao");
const fecharModal = document.getElementById("fechar-modal-avaliacao");
const cancelarModal = document.getElementById("cancelar-modal-avaliacao");

abrirModal.addEventListener("click", () => {
    modal.classList.add("aberto");
    modal.setAttribute("aria-hidden", "false");
});

function fecharAvaliacao() {
    modal.classList.remove("aberto");
    modal.setAttribute("aria-hidden", "true");
}

fecharModal.addEventListener("click", fecharAvaliacao);
cancelarModal.addEventListener("click", fecharAvaliacao);

modal.addEventListener("click", (event) => {
    if (event.target === modal) {
        fecharAvaliacao();
    }
});


const estrelas = document.querySelectorAll(".estrela");
const campoNota = document.getElementById("nota-avaliacao");

estrelas.forEach((estrela) => {
    estrela.addEventListener("click", () => {
        const nota = Number(estrela.dataset.nota);

        campoNota.value = nota;

        estrelas.forEach((item) => {
            const valor = Number(item.dataset.nota);

            item.textContent = valor <= nota ? "★" : "☆";
        });
    });
});