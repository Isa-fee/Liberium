// document.addEventListener("DOMContentLoaded", () => {

//     const tituloEstante = document.querySelector("#estante");

//     const links = document.querySelectorAll(".link-prateleira");
//     const prateleiras = document.querySelectorAll(".bloco-prateleira");

//     function abrirPrateleira(id) {

//         const selecionada = document.getElementById(id);

//         if (!selecionada) return;

//         // Se já estiver expandida, volta ao estado normal
//         if (selecionada.classList.contains("expandida")) {

//             prateleiras.forEach(prateleira => {
//                 prateleira.classList.remove("expandida");
//                 prateleira.classList.remove("minimizada");
//             });

//             return;
//         }

//         // Fecha/minimiza todas
//         prateleiras.forEach(prateleira => {

//             if (prateleira === selecionada) {
//                 prateleira.classList.add("expandida");
//                 prateleira.classList.remove("minimizada");
//             } else {
//                 prateleira.classList.add("minimizada");
//                 prateleira.classList.remove("expandida");
//             }

//         });

//         // Leva o usuário até a prateleira selecionada
//         setTimeout(() => {

//             selecionada.scrollIntoView({
//                 behavior: "smooth",
//                 block: "start"
//             });

//         }, 100);
//     }


//     links.forEach(link => {

//         link.addEventListener("click", (evento) => {

//             evento.preventDefault();

//             const id = link.getAttribute("href").substring(1);

//             abrirPrateleira(id);

//             // Atualiza o endereço da página sem recarregar
//             history.replaceState(null, "", `#${id}`);
//         });

//     });

//     function voltarEstanteNormal() {

//     prateleiras.forEach(prateleira => {
//         prateleira.classList.remove("expandida");
//         prateleira.classList.remove("minimizada");
//     });

//     history.replaceState(null, "", window.location.pathname);
//     }

//     tituloEstante.addEventListener("click", () => {
//     voltarEstanteNormal();
//     });


//     // Se a página for aberta já com #lendo, #lidos ou #quero-ler
//     const hash = window.location.hash.substring(1);

//     if (hash) {
//         abrirPrateleira(hash);
//     }

//  // =========================================
//     // ORGANIZAÇÃO DA ESTANTE
//     // =========================================

//     const linhasPrateleira = document.querySelectorAll(".linha-prateleira");

//     linhasPrateleira.forEach(linha => {

//         let itemArrastado = null;

//         linha.querySelectorAll(".item-arrastavel").forEach(item => {

//             item.setAttribute("draggable", "true");

//             item.addEventListener("dragstart", () => {

//                 itemArrastado = item;

//                 item.dataset.prateleiraOriginal =
//                     linha.dataset.prateleira;

//                 item.classList.add("arrastando");
//             });

//             item.addEventListener("dragend", () => {
//                 item.classList.remove("arrastando");
//                 itemArrastado = null;
//             });

//         });

//         linha.addEventListener("dragover", evento => {

//             evento.preventDefault();

//             if (!itemArrastado) return;

//             const itemDepois = encontrarItemDepois(linha, evento.clientX);

//             if (!itemDepois) {
//                 linha.appendChild(itemArrastado);
//             } else {
//                 linha.insertBefore(itemArrastado, itemDepois);
//             }

//         });

//         linha.addEventListener("drop", async evento => {

//             evento.preventDefault();

//             if (!itemArrastado) return;

//             const prateleiraDestino =
//                 linha.dataset.prateleira;

//             const tipo =
//                 itemArrastado.dataset.tipo;

//             const id =
//                 itemArrastado.dataset.id;

//             // =====================================
//             // LIVRO
//             // =====================================
//             // Livro NÃO pode mudar de prateleira.

//             // if (tipo === "livro") {

//             //     const prateleiraOriginal =
//             //         itemArrastado.closest(".linha-prateleira")
//             //         ?.dataset.prateleira;

//             //     if (
//             //         prateleiraOriginal &&
//             //         prateleiraOriginal !== prateleiraDestino
//             //     ) {
//             //         return;
//             //     }
//             // }

//             if (tipo === "livro") {

//                 const prateleiraOriginal =
//                     itemArrastado.dataset.prateleiraOriginal;

//                 if (
//                     prateleiraOriginal !== prateleiraDestino
//                 ) {

//                     return;
//                 }
//             }

//             // =====================================
//             // SALVAR NOVA ORDEM
//             // =====================================

//             const itens = [
//                 ...linha.querySelectorAll(".item-arrastavel")
//             ];

//             const ordem = itens.map((item, posicao) => ({
//                 id: Number(item.dataset.id),
//                 tipo: item.dataset.tipo,
//                 posicao: posicao
//             }));

//             try {

//                 const resposta = await fetch(
//                     "{{ url_for('estante_bp.reordenar_estante') }}",
//                     {
//                         method: "POST",

//                         headers: {
//                             "Content-Type": "application/json"
//                         },

//                         body: JSON.stringify({
//                             prateleira: prateleiraDestino,
//                             ordem: ordem
//                         })
//                     }
//                 );

//                 const dados = await resposta.json();

//                 if (!dados.sucesso) {
//                     console.error(
//                         "Erro ao salvar a ordem:",
//                         dados.erro
//                     );
//                 }

//             } catch (erro) {

//                 console.error(
//                     "Erro ao salvar a estante:",
//                     erro
//                 );

//             }

//         });

//     });


//     function encontrarItemDepois(linha, mouseX) {

//         const itens = [
//             ...linha.querySelectorAll(
//                 ".item-arrastavel:not(.arrastando)"
//             )
//         ];

//         return itens.reduce(
//             (itemMaisProximo, itemAtual) => {

//                 const caixa =
//                     itemAtual.getBoundingClientRect();

//                 const distancia =
//                     mouseX -
//                     caixa.left -
//                     caixa.width / 2;

//                 if (
//                     distancia < 0 &&
//                     distancia >
//                     itemMaisProximo.distancia
//                 ) {

//                     return {
//                         distancia: distancia,
//                         elemento: itemAtual
//                     };

//                 }

//                 return itemMaisProximo;

//             },
//             {
//                 distancia: Number.NEGATIVE_INFINITY,
//                 elemento: null
//             }
//         ).elemento;
//     }

// });


document.addEventListener("DOMContentLoaded", () => {

    const tituloEstante = document.querySelector("#estante");
    const links = document.querySelectorAll(".link-prateleira");
    const prateleiras = document.querySelectorAll(".bloco-prateleira");


    // =========================================
    // ABRIR PRATELEIRA
    // =========================================

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


    // =========================================
    // LINKS DAS PRATELEIRAS
    // =========================================

    links.forEach(link => {

        link.addEventListener("click", evento => {

            evento.preventDefault();

            const id =
                link.getAttribute("href").substring(1);

            abrirPrateleira(id);

            history.replaceState(
                null,
                "",
                `#${id}`
            );

        });

    });


    // =========================================
    // VOLTAR AO ESTADO NORMAL
    // =========================================

    function voltarEstanteNormal() {

        prateleiras.forEach(prateleira => {

            prateleira.classList.remove("expandida");
            prateleira.classList.remove("minimizada");

        });

        history.replaceState(
            null,
            "",
            window.location.pathname
        );
    }


    tituloEstante.addEventListener(
        "click",
        voltarEstanteNormal
    );


    // =========================================
    // ABRIR PELO HASH
    // =========================================

    const hash =
        window.location.hash.substring(1);

    if (hash) {
        abrirPrateleira(hash);
    }


    // =========================================
    // DRAG AND DROP
    // =========================================

    const linhasPrateleira =
        document.querySelectorAll(".linha-prateleira");


    let itemArrastado = null;


    linhasPrateleira.forEach(linha => {

        const itens =
            linha.querySelectorAll(".item-arrastavel");


        // =====================================
        // PREPARAR ITENS
        // =====================================

        itens.forEach(item => {

            item.setAttribute(
                "draggable",
                "true"
            );


            item.addEventListener(
                "dragstart",
                evento => {

                    itemArrastado = item;

                    // Guarda onde o item começou.
                    item.dataset.prateleiraOriginal =
                        linha.dataset.prateleira;

                    item.classList.add(
                        "arrastando"
                    );

                    evento.dataTransfer.effectAllowed =
                        "move";

                }
            );


            item.addEventListener(
                "dragend",
                () => {

                    item.classList.remove(
                        "arrastando"
                    );

                    itemArrastado = null;

                }
            );

        });


        // =====================================
        // ARRASTAR SOBRE A PRATELEIRA
        // =====================================

        linha.addEventListener(
            "dragover",
            evento => {

                evento.preventDefault();

                if (!itemArrastado) return;


                const tipo =
                    itemArrastado.dataset.tipo;

                const prateleiraOrigem =
                    itemArrastado.dataset
                        .prateleiraOriginal;

                const prateleiraDestino =
                    linha.dataset.prateleira;


                // =================================
                // LIVRO
                // =================================

                // Livro só pode ser movimentado
                // dentro da prateleira original.

                if (
                    tipo === "livro" &&
                    prateleiraOrigem !==
                    prateleiraDestino
                ) {

                    evento.dataTransfer.dropEffect =
                        "none";

                    return;
                }


                evento.dataTransfer.dropEffect =
                    "move";


                // =================================
                // ENCONTRAR POSIÇÃO
                // =================================

                const itemDepois =
                    encontrarItemDepois(
                        linha,
                        evento.clientX
                    );


                if (!itemDepois) {

                    linha.appendChild(
                        itemArrastado
                    );

                } else {

                    linha.insertBefore(
                        itemArrastado,
                        itemDepois
                    );

                }

            }
        );


        // =====================================
        // SOLTAR
        // =====================================

        linha.addEventListener(
            "drop",
            async evento => {

                evento.preventDefault();

                if (!itemArrastado) return;


                const tipo =
                    itemArrastado.dataset.tipo;

                const prateleiraOrigem =
                    itemArrastado.dataset
                        .prateleiraOriginal;

                const prateleiraDestino =
                    linha.dataset.prateleira;


                // =================================
                // IMPEDIR LIVRO DE TROCAR
                // =================================

                if (
                    tipo === "livro" &&
                    prateleiraOrigem !==
                    prateleiraDestino
                ) {

                    // Recarrega para devolver
                    // o elemento visualmente
                    // para o lugar correto.

                    window.location.reload();

                    return;
                }


                // =================================
                // PEGAR NOVA ORDEM
                // =================================

                const itens =
                    Array.from(
                        linha.querySelectorAll(
                            ".item-arrastavel"
                        )
                    );


                const ordem =
                    itens.map(
                        (item, posicao) => {

                            return {
                                id: Number(
                                    item.dataset.id
                                ),

                                tipo:
                                    item.dataset.tipo,

                                posicao:
                                    posicao
                            };

                        }
                    );


                // =================================
                // ENVIAR PARA O FLASK
                // =================================

                try {

                    const resposta =
                        await fetch(
                            "/books/estante/reordenar",
                            {
                                method: "POST",

                                headers: {
                                    "Content-Type":
                                        "application/json"
                                },

                                body:
                                    JSON.stringify({
                                        prateleira:
                                            prateleiraDestino,

                                        ordem:
                                            ordem
                                    })
                            }
                        );


                    const dados =
                        await resposta.json();


                    if (!dados.sucesso) {

                        console.error(
                            "Erro ao salvar:",
                            dados.erro
                        );

                        window.location.reload();

                    }


                } catch (erro) {

                    console.error(
                        "Erro ao salvar a ordem:",
                        erro
                    );

                    window.location.reload();

                }

            }
        );

    });


    // =========================================
    // ENCONTRAR ITEM MAIS PRÓXIMO
    // =========================================

    function encontrarItemDepois(
        linha,
        mouseX
    ) {

        const itens =
            Array.from(
                linha.querySelectorAll(
                    ".item-arrastavel:not(.arrastando)"
                )
            );


        let itemMaisProximo = null;

        let menorDistancia =
            Number.NEGATIVE_INFINITY;


        itens.forEach(item => {

            const caixa =
                item.getBoundingClientRect();


            const distancia =
                mouseX -
                caixa.left -
                caixa.width / 2;


            if (
                distancia < 0 &&
                distancia >
                menorDistancia
            ) {

                menorDistancia =
                    distancia;

                itemMaisProximo =
                    item;

            }

        });


        return itemMaisProximo;
    }

});