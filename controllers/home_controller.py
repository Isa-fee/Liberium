from flask import Blueprint, render_template
from flask_login import login_required, current_user
from models import Livro, Estante
from collections import Counter

from sqlalchemy import case

home_bp = Blueprint(
    'home',
    __name__,
    template_folder='../templates'
)

def buscar_sugestoes(usuario_id, limite=12):

    # ==========================================
    # ESTANTE DO USUÁRIO
    # ==========================================

    itens_estante = Estante.query.filter_by(
        usuario_id=usuario_id
    ).all()

    livros_na_estante = {
        item.livro_id
        for item in itens_estante
    }


    # ==========================================
    # PREFERÊNCIAS DO USUÁRIO
    # ==========================================

    pontuacao_generos = Counter()
    pontuacao_autores = Counter()

    pesos_status = {
        "lido": 3,
        "lendo": 2,
        "quero ler": 1
    }


    for item in itens_estante:

        if not item.livro:
            continue

        livro = item.livro

        peso = pesos_status.get(
            item.status,
            0
        )

        if peso == 0:
            continue


        # ------------------------------
        # GÊNERO
        # ------------------------------

        if livro.genero:

            pontuacao_generos[
                livro.genero.strip()
            ] += peso


        # ------------------------------
        # AUTOR
        # ------------------------------

        if livro.autor:

            # Autor influencia um pouco menos
            # que o gênero.

            pontuacao_autores[
                livro.autor.strip()
            ] += peso


    # ==========================================
    # LIVROS CANDIDATOS
    # ==========================================

    consulta = Livro.query

    if livros_na_estante:

        consulta = consulta.filter(
            ~Livro.id.in_(
                livros_na_estante
            )
        )


    candidatos = consulta.all()


    # ==========================================
    # CALCULAR PONTUAÇÃO
    # ==========================================

    livros_pontuados = []


    for livro in candidatos:

        pontos = 0


        # ------------------------------
        # GÊNERO
        # ------------------------------

        if livro.genero:

            genero = livro.genero.strip()

            pontos += (
                pontuacao_generos.get(
                    genero,
                    0
                ) * 4
            )


        # ------------------------------
        # AUTOR
        # ------------------------------

        if livro.autor:

            autor = livro.autor.strip()

            pontos += (
                pontuacao_autores.get(
                    autor,
                    0
                ) * 2
            )


        # ------------------------------
        # AVALIAÇÃO GERAL
        # ------------------------------

        if livro.avaliacao:

            if livro.avaliacao >= 4.5:
                pontos += 3

            elif livro.avaliacao >= 4:
                pontos += 2

            elif livro.avaliacao >= 3.5:
                pontos += 1


        livros_pontuados.append(
            (
                livro,
                pontos
            )
        )


    # ==========================================
    # ORDENAR POR RELEVÂNCIA
    # ==========================================

    livros_pontuados.sort(
        key=lambda item: (
            item[1],
            item[0].avaliacao or 0
        ),
        reverse=True
    )


    # ==========================================
    # DIVERSIDADE DAS SUGESTÕES
    # ==========================================

    sugestoes = []

    quantidade_genero = Counter()
    quantidade_autor = Counter()


    # Primeiro tentamos montar uma seleção
    # diversificada.

    for livro, pontos in livros_pontuados:

        genero = (
            livro.genero.strip()
            if livro.genero
            else None
        )

        autor = (
            livro.autor.strip()
            if livro.autor
            else None
        )


        # Evita dominar o carrossel com
        # um único gênero.

        if (
            genero
            and quantidade_genero[genero] >= 4
        ):
            continue


        # Evita muitos livros seguidos
        # do mesmo autor.

        if (
            autor
            and quantidade_autor[autor] >= 2
        ):
            continue


        sugestoes.append(livro)


        if genero:
            quantidade_genero[genero] += 1

        if autor:
            quantidade_autor[autor] += 1


        if len(sugestoes) == limite:
            break


    # ==========================================
    # COMPLETAR SE FALTARAM LIVROS
    # ==========================================

    if len(sugestoes) < limite:

        ids_sugeridos = {
            livro.id
            for livro in sugestoes
        }


        for livro, pontos in livros_pontuados:

            if livro.id in ids_sugeridos:
                continue

            sugestoes.append(livro)

            ids_sugeridos.add(
                livro.id
            )


            if len(sugestoes) == limite:
                break


    return sugestoes

@home_bp.route('/')
def index():
    return render_template('home/index.html')


@home_bp.route('/home')
@login_required
def home():
    livros = buscar_sugestoes(
    current_user.id,
    limite=12
    )

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