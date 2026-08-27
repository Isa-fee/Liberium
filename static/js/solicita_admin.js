function alternarSinopse(id, botao) {

    const sinopse = document.getElementById(
        `sinopse-${id}`
    );

    if (!sinopse) {
        return;
    }

    sinopse.classList.toggle("expandida");

    if (sinopse.classList.contains("expandida")) {
        botao.textContent = "Ver menos";
    } else {
        botao.textContent = "Ver mais";
    }
}