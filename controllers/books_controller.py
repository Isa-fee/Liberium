from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required

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

    termo = request.args.get("q", "").strip()

    if not termo:

        flash(
            "Digite algo para buscar!",
            "warning"
        )

        return redirect(
            url_for("home.home")
        )

    # ======================================
    # 1 - BUSCA NO BANCO
    # ======================================

    todos = Livro.query.all()

    livros = []

    for livro in todos:

        if termo.lower() in livro.titulo.lower():

            livros.append(livro)

    print("ENCONTRADOS NO BANCO:", len(livros))

    # já começa os resultados com os livros do banco
    resultados = livros.copy()

    # ======================================
    # 2 - BUSCA NA API
    # ======================================

    try:

        api_key = os.getenv(
            "GOOGLE_BOOKS_API_KEY"
        )

        if api_key:

            url = (
                "https://www.googleapis.com/books/v1/volumes"
                f"?q={termo}"
                f"&key={api_key}"
                "&maxResults=10"
            )

            resposta = requests.get(url).json()

            titulos_existentes = {
                livro.titulo.lower()
                for livro in livros
            }

            for item in resposta.get(
                "items",
                []
            ):

                info = item.get(
                    "volumeInfo",
                    {}
                )

                titulo = info.get(
                    "title",
                    "Título desconhecido"
                )

                # evita duplicados
                if titulo.lower() in titulos_existentes:
                    continue

                capa = None

                if info.get("imageLinks"):

                    capa = info[
                        "imageLinks"
                    ].get(
                        "thumbnail"
                    )

                resultados.append({

                    "id": item.get("id"),

                    "titulo": titulo,

                    "autor": ", ".join(
                        info.get(
                            "authors",
                            ["Autor desconhecido"]
                        )
                    ),

                    "descricao": info.get(
                        "description",
                        ""
                    ),

                    "capa": capa,

                    "editora": info.get(
                        "publisher",
                        ""
                    ),

                    "paginas": info.get(
                        "pageCount"
                    ),

                    "ano": info.get(
                        "publishedDate",
                        ""
                    ),

                    "idioma": info.get(
                        "language",
                        ""
                    ),

                    "avaliacao": info.get(
                        "averageRating",
                        0
                    ),

                    "origem": "google"
                })

    except Exception as erro:

        print(
            f"Erro ao consultar Google Books: {erro}"
        )

    print(
        "TOTAL RESULTADOS:",
        len(resultados)
    )

    return render_template(
        "books/resultados.html",
        livros=resultados
    )