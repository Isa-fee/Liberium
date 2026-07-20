from flask import flash

NIVEIS = [
    (0, "Leitor Iniciante"),
    (250, "Leitor Curioso"),
    (500, "Explorador Literário"),
    (1000, "Devorador de Livros"),
    (1500, "Mestre da Biblioteca"),
    (2500, "Lenda Literária")
]


def atualizar_nivel(usuario):

    nivel_antigo = usuario.nivel

    for xp_minimo, nome in reversed(NIVEIS):

        if usuario.xp >= xp_minimo:
            usuario.nivel = nome
            break

    if nivel_antigo != usuario.nivel:

        flash(
            f"Parabéns! Você alcançou o nível '{usuario.nivel}'!",
            "success"
        )


def adicionar_xp(usuario, quantidade, motivo):

    usuario.xp += quantidade

    flash(
        f"Você ganhou +{quantidade} XP por {motivo}.",
        "success"
    )

    atualizar_nivel(usuario)


def adicionar_libelulas(usuario, quantidade, motivo):

    usuario.libelulas += quantidade

    flash(
        f"Você ganhou +{quantidade} libélulas por {motivo}.",
        "success"
    )