from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from datetime import date

from utils.gamificacao import adicionar_xp, adicionar_libelulas
from utils.insignias import verificar_insignias
from utils.atividades import registrar_atividade

from models import Livro, Estante, DecoracaoEstante
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

        status_anterior = existe.status

        # Se mudou de prateleira,
        # coloca o livro no final da nova prateleira
        if status_anterior != status:

            # Define o nome da prateleira
            nova_prateleira = status

            # Pega a maior posição entre os livros
            ultimo_livro = Estante.query.filter_by(
                usuario_id=current_user.id,
                status=nova_prateleira
            ).order_by(
                Estante.posicao.desc()
            ).first()

            # Pega a maior posição entre as decorações
            ultima_decoracao = DecoracaoEstante.query.filter_by(
                usuario_id=current_user.id,
                prateleira=nova_prateleira
            ).order_by(
                DecoracaoEstante.posicao.desc()
            ).first()

            maior_posicao = -1

            if ultimo_livro:
                maior_posicao = max(
                    maior_posicao,
                    ultimo_livro.posicao
                )

            if ultima_decoracao:
                maior_posicao = max(
                    maior_posicao,
                    ultima_decoracao.posicao
                )

            existe.posicao = maior_posicao + 1

        existe.status = status

        # ==================================
        # STATUS LIDO
        # ==================================

        if status == "lido":

            existe.progresso = 100
            existe.pagina_atual = existe.livro.paginas
            existe.data_leitura = date.today()

        # ==================================
        # STATUS QUERO LER
        # ==================================

        elif status == "quero ler":

            existe.progresso = 0
            existe.pagina_atual = 0
            existe.data_leitura = None

        # ==================================
        # STATUS LENDO
        # ==================================

        elif status == "lendo":

            # Se estava em outra prateleira e agora começou a ler,
            # mantém o progresso atual.
            if existe.progresso == 100:
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

        # ==================================
        # CALCULAR PRÓXIMA POSIÇÃO
        # ==================================

        ultimo_livro = Estante.query.filter_by(
            usuario_id=current_user.id,
            status=status
        ).order_by(
            Estante.posicao.desc()
        ).first()

        ultima_decoracao = DecoracaoEstante.query.filter_by(
            usuario_id=current_user.id,
            prateleira=status
        ).order_by(
            DecoracaoEstante.posicao.desc()
        ).first()

        maior_posicao = -1

        if ultimo_livro:
            maior_posicao = max(
                maior_posicao,
                ultimo_livro.posicao
            )

        if ultima_decoracao:
            maior_posicao = max(
                maior_posicao,
                ultima_decoracao.posicao
            )

        proxima_posicao = maior_posicao + 1

        # ==================================
        # CRIAR LIVRO
        # ==================================

        novo = Estante(
            usuario_id=current_user.id,
            livro_id=livro_id,
            status=status,

            progresso=100 if status == "lido" else 0,

            pagina_atual=(
                livro.paginas
                if status == "lido"
                else 0
            ),

            data_leitura=(
                date.today()
                if status == "lido"
                else None
            ),

            nota=None,
            resenha="",

            # posição dentro da prateleira
            posicao=proxima_posicao
        )

        db.session.add(novo)

        # ==================================
        # ATIVIDADE
        # ==================================

        registrar_atividade(
            current_user,
            "adicionar",
            f'Você adicionou "{livro.titulo}" à sua estante.',
            livro
        )

        # ==================================
        # XP POR ADICIONAR LIVRO
        # ==================================

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

        # ==================================
        # SE JÁ ADICIONOU COMO LIDO
        # ==================================

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

        # ==================================
        # BÔNUS PELO PRIMEIRO LIVRO
        # ==================================

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

    # ==================================
    # SALVAR
    # ==================================

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


# ======================================
# CATÁLOGO DE LIVROS
# ======================================

@books_bp.route("/")
@login_required
def catalogo():

    busca = request.args.get("q", "").strip()
    genero = request.args.get("genero", "").strip()
    idioma = request.args.get("idioma", "").strip()
    ano = request.args.get("ano", "").strip()
    avaliacao = request.args.get("avaliacao", "").strip()
    ordenar = request.args.get("ordenar", "recentes")

    # --------------------------------------
    # BUSCA BASE
    # --------------------------------------

    consulta = Livro.query

    # --------------------------------------
    # BUSCA POR TÍTULO OU AUTOR
    # --------------------------------------

    if busca:

        consulta = consulta.filter(
            db.or_(
                Livro.titulo.ilike(f"%{busca}%"),
                Livro.autor.ilike(f"%{busca}%")
            )
        )

    # --------------------------------------
    # FILTRO DE GÊNERO
    # --------------------------------------

    if genero:

        consulta = consulta.filter(
            Livro.genero == genero
        )

    # --------------------------------------
    # FILTRO DE IDIOMA
    # --------------------------------------

    if idioma:

        consulta = consulta.filter(
            Livro.idioma == idioma
        )

    # --------------------------------------
    # FILTRO DE ANO
    # --------------------------------------

    if ano:

        consulta = consulta.filter(
            Livro.ano == ano
        )

    # --------------------------------------
    # FILTRO DE AVALIAÇÃO
    # --------------------------------------

    if avaliacao:

        try:
            nota_minima = float(avaliacao)

            consulta = consulta.filter(
                Livro.avaliacao >= nota_minima
            )

        except ValueError:
            pass

    # --------------------------------------
    # ORDENAÇÃO
    # --------------------------------------

    if ordenar == "avaliacao":

        consulta = consulta.order_by(
            Livro.avaliacao.desc()
        )

    elif ordenar == "az":

        consulta = consulta.order_by(
            Livro.titulo.asc()
        )

    elif ordenar == "za":

        consulta = consulta.order_by(
            Livro.titulo.desc()
        )

    elif ordenar == "antigos":

        consulta = consulta.order_by(
            Livro.ano.asc()
        )

    else:

        # Mais recentes
        consulta = consulta.order_by(
            Livro.ano.desc()
        )

    livros = consulta.all()

    # --------------------------------------
    # OPÇÕES DOS FILTROS
    # --------------------------------------

    generos = db.session.query(
        Livro.genero
    ).filter(
        Livro.genero.isnot(None),
        Livro.genero != ""
    ).distinct().order_by(
        Livro.genero
    ).all()

    idiomas = db.session.query(
        Livro.idioma
    ).filter(
        Livro.idioma.isnot(None),
        Livro.idioma != ""
    ).distinct().order_by(
        Livro.idioma
    ).all()

    anos = db.session.query(
        Livro.ano
    ).filter(
        Livro.ano.isnot(None),
        Livro.ano != ""
    ).distinct().order_by(
        Livro.ano.desc()
    ).all()

    # --------------------------------------
    # LIVROS QUE JÁ ESTÃO NA ESTANTE
    # --------------------------------------

    livros_na_estante = {
        item.livro_id
        for item in Estante.query.filter_by(
            usuario_id=current_user.id
        ).all()
    }

    return render_template(
        "books/catalogo.html",
        livros=livros,
        generos=[g[0] for g in generos],
        idiomas=[i[0] for i in idiomas],
        anos=[a[0] for a in anos],
        livros_na_estante=livros_na_estante,
        busca=busca,
        genero=genero,
        idioma=idioma,
        ano=ano,
        avaliacao=avaliacao,
        ordenar=ordenar
    )