from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from datetime import date

from utils.gamificacao import adicionar_xp, adicionar_libelulas
from utils.insignias import verificar_insignias

from models import Estante
from extensions import db


estante_bp = Blueprint(
    "estante_bp",
    __name__,
    url_prefix="/books"
)


# ======================================
# VISUALIZAR ESTANTE
# ======================================

@estante_bp.route("/estante")
@login_required
def estante():

    lendo = Estante.query.filter_by(
        usuario_id=current_user.id,
        status="lendo"
    ).all()

    lidos = Estante.query.filter_by(
        usuario_id=current_user.id,
        status="lido"
    ).all()

    quero_ler = Estante.query.filter_by(
        usuario_id=current_user.id,
        status="quero ler"
    ).all()

    return render_template(
        "books/estante.html",
        lendo=lendo,
        lidos=lidos,
        quero_ler=quero_ler
    )


# ======================================
# ATUALIZAR PROGRESSO
# ======================================

@estante_bp.route(
    "/progresso/<int:id>",
    methods=["POST"]
)
@login_required
def atualizar_progresso(id):

    item = Estante.query.filter_by(
        usuario_id=current_user.id,
        livro_id=id
    ).first_or_404()

    pagina = int(
        request.form["pagina"]
    )

    if pagina < 0:
        pagina = 0

    if pagina > item.livro.paginas:
        pagina = item.livro.paginas

    # Guarda o status anterior
    status_anterior = item.status

    item.pagina_atual = pagina

    item.progresso = round(
        (pagina / item.livro.paginas) * 100
    )

    # ==================================
    # AINDA NÃO COMEÇOU
    # ==================================

    if item.progresso == 0:

        item.status = "quero ler"

    # ==================================
    # COMEÇOU A LER
    # ==================================

    elif item.progresso < 100:

        item.status = "lendo"

        # Aqui depois entraremos com:
        #
        # 📖 Você começou a ler "Livro"
        #
        # somente quando realmente mudar
        # de "quero ler" para "lendo".

        if status_anterior == "quero ler":

            pass

    # ==================================
    # CONCLUIU
    # ==================================

    else:

        if item.status != "lido":

            adicionar_xp(
                current_user,
                100,
                "concluir um livro"
            )

            adicionar_libelulas(
                current_user,
                10,
                "concluir um livro"
            )

        item.status = "lido"

        if item.data_leitura is None:

            item.data_leitura = date.today()

    db.session.commit()

    verificar_insignias(current_user)

    flash(
        "Progresso atualizado!",
        "success"
    )

    return redirect(
        url_for(
            "books_bp.ver",
            id=id
        )
    )


# ======================================
# AVALIAR LIVRO / ESCREVER RESENHA
# ======================================

@estante_bp.route(
    "/avaliar/<int:id>",
    methods=["POST"]
)
@login_required
def avaliar(id):

    item = Estante.query.filter_by(
        usuario_id=current_user.id,
        livro_id=id
    ).first_or_404()

    nota = int(
        request.form["nota"]
    )

    if nota < 1 or nota > 5:

        flash(
            "A nota deve ser entre 1 e 5.",
            "danger"
        )

        return redirect(
            url_for(
                "books_bp.ver",
                id=id
            )
        )

    data_leitura = request.form.get(
        "data_leitura"
    )

    if data_leitura:

        data_leitura = date.fromisoformat(
            data_leitura
        )

    # ==================================
    # PRIMEIRA AVALIAÇÃO
    # ==================================

    if item.nota is None:

        adicionar_xp(
            current_user,
            15,
            "avaliar um livro"
        )

        adicionar_libelulas(
            current_user,
            2,
            "avaliar um livro"
        )

    # ==================================
    # PRIMEIRA RESENHA
    # ==================================

    resenha_nova = request.form.get(
        "resenha",
        ""
    ).strip()

    if (
        item.resenha == ""
        and resenha_nova
    ):

        adicionar_xp(
            current_user,
            50,
            "escrever uma resenha"
        )

        adicionar_libelulas(
            current_user,
            5,
            "escrever uma resenha"
        )

    item.nota = nota
    item.resenha = resenha_nova
    item.data_leitura = data_leitura

    db.session.commit()

    verificar_insignias(current_user)

    flash(
        "Avaliação salva!",
        "success"
    )

    return redirect(
        url_for(
            "books_bp.ver",
            id=id
        )
    )


# ======================================
# REMOVER DA ESTANTE
# ======================================

@estante_bp.route(
    "/remover-estante/<int:livro_id>",
    methods=["POST"]
)
@login_required
def remover_estante(livro_id):

    item = Estante.query.filter_by(
        usuario_id=current_user.id,
        livro_id=livro_id
    ).first_or_404()

    db.session.delete(item)

    db.session.commit()

    flash(
        "Livro removido da estante!",
        "success"
    )

    return redirect(
        url_for(
            "estante_bp.estante"
        )
    )