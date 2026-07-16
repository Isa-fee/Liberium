from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required

from models import Livro


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

    return render_template(
        "books/books.html",
        livro=livro
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
# ESTANTE
# ======================================

@books_bp.route("/estante")
@login_required
def estante():

    return render_template(
        "books/estante.html"
    )