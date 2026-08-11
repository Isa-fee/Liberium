from flask import flash
from datetime import date
import calendar

from extensions import db
from models import MetaLeitura, Estante


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
    
def atualizar_meta_leitura(usuario):

    hoje = date.today()

    meta = MetaLeitura.query.filter_by(
        usuario_id=usuario.id,
        mes=hoje.month,
        ano=hoje.year
    ).order_by(
        MetaLeitura.id.desc()
    ).first()

    if not meta:
        return None

    primeiro_dia = meta.data_inicio

    ultimo_dia = date(
        hoje.year,
        hoje.month,
        calendar.monthrange(
            hoje.year,
            hoje.month
        )[1]
    )

    livros_lidos = Estante.query.filter(
        Estante.usuario_id == usuario.id,
        Estante.status == "lido",
        Estante.data_leitura >= primeiro_dia,
        Estante.data_leitura <= ultimo_dia
    ).count()

    meta.progresso = livros_lidos

    if livros_lidos >= meta.quantidade:

        meta.progresso = meta.quantidade
        meta.concluida = True

        if not meta.recompensa_recebida:

            meta.recompensa_recebida = True

            adicionar_xp(
                usuario,
                300,
                "cumprir sua meta de leitura"
            )

            adicionar_libelulas(
                usuario,
                10,
                "cumprir sua meta de leitura"
            )

            flash(
                "🎯 Parabéns! Você cumpriu sua meta de leitura!",
                "success"
            )

    else:

        meta.concluida = False

    return meta