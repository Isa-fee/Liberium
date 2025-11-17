document.addEventListener("DOMContentLoaded", () => {
    // 📏 Verifica se a largura da tela é maior que 600px
    // O carrossel com JS (smooth scroll e loop) só será ativado em telas maiores
    if (window.matchMedia("(min-width: 601px)").matches) { 

        const carrossel = document.querySelector(".carrossel-cards");
        const btnLeft = document.querySelector(".carrossel-btn.left");
        const btnRight = document.querySelector(".carrossel-btn.right");

        // Verifica se os elementos necessários existem antes de prosseguir
        if (!carrossel || !btnLeft || !btnRight) {
            console.error("Elementos do carrossel não encontrados. Verifique o HTML.");
            return;
        }

        const cards = Array.from(carrossel.querySelectorAll(".card"));
        // Largura do card (180px) + gap (20px, conforme style.css)
        const cardWidth = cards[0].offsetWidth + 20; 

        // --- 1. Clonagem de Cards para Loop Infinito ---
        cards.forEach(card => {
            // Clona e adiciona no final
            const cloneEnd = card.cloneNode(true);
            carrossel.appendChild(cloneEnd);
            
            // Clona e adiciona no início
            const cloneStart = card.cloneNode(true);
            carrossel.insertBefore(cloneStart, carrossel.firstChild);
        });

        // Posição inicial: move o scroll para o primeiro conjunto real de cards
        // Isso esconde os clones iniciais
        carrossel.scrollLeft = cardWidth * cards.length;


        // --- 2. Funções de Easing e Scroll Suave ---

        // Função de easing (desaceleração)
        function easeInOutQuad(t, b, c, d) {
            t /= d/2;
            if (t < 1) return c/2*t*t + b;
            t--;
            return -c/2 * (t*(t-2) - 1) + b;
        }
        
        // Função de scroll suave usando requestAnimationFrame
        function smoothScroll(element, target, duration) {
            const start = element.scrollLeft;
            const change = target - start;
            const increment = 20; // Intervalo de tempo para cada quadro (em ms, simulado)
            let currentTime = 0;

            const animateScroll = function() {
                currentTime += increment;
                const val = easeInOutQuad(currentTime, start, change, duration);
                element.scrollLeft = val;
                if (currentTime < duration) {
                    requestAnimationFrame(animateScroll);
                }
            };
            requestAnimationFrame(animateScroll);
        }

        // --- 3. Event Listeners (Cliques e Scroll) ---

        // Evento para o botão Direito
        btnRight.addEventListener("click", () => {
            smoothScroll(carrossel, carrossel.scrollLeft + cardWidth, 300);
        });

        // Evento para o botão Esquerdo
        btnLeft.addEventListener("click", () => {
            smoothScroll(carrossel, carrossel.scrollLeft - cardWidth, 300);
        });

        // Ajusta a posição do scroll quando ele atinge os limites (clones)
        carrossel.addEventListener("scroll", () => {
            // Se rolou até o final dos cards reais (e entrou nos clones finais)
            if (carrossel.scrollLeft >= cardWidth * (cards.length * 2)) {
                // Volta para o início dos cards reais instantaneamente
                carrossel.scrollLeft = cardWidth * cards.length;
            }
            // Se rolou até os clones iniciais (passou do início)
            if (carrossel.scrollLeft <= 0) {
                // Volta para o último conjunto de cards reais instantaneamente
                carrossel.scrollLeft = cardWidth * cards.length;
            }
        });

    } 
    // Em telas <= 600px, o JS é ignorado e o CSS (scroll-snap) assume o controle.
});