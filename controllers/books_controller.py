from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from extensions import db
from models import Livro
import requests

books_bp = Blueprint("books_bp", __name__, url_prefix="/books")


# 📚 LISTAR LIVROS DO BANCO
@books_bp.route("/")
def listar():
    livros = Livro.query.all()
    return render_template("books/listar.html", livros=livros)


# ➕ ADICIONAR LIVRO MANUALMENTE
@books_bp.route("/add", methods=["GET", "POST"])
def add():
    if "usuario_id" not in session:
        flash("Faça login para adicionar livros!", "danger")
        return redirect(url_for("user_bp.login"))

    if request.method == "POST":
        titulo = request.form.get("titulo")
        autor = request.form.get("autor")
        descricao = request.form.get("descricao")
        usuario_id = session["usuario_id"]

        novo = Livro(
            titulo=titulo,
            autor=autor,
            descricao=descricao,
            usuario_id=usuario_id
        )

        db.session.add(novo)
        db.session.commit()

        flash("Livro adicionado com sucesso!", "success")
        return redirect(url_for("books_bp.listar"))

    return render_template("books/add.html")


# 🔎 VER LIVRO DO BANCO (SEU)
@books_bp.route("/<int:id>")
def ver(id):
    livro = Livro.query.get_or_404(id)
    return render_template("books/ver.html", livro=livro)


# ❌ DELETAR LIVRO
@books_bp.route("/delete/<int:id>")
def delete(id):
    livro = Livro.query.get_or_404(id)
    
    if livro.usuario_id != session.get("usuario_id"):
        flash("Você não tem permissão para excluir este livro.", "danger")
        return redirect(url_for("books_bp.listar"))

    db.session.delete(livro)
    db.session.commit()

    flash("Livro excluído!", "success")
    return redirect(url_for("books_bp.listar"))


# 🌐 BUSCAR LIVROS NA API
@books_bp.route("/buscar")
def buscar():
    termo = request.args.get("q")

    if not termo:
        flash("Digite algo para buscar!", "warning")
        return redirect(url_for("books_bp.listar"))

    url = f"https://openlibrary.org/search.json?q={termo}"
    resposta = requests.get(url)

    dados = resposta.json()
    livros_api = dados.get("docs", [])[:10]

    return render_template("books/resultados.html", livros=livros_api)


# 📖 DETALHES DO LIVRO (API)
@books_bp.route("/detalhes/<path:obra_id>")
def detalhes(obra_id):
    # 🔹 Busca dados principais do livro
    url = f"https://openlibrary.org/{obra_id}.json"
    resposta = requests.get(url)
    dados = resposta.json()

    titulo = dados.get("title", "Sem título")

    # 📄 descrição
    descricao = dados.get("description", "Sem descrição disponível")
    if isinstance(descricao, dict):
        descricao = descricao.get("value", "")

    # ✍️ autor
    autor = "Autor desconhecido"
    try:
        if "authors" in dados:
            author_key = dados["authors"][0]["author"]["key"]
            author_data = requests.get(f"https://openlibrary.org{author_key}.json").json()
            autor = author_data.get("name", autor)
    except:
        pass

    # 🖼️ capa
    capa = ""
    if "covers" in dados:
        capa = f"https://covers.openlibrary.org/b/id/{dados['covers'][0]}-L.jpg"

    return render_template(
        "books/books.html",  # 👈 usa sua página bonita
        titulo=titulo,
        descricao=descricao,
        autor=autor,
        capa=capa
    )