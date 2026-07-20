from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from datetime import date

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
        item_estante=item_estante
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
# ADCIONAR LIVRO
# ======================================

@books_bp.route("/adicionar-estante/<int:livro_id>", methods=["POST"])
@login_required
def adicionar_estante(livro_id):

    status = request.form.get("status")

    existe = Estante.query.filter_by(
        usuario_id=current_user.id,
        livro_id=livro_id
    ).first()

    livro = Livro.query.get_or_404(livro_id)

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

    else:

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
        mensagem = "Livro adicionado à estante!"

    db.session.commit()

    flash(mensagem, "success")

    return redirect(
        url_for("books_bp.ver", id=livro_id)
    )


@books_bp.route("/progresso/<int:id>", methods=["POST"])
@login_required
def atualizar_progresso(id):

    item = Estante.query.filter_by(
        usuario_id=current_user.id,
        livro_id=id
    ).first_or_404()

    pagina = int(request.form["pagina"])

    if pagina < 0:
        pagina = 0

    if pagina > item.livro.paginas:
        pagina = item.livro.paginas

    item.pagina_atual = pagina

    item.progresso = round(
        (pagina / item.livro.paginas) * 100
    )

    if item.progresso == 0:
        item.status = "quero ler"

    elif item.progresso < 100:
        item.status = "lendo"

    else:
        item.status = "lido"
        if item.data_leitura is None:
            item.data_leitura = date.today()

    db.session.commit()

    flash("Progresso atualizado!", "success")

    return redirect(url_for("books_bp.ver", id=id))


@books_bp.route("/avaliar/<int:id>", methods=["POST"])
@login_required
def avaliar(id):

    item = Estante.query.filter_by(
        usuario_id=current_user.id,
        livro_id=id
    ).first_or_404()

    nota = int(request.form["nota"])

    if nota < 1 or nota > 5:
        flash("A nota deve ser entre 1 e 5.", "danger")
        return redirect(url_for("books_bp.ver", id=id))

    item.nota = nota
    item.resenha = request.form.get("resenha", "").strip()

    db.session.commit()

    flash("Avaliação salva!", "success")

    return redirect(url_for("books_bp.ver", id=id))




@books_bp.route("/remover-estante/<int:livro_id>", methods=["POST"])
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

    return redirect(url_for("books_bp.estante"))