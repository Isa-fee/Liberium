document.addEventListener("DOMContentLoaded", function () {

    // ======================================
    // DADOS VINDOS DO FLASK
    // ======================================

    const elementoDados = document.getElementById("dados-home");

    if (!elementoDados) {
        return;
    }

    const dados = JSON.parse(elementoDados.textContent);

    const generosLabels = dados.generos_labels;
    const generosValores = dados.generos_valores;

    const totalLidos = dados.total_lidos;
    const totalLendo = dados.total_lendo;
    const totalQueroLer = dados.total_quero_ler;


    // ======================================
    // GRÁFICO DE GÊNEROS LIDOS
    // ======================================

    const canvasGeneros =
        document.getElementById("generosLidos");

    if (
        canvasGeneros &&
        generosValores.length > 0
    ) {

        new Chart(canvasGeneros, {

            type: "doughnut",

            data: {

                labels: generosLabels,

                datasets: [
                    {
                        data: generosValores,

                        backgroundColor: [
                            "#879d84",
                            "#36503c",
                            "#c8b39b",
                            "#a7b99f",
                            "#6c5338",
                            "#d7e2cf"
                        ],

                        borderWidth: 0
                    }
                ]
            },

            options: {
                responsive: true,
                maintainAspectRatio: true,
            
                plugins: {
                    legend: {
                        position: "bottom"
                    }
                }
            }
        });
    }


    // ======================================
    // GRÁFICO DA SITUAÇÃO DA ESTANTE
    // ======================================

    const canvasEstante =
    document.getElementById("livrosAndamento");

    const totalLivros =
        totalLidos +
        totalLendo +
        totalQueroLer;

    if (canvasEstante && totalLivros > 0) {

        new Chart(canvasEstante, {

            type: "doughnut",

            data: {

                labels: [
                    "Lidos",
                    "Lendo",
                    "Quero ler"
                ],

                datasets: [
                    {
                        data: [
                            totalLidos,
                            totalLendo,
                            totalQueroLer
                        ],

                        backgroundColor: [
                            "#36503c",
                            "#879d84",
                            "#c8b39b"
                        ],

                        borderWidth: 0
                    }
                ]
            },

            options: {
                responsive: true,
                maintainAspectRatio: true,
    
                plugins: {
                    legend: {
                        position: "bottom"
                    }
                }
            }
        });
    }

});