document.addEventListener("DOMContentLoaded", () => {

    const tituloEstante = document.querySelector("#estante");

    const links = document.querySelectorAll(".link-prateleira");
    const prateleiras = document.querySelectorAll(".bloco-prateleira");

    function abrirPrateleira(id) {

        const selecionada = document.getElementById(id);

        if (!selecionada) return;

        // Se já estiver expandida, volta ao estado normal
        if (selecionada.classList.contains("expandida")) {

            prateleiras.forEach(prateleira => {
                prateleira.classList.remove("expandida");
                prateleira.classList.remove("minimizada");
            });

            return;
        }

        // Fecha/minimiza todas
        prateleiras.forEach(prateleira => {

            if (prateleira === selecionada) {
                prateleira.classList.add("expandida");
                prateleira.classList.remove("minimizada");
            } else {
                prateleira.classList.add("minimizada");
                prateleira.classList.remove("expandida");
            }

        });

        // Leva o usuário até a prateleira selecionada
        setTimeout(() => {

            selecionada.scrollIntoView({
                behavior: "smooth",
                block: "start"
            });

        }, 100);
    }


    links.forEach(link => {

        link.addEventListener("click", (evento) => {

            evento.preventDefault();

            const id = link.getAttribute("href").substring(1);

            abrirPrateleira(id);

            // Atualiza o endereço da página sem recarregar
            history.replaceState(null, "", `#${id}`);
        });

    });

    function voltarEstanteNormal() {

    prateleiras.forEach(prateleira => {
        prateleira.classList.remove("expandida");
        prateleira.classList.remove("minimizada");
    });

    history.replaceState(null, "", window.location.pathname);
    }

    tituloEstante.addEventListener("click", () => {
    voltarEstanteNormal();
    });


    // Se a página for aberta já com #lendo, #lidos ou #quero-ler
    const hash = window.location.hash.substring(1);

    if (hash) {
        abrirPrateleira(hash);
    }

});