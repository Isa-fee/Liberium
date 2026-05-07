from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user

from extensions import db
from models import Livro

from deep_translator import GoogleTranslator
import requests
import os

books_bp = Blueprint("books_bp", __name__, url_prefix="/books")


@books_bp.route("/")
@login_required
def listar():

    livros = Livro.query.all()

    return render_template("books/listar.html", livros=livros)


@books_bp.route("/add", methods=["GET", "POST"])
@login_required
def add():

    if request.method == "POST":

        titulo = request.form.get("titulo")
        autor = request.form.get("autor")
        descricao = request.form.get("descricao")

        novo = Livro(
            titulo=titulo,
            autor=autor,
            descricao=descricao,
            usuario_id=current_user.id
        )

        db.session.add(novo)
        db.session.commit()

        flash("Livro adicionado com sucesso!", "success")

        return redirect(url_for("books_bp.listar"))

    return render_template("books/add.html")


@books_bp.route("/<int:id>")
@login_required
def ver(id):

    livro = Livro.query.get_or_404(id)

    return render_template("books/ver.html", livro=livro)


@books_bp.route("/delete/<int:id>")
@login_required
def delete(id):

    livro = Livro.query.get_or_404(id)

    if livro.usuario_id != current_user.id:

        flash("Você não tem permissão para excluir este livro.", "danger")

        return redirect(url_for("books_bp.listar"))

    db.session.delete(livro)
    db.session.commit()

    flash("Livro excluído!", "success")

    return redirect(url_for("books_bp.listar"))


@books_bp.route("/buscar")
@login_required
def buscar():

    termo = request.args.get("q")

    if not termo:

        flash("Digite algo para buscar!", "warning")

        return redirect(url_for("books_bp.listar"))

    livros = []

    # =========================
    # GOOGLE BOOKS
    # =========================

    try:

        api_key = os.getenv("GOOGLE_BOOKS_API_KEY")

        url_google = f"https://www.googleapis.com/books/v1/volumes?q={termo}&key={api_key}&maxResults=10"

        resp_google = requests.get(url_google).json()

        for item in resp_google.get("items", []):

            info = item.get("volumeInfo", {})

            capa = None

            if info.get("imageLinks"):
                capa = info["imageLinks"].get("thumbnail")

            livros.append({
                "titulo": info.get("title"),
                "autor": ", ".join(info.get("authors", ["Autor desconhecido"])),
                "capa": capa,
                "id": item.get("id"),
                "origem": "google",
                "descricao": ""
            })

    except:
        pass

    # =========================
    # OPEN LIBRARY
    # =========================

    try:

        url_open = f"https://openlibrary.org/search.json?q={termo}&limit=20"

        resp_open = requests.get(url_open).json()

        for item in resp_open.get("docs", []):

            if item.get("title") and item.get("author_name"):

                capa = None

                if item.get("cover_i"):
                    capa = f"https://covers.openlibrary.org/b/id/{item.get('cover_i')}-L.jpg"

                livros.append({
                    "titulo": item.get("title"),
                    "autor": item.get("author_name")[0],
                    "capa": capa,
                    "id": item.get("key"),
                    "origem": "open"
                })

    except:
        pass

    return render_template("books/resultados.html", livros=livros)


@books_bp.route("/detalhes/<origem>/<path:id>")
@login_required
def detalhes(origem, id):

    capa = request.args.get("capa")

    if origem == "google":

        api_key = os.getenv("GOOGLE_BOOKS_API_KEY")

        url = f"https://www.googleapis.com/books/v1/volumes/{id}?key={api_key}"

        dados = requests.get(url).json()

        info = dados.get("volumeInfo", {})

        descricao = info.get("description")

        if descricao and len(descricao) > 30:

            try:
                descricao = GoogleTranslator(source='auto', target='pt').translate(descricao)
            except:
                pass

        livro = {
            "titulo": info.get("title", "Título desconhecido"),

            "autor": ", ".join(
                info.get("authors", ["Autor desconhecido"])
            ),

            "descricao": descricao,

            "capa": info.get(
                "imageLinks",
                {}
            ).get("thumbnail"),

            "editora": info.get(
                "publisher",
                "Não informado"
            ),

            "paginas": info.get(
                "pageCount",
                "Não informado"
            ),

            "ano": info.get(
                "publishedDate",
                "Não informado"
            ),

            "avaliacao": info.get(
                "averageRating",
                "0.0"
            )
        }
    else:

        url = f"https://openlibrary.org/{id}.json"

        dados = requests.get(url).json()

        descricao = dados.get("description")

        if isinstance(descricao, dict):
            descricao = descricao.get("value")

        if descricao:

            try:
                descricao = GoogleTranslator(source='auto', target='pt').translate(descricao)
            except:
                pass

        livro = {
            "titulo": dados.get(
                "title",
                "Título desconhecido"
            ),

            "autor": "Autor desconhecido",

            "descricao": descricao,

            "capa": capa,

            "editora": "Não informado",

            "paginas": "Não informado",

            "ano": dados.get(
                "first_publish_date",
                "Não informado"
            ),

            "avaliacao": "0.0"
        }
    return render_template("books/books.html", livro=livro)