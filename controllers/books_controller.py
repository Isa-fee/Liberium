from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from datetime import date

from utils.gamificacao import adicionar_xp, adicionar_libelulas
from utils.insignias import verificar_insignias

from models import Livro, Estante
from extensions import db


books_bp = Blueprint(
    "books_bp",
    __name__,
    url_prefix="/books"
)


# ======================================
# DETALHES DO LIVRO
# ======================================

@books_bp.route("/<int:id>")
@login_required
def ver(id):

    livro = Livro.query.get_or_404(id)

    item_estante = Estante.query.filter_by(
        usuario_id=current_user.id,
        livro_id=id
    ).first()

    return render_template(
        "books/books.html",
        livro=livro,
        item_estante=item_estante,
        hoje=date.today()
    )


# ======================================
# BUSCA DE LIVROS
# ======================================

@books_bp.route("/buscar")
@login_required
def buscar():

    termo = request.args.get("q", "").strip()

    if not termo:

        flash(
            "Digite algo para buscar!",
            "warning"
        )

        return redirect(
            url_for("home.home")
        )

    livros = Livro.query.filter(
        Livro.titulo.ilike(f"%{termo}%")
    ).all()

    return render_template(
        "books/resultados.html",
        livros=livros
    )


# ======================================
# ADICIONAR LIVRO À ESTANTE
# ======================================

@books_bp.route(
    "/adicionar_estante/<int:livro_id>",
    methods=["POST"]
)
@login_required
def adicionar_estante(livro_id):

    status = request.form.get("status")

    livro = Livro.query.get_or_404(livro_id)

    existe = Estante.query.filter_by(
        usuario_id=current_user.id,
        livro_id=livro_id
    ).first()

    # ==================================
    # LIVRO JÁ ESTÁ NA ESTANTE
    # ==================================

    if existe:

        existe.status = status

        if status == "lido":

            existe.progresso = 100
            existe.pagina_atual = existe.livro.paginas
            existe.data_leitura = date.today()

        elif status == "quero ler":

            existe.progresso = 0
            existe.pagina_atual = 0
            existe.data_leitura = None

        mensagem = "Status atualizado!"

    # ==================================
    # LIVRO NOVO
    # ==================================

    else:

        total = Estante.query.filter_by(
            usuario_id=current_user.id
        ).count()

        novo = Estante(
            usuario_id=current_user.id,
            livro_id=livro_id,
            status=status,
            progresso=100 if status == "lido" else 0,
            pagina_atual=livro.paginas if status == "lido" else 0,
            data_leitura=date.today() if status == "lido" else None,
            nota=None,
            resenha=""
        )

        db.session.add(novo)

        # XP por adicionar qualquer livro
        adicionar_xp(
            current_user,
            5,
            "adicionar um livro à estante"
        )

        adicionar_libelulas(
            current_user,
            1,
            "adicionar um livro à estante"
        )

        # Se já adicionou como lido
        if status == "lido":

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

        # Bônus pelo primeiro livro
        if total == 0:

            adicionar_xp(
                current_user,
                20,
                "adicionar seu primeiro livro"
            )

            adicionar_libelulas(
                current_user,
                5,
                "adicionar seu primeiro livro"
            )

        mensagem = "Livro adicionado à estante!"

    db.session.commit()

    verificar_insignias(current_user)

    flash(
        mensagem,
        "success"
    )

    return redirect(
        url_for(
            "books_bp.ver",
            id=livro_id
        )
    )