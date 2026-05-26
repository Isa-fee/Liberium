from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required

from extensions import db
from models import Livro

import requests
import os

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

    termo = request.args.get("q")

    if not termo:

        flash(
            "Digite algo para buscar!",
            "warning"
        )

        return redirect(
            url_for("home.home")
        )

    # ======================================
    # 1 - PROCURA NO BANCO
    # ======================================

    livros = Livro.query.filter(
        Livro.titulo.ilike(f"%{termo}%")
    ).all()

    # encontrou no banco
    if livros:

        return render_template(
            "books/resultados.html",
            livros=livros
        )

    # ======================================
    # 2 - PROCURA NA API
    # ======================================

    try:

        api_key = os.getenv(
            "GOOGLE_BOOKS_API_KEY"
        )

        url = (
            f"https://www.googleapis.com/books/v1/volumes"
            f"?q={termo}"
            f"&key={api_key}"
            f"&maxResults=10"
        )

        resposta = requests.get(url).json()

        for item in resposta.get(
            "items",
            []
        ):

            info = item.get(
                "volumeInfo",
                {}
            )

            google_id = item.get("id")

            # evita duplicação
            existente = Livro.query.filter_by(
                google_id=google_id
            ).first()

            if existente:
                continue

            capa = None

            if info.get("imageLinks"):

                capa = info[
                    "imageLinks"
                ].get(
                    "thumbnail"
                )

            isbn = None

            for identificador in info.get(
                "industryIdentifiers",
                []
            ):

                if identificador.get(
                    "type"
                ) == "ISBN_13":

                    isbn = identificador.get(
                        "identifier"
                    )

                    break

            novo_livro = Livro(

                google_id=google_id,

                isbn=isbn,

                titulo=info.get(
                    "title",
                    "Título desconhecido"
                ),

                autor=", ".join(
                    info.get(
                        "authors",
                        ["Autor desconhecido"]
                    )
                ),

                descricao=info.get(
                    "description",
                    ""
                ),

                capa=capa,

                genero="",

                editora=info.get(
                    "publisher",
                    ""
                ),

                paginas=info.get(
                    "pageCount"
                ),

                ano=info.get(
                    "publishedDate",
                    ""
                ),

                idioma=info.get(
                    "language",
                    ""
                ),

                avaliacao=info.get(
                    "averageRating",
                    0
                ),

                origem="google",

                destaque=False
            )

            db.session.add(
                novo_livro
            )

        db.session.commit()

    except Exception as erro:

        print(
            f"Erro ao consultar Google Books: {erro}"
        )

    # ======================================
    # 3 - BUSCA NOVAMENTE NO BANCO
    # ======================================

    livros = Livro.query.filter(
        Livro.titulo.ilike(f"%{termo}%")
    ).all()

    return render_template(
        "books/resultados.html",
        livros=livros
    )