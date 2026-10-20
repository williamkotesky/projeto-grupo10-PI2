
(() => {
    const home = document.querySelector(".home-page");

    if (!home) return;

    const diminuir = document.getElementById("diminuir-fonte");
    const restaurar = document.getElementById("restaurar-fonte");
    const aumentar = document.getElementById("aumentar-fonte");

    if (!diminuir || !restaurar || !aumentar) return;

    const chaveFonte = "oficina-mp-tamanho-fonte";
    const escalaPadrao = 1;
    const escalaMinima = 0.8;
    const escalaMaxima = 1.5;
    const passo = 0.1;

    let escala = escalaPadrao;

    try {
        const salva = Number(localStorage.getItem(chaveFonte));

        if (salva >= escalaMinima && salva <= escalaMaxima) {
            escala = salva;
        }
    } catch {
        // O controle continua funcionando sem localStorage.
    }

    function aplicarEscala() {
        home.style.setProperty("--escala-fonte", escala);
        home.classList.add("fonte-ajustada");

        try {
            localStorage.setItem(chaveFonte, String(escala));
        } catch {
            // A preferência não será persistida, mas a fonte será ajustada.
        }
    }

    diminuir.addEventListener("click", () => {
        escala = Math.max(
            escalaMinima,
            Math.round((escala - passo) * 10) / 10
        );
        aplicarEscala();
    });

    restaurar.addEventListener("click", () => {
        escala = escalaPadrao;
        aplicarEscala();
    });

    aumentar.addEventListener("click", () => {
        escala = Math.min(
            escalaMaxima,
            Math.round((escala + passo) * 10) / 10
        );
        aplicarEscala();
    });

    aplicarEscala();
})();
