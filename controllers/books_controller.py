from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from extensions import db
from models import Livro

books_bp = Blueprint("books_bp", __name__, url_prefix="/books")

@books_bp.route("/")
def listar():
    livros = Livro.query.all()
    return render_template("books/listar.html", livros=livros)
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

@books_bp.route("/<int:id>")
def ver(id):
    livro = Livro.query.get_or_404(id)
    return render_template("books/ver.html", livro=livro)

@books_bp.route("/delete/<int:id>")
def delete(id):
    livro = Livro.query.get_or_404(id)
    
    # Evitar apagar livros de outros usuários
    if livro.usuario_id != session.get("usuario_id"):
        flash("Você não tem permissão para excluir este livro.", "danger")
        return redirect(url_for("books_bp.listar"))

    db.session.delete(livro)
    db.session.commit()

    flash("Livro excluído!", "success")
    return redirect(url_for("books_bp.listar"))
