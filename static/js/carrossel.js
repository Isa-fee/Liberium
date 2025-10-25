document.addEventListener("DOMContentLoaded", () => {
    const carrossel = document.querySelector(".carrossel-cards");
    const btnLeft = document.querySelector(".carrossel-btn.left");
    const btnRight = document.querySelector(".carrossel-btn.right");

    const cards = Array.from(carrossel.querySelectorAll(".card"));
    const cardWidth = cards[0].offsetWidth + 16; // largura do card + gap

    // clonar cards para efeito infinito
    cards.forEach(card => {
        const cloneFirst = card.cloneNode(true);
        const cloneLast = card.cloneNode(true);
        carrossel.appendChild(cloneFirst);
        carrossel.insertBefore(cloneLast, carrossel.firstChild);
    });

    // posição inicial
    carrossel.scrollLeft = cardWidth * cards.length;

    btnRight.addEventListener("click", () => {
        smoothScroll(carrossel, carrossel.scrollLeft + cardWidth, 300);
    });

    btnLeft.addEventListener("click", () => {
        smoothScroll(carrossel, carrossel.scrollLeft - cardWidth, 300);
    });

    // quando o scroll terminar, ajustar para loop infinito
    carrossel.addEventListener("scroll", () => {
        if (carrossel.scrollLeft >= cardWidth * (cards.length * 2)) {
            carrossel.scrollLeft = cardWidth * cards.length;
        }
        if (carrossel.scrollLeft <= 0) {
            carrossel.scrollLeft = cardWidth * cards.length;
        }
    });

    // função de scroll suave
    function smoothScroll(element, target, duration) {
        const start = element.scrollLeft;
        const change = target - start;
        const increment = 20;
        let currentTime = 0;

        const animateScroll = function() {
            currentTime += increment;
            const val = easeInOutQuad(currentTime, start, change, duration);
            element.scrollLeft = val;
            if (currentTime < duration) {
                requestAnimationFrame(animateScroll);
            }
        };
        animateScroll();
    }

    // função de easing
    function easeInOutQuad(t, b, c, d) {
        t /= d/2;
        if (t < 1) return c/2*t*t + b;
        t--;
        return -c/2 * (t*(t-2) - 1) + b;
    }
});
