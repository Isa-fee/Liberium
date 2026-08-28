document.addEventListener("DOMContentLoaded", () => {

    const carrossel =
        document.querySelector(".carrossel-cards");

    const btnLeft =
        document.querySelector(".carrossel-btn.left");

    const btnRight =
        document.querySelector(".carrossel-btn.right");


    // ==========================================
    // VERIFICA SE O CARROSSEL EXISTE
    // ==========================================

    if (
        !carrossel ||
        !btnLeft ||
        !btnRight
    ) {
        return;
    }


    const livros = Array.from(
        carrossel.querySelectorAll(".livro-sugestao")
    );


    // Se não houver livros, não há o que navegar
    if (livros.length === 0) {

        btnLeft.style.display = "none";
        btnRight.style.display = "none";

        return;
    }


    // ==========================================
    // TAMANHO DO DESLOCAMENTO
    // ==========================================

    function obterDistancia() {

        const primeiroLivro = livros[0];

        const estiloCarrossel =
            window.getComputedStyle(carrossel);

        const gap =
            parseFloat(estiloCarrossel.columnGap) || 0;

        return primeiroLivro.offsetWidth + gap;
    }


    // ==========================================
    // NAVEGAÇÃO
    // ==========================================

    btnRight.addEventListener("click", () => {

        carrossel.scrollBy({
            left: obterDistancia(),
            behavior: "smooth"
        });

    });


    btnLeft.addEventListener("click", () => {

        carrossel.scrollBy({
            left: -obterDistancia(),
            behavior: "smooth"
        });

    });


    // ==========================================
    // ESTADO DOS BOTÕES
    // ==========================================

    function atualizarBotoes() {

        const limite =
            carrossel.scrollWidth -
            carrossel.clientWidth;

        const estaNoInicio =
            carrossel.scrollLeft <= 2;

        const estaNoFim =
            carrossel.scrollLeft >= limite - 2;


        btnLeft.disabled = estaNoInicio;
        btnRight.disabled = estaNoFim;

    }


    carrossel.addEventListener(
        "scroll",
        atualizarBotoes
    );


    window.addEventListener(
        "resize",
        atualizarBotoes
    );


    atualizarBotoes();

});