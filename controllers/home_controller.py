from flask import Blueprint, render_template
from flask_login import login_required, current_user
from models import Livro, Estante
from collections import Counter

home_bp = Blueprint(
    'home',
    __name__,
    template_folder='../templates'
)


@home_bp.route('/')
def index():
    return render_template('home/index.html')


@home_bp.route('/home')
@login_required
def home():
    livros = Livro.query.filter_by(
        destaque=True
    ).limit(8).all()

    itens_estante = Estante.query.filter_by(
        usuario_id=current_user.id
    ).all()

    itens_lidos = [
        item
        for item in itens_estante
        if item.status == "lido"
    ]

    itens_lendo = [
        item
        for item in itens_estante
        if item.status == "lendo"
    ]

    itens_quero_ler = [
        item
        for item in itens_estante
        if item.status == "quero ler"
    ]

    total_lidos = len(itens_lidos)
    total_lendo = len(itens_lendo)
    total_quero_ler = len(itens_quero_ler)
    total_estante = len(itens_estante)

    generos_lidos = []

    for item in itens_lidos:

        if item.livro and item.livro.genero:
            generos_lidos.append(
                item.livro.genero
            )


    contagem_generos = Counter(
        generos_lidos
    )


    generos_labels = list(
        contagem_generos.keys()
    )

    generos_valores = list(
        contagem_generos.values()
    )

    return render_template(
        "home/home.html",
        livros=livros,

        total_lidos=total_lidos,
        total_lendo=total_lendo,
        total_quero_ler=total_quero_ler,
        total_estante=total_estante,

        generos_labels=generos_labels,
        generos_valores=generos_valores
    )
    

@home_bp.route("/sobre")
def sobre():
    return render_template("home/sobre.html")

@home_bp.route("/contato")
def contato():
    return render_template("home/contato.html")