from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from datetime import date
from random import choice

from utils.gamificacao import adicionar_xp, adicionar_libelulas
from utils.insignias import verificar_insignias
from utils.atividades import registrar_atividade
from utils.google_books import (buscar_google_books, buscar_livro_google)

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
        hoje=date.today(),
        origem="banco"
    )


# ======================================
# DETALHES DO LIVRO DO GOOGLE
# ======================================

@books_bp.route("/google/<string:google_id>")
@login_required
def ver_google(google_id):

    livro = buscar_livro_google(
        google_id
    )

    if not livro:

        flash(
            "Não foi possível carregar esse livro.",
            "warning"
        )

        return redirect(
            url_for("books_bp.catalogo")
        )

    return render_template(
        "books/books.html",
        livro=livro,
        item_estante=None,
        hoje=date.today(),
        origem="google"
    )
# ======================================
# ADICIONAR LIVRO DO GOOGLE À ESTANTE
# ======================================

@books_bp.route(
    "/google/<string:google_id>/adicionar_estante",
    methods=["POST"]
)
@login_required
def adicionar_google_estante(google_id):

    status = request.form.get("status")

    if status not in [
        "quero ler",
        "lendo",
        "lido"
    ]:

        flash(
            "Status inválido.",
            "warning"
        )

        return redirect(
            url_for(
                "books_bp.ver_google",
                google_id=google_id
            )
        )

    # ==================================
    # JÁ EXISTE NO BANCO?
    # ==================================

    livro = Livro.query.filter_by(
        google_id=google_id
    ).first()

    # ==================================
    # SE NÃO EXISTE, BUSCAR NA API
    # ==================================

    if not livro:

        dados = buscar_livro_google(
            google_id
        )

        if not dados:

            flash(
                "Não foi possível salvar esse livro.",
                "warning"
            )

            return redirect(
                url_for("books_bp.catalogo")
            )

        livro = Livro(
            titulo=dados.get("titulo"),
            autor=dados.get("autor"),
            descricao=dados.get("descricao"),
            capa=dados.get("capa"),
            genero=dados.get("genero"),
            editora=dados.get("editora"),
            paginas=dados.get("paginas"),
            ano=dados.get("ano"),
            idioma=dados.get("idioma"),
            avaliacao=dados.get("avaliacao"),
            google_id=google_id,
            origem="google"
        )

        db.session.add(livro)

        db.session.commit()

    # ==================================
    # ADICIONAR NA ESTANTE
    # ==================================

    return adicionar_estante(
        livro.id
    )

    
# ======================================
# PÁGINA DO AUTOR
# ======================================

@books_bp.route("/autor/<path:nome>")
@login_required
def autor(nome):

    livros = Livro.query.filter(
        Livro.autor == nome
    ).order_by(
        Livro.titulo.asc()
    ).all()

    if not livros:

        flash(
            "Autor não encontrado.",
            "warning"
        )

        return redirect(
            url_for("books_bp.catalogo")
        )

    return render_template(
        "autor/autor.html",
        autor=nome,
        livros=livros,
        quantidade=len(livros)
    )

# ======================================
# BUSCA DE LIVROS
# ======================================

# ======================================
# BUSCA DE LIVROS
# ======================================

@books_bp.route("/buscar")
@login_required
def buscar():

    termo = request.args.get(
        "q",
        ""
    ).strip()

    # ==================================
    # BUSCA VAZIA
    # ==================================

    if not termo:

        flash(
            "Digite algo para buscar!",
            "warning"
        )

        return redirect(
            url_for("home.home")
        )

    # ==================================
    # 1. BUSCAR NO BANCO LOCAL
    # ==================================

    livros_banco = Livro.query.filter(
        db.or_(
            Livro.titulo.ilike(
                f"%{termo}%"
            ),
            Livro.autor.ilike(
                f"%{termo}%"
            )
        )
    ).all()

    # ==================================
    # 2. ENCONTROU NO NOSSO BANCO
    # ==================================

    if livros_banco:

        return render_template(
            "books/resultados.html",
            livros=livros_banco,
            termo=termo,
            origem="banco"
        )

    # ==================================
    # 3. NÃO ENCONTROU:
    # BUSCAR NO GOOGLE BOOKS
    # ==================================

    livros_google = buscar_google_books(
        termo
    )

    return render_template(
        "books/resultados.html",
        livros=livros_google,
        termo=termo,
        origem="google"
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

    # ======================================
    # PARÂMETROS
    # ======================================

    busca = request.args.get(
        "q",
        ""
    ).strip()

    genero = request.args.get(
        "genero",
        ""
    ).strip()

    idioma = request.args.get(
        "idioma",
        ""
    ).strip()

    ano = request.args.get(
        "ano",
        ""
    ).strip()

    avaliacao = request.args.get(
        "avaliacao",
        ""
    ).strip()

    ordenar = request.args.get(
        "ordenar",
        "recentes"
    )

    pagina = request.args.get(
        "pagina",
        1,
        type=int
    )

    if pagina < 1:
        pagina = 1

    por_pagina = 12


    # ======================================
    # LIVROS DO BANCO
    # ======================================

    consulta = Livro.query


    # ======================================
    # BUSCA
    # ======================================

    if busca:

        consulta = consulta.filter(

            db.or_(

                Livro.titulo.ilike(
                    f"%{busca}%"
                ),

                Livro.autor.ilike(
                    f"%{busca}%"
                )
            )
        )


    # ======================================
    # FILTRO GÊNERO
    # ======================================

    if genero:

        consulta = consulta.filter(
            Livro.genero.ilike(
                f"%{genero}%"
            )
        )


    # ======================================
    # FILTRO IDIOMA
    # ======================================

    if idioma:

        consulta = consulta.filter(
            Livro.idioma == idioma
        )


    # ======================================
    # FILTRO ANO
    # ======================================

    if ano:

        consulta = consulta.filter(
            Livro.ano.ilike(
                f"{ano}%"
            )
        )


    # ======================================
    # FILTRO AVALIAÇÃO
    # ======================================

    if avaliacao:

        try:

            nota_minima = float(
                avaliacao
            )

            consulta = consulta.filter(
                Livro.avaliacao >= nota_minima
            )

        except ValueError:

            pass


    # ======================================
    # ORDENAÇÃO BANCO
    # ======================================

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

        consulta = consulta.order_by(
            Livro.ano.desc()
        )


    # ======================================
    # PEGAR LIVROS DO BANCO
    # ======================================

    if pagina == 1:

        livros_banco = consulta.limit(
            por_pagina
        ).all()

    else:

        livros_banco = []

    # ======================================
    # TRANSFORMAR EM DICIONÁRIO
    # ======================================

    livros = []

    for livro in livros_banco:

        livros.append({

            "id": livro.id,

            "google_id": livro.google_id,

            "titulo": livro.titulo,

            "autor": livro.autor,

            "descricao": livro.descricao,

            "capa": livro.capa,

            "genero": livro.genero,

            "editora": livro.editora,

            "paginas": livro.paginas,

            "ano": livro.ano,

            "idioma": livro.idioma,

            "avaliacao": livro.avaliacao,

            "origem": "banco"
        })


    # ======================================
    # TERMO PARA GOOGLE
    # ======================================

    if busca:

        termo_google = busca

    elif genero:

        termo_google = (
            f"subject:{genero}"
        )

    else:

        termo_google = "subject:fiction"


    # ======================================
    # GOOGLE BOOKS
    # ======================================

    inicio_google = (
        (pagina - 1)
        * por_pagina
    )

    livros_google = buscar_google_books(
        termo_google,
        start_index=inicio_google,
        max_results=por_pagina,
        idioma=(
            idioma
            if idioma
            else None
        )
    )

        # ======================================
        # FILTRAR GOOGLE POR GÊNERO
        # ======================================

    if genero:
        livros_google = [
            livro
            for livro in livros_google
                if (
                    livro.get("genero")
                    and genero.lower()
                    in livro.get(
                        "genero",
                        ""
                    ).lower()
                )
            ]


    # ======================================
    # FILTRAR GOOGLE POR ANO
    # ======================================

    if ano:

        livros_google = [

            livro

            for livro in livros_google

            if str(
                livro.get(
                    "ano",
                    ""
                )
            ).startswith(
                ano
            )
        ]


    # ======================================
    # FILTRAR GOOGLE POR AVALIAÇÃO
    # ======================================

    if avaliacao:

        try:

            nota_minima = float(
                avaliacao
            )

            livros_google = [

                livro

                for livro in livros_google

                if (
                    livro.get(
                        "avaliacao"
                    ) is not None
                    and livro.get(
                        "avaliacao"
                    ) >= nota_minima
                )
            ]

        except ValueError:

            pass


    # ======================================
    # IDS GOOGLE QUE JÁ ESTÃO NO BANCO
    # ======================================

    google_ids_salvos = {

        livro.google_id

        for livro in Livro.query.filter(
            Livro.google_id.isnot(None)
        ).all()

        if livro.google_id
    }


    # ======================================
    # ADICIONAR GOOGLE AO CATÁLOGO
    # ======================================

    for livro_google in livros_google:

        google_id = livro_google.get(
            "google_id"
        )

        # Se o mesmo volume já existe no
        # banco, não mostramos duas vezes
        if (
            google_id
            not in google_ids_salvos
        ):

            livros.append(
                livro_google
            )


    # ======================================
    # ORDENAÇÃO FINAL
    # ======================================

    if ordenar == "az":

        livros.sort(
            key=lambda livro:
            (
                livro.get(
                    "titulo"
                )
                or ""
            ).lower()
        )


    elif ordenar == "za":

        livros.sort(
            key=lambda livro:
            (
                livro.get(
                    "titulo"
                )
                or ""
            ).lower(),
            reverse=True
        )


    elif ordenar == "avaliacao":

        livros.sort(
            key=lambda livro:
            livro.get(
                "avaliacao"
            )
            or 0,
            reverse=True
        )


    elif ordenar == "antigos":

        livros.sort(
            key=lambda livro:
            str(
                livro.get(
                    "ano"
                )
                or "9999"
            )
        )


    else:

        livros.sort(
            key=lambda livro:
            str(
                livro.get(
                    "ano"
                )
                or ""
            ),
            reverse=True
        )


    # ======================================
    # LIVROS NA ESTANTE DO USUÁRIO
    # ======================================

    livros_na_estante = {

        item.livro_id

        for item in Estante.query.filter_by(
            usuario_id=current_user.id
        ).all()
    }


    # ======================================
    # SURPREENDA-ME
    # ======================================

    if request.args.get(
        "surpreenda"
    ):

        livros_disponiveis = []

        for livro in livros:

            if livro["origem"] == "google":

                livros_disponiveis.append(
                    livro
                )

            elif (
                livro["id"]
                not in livros_na_estante
            ):

                livros_disponiveis.append(
                    livro
                )


        if livros_disponiveis:

            livro_sorteado = choice(
                livros_disponiveis
            )


            # GOOGLE

            if (
                livro_sorteado[
                    "origem"
                ]
                == "google"
            ):

                return redirect(
                    url_for(
                        "books_bp.ver_google",

                        google_id=(
                            livro_sorteado[
                                "google_id"
                            ]
                        )
                    )
                )


            # BANCO

            return redirect(
                url_for(
                    "books_bp.ver",

                    id=livro_sorteado[
                        "id"
                    ]
                )
            )


    # ======================================
    # GÊNEROS
    # ======================================

    generos = [

        "Ficção",
        "Fantasia",
        "Romance",
        "Mistério",
        "Suspense",
        "Terror",
        "Aventura",
        "História",
        "Biografia",
        "Ciência",
        "Tecnologia"
    ]


    # ======================================
    # IDIOMAS
    # ======================================

    idiomas = [
        "pt",
        "en",
        "es",
        "fr"
    ]


    # ======================================
    # ANOS
    #
    # Mantém compatibilidade com seu
    # catalogo.html atual.
    # ======================================

    anos = [

        item[0]

        for item in db.session.query(
            Livro.ano
        ).filter(
            Livro.ano.isnot(None)
        ).distinct().all()

        if item[0]
    ]

    anos.sort(
        reverse=True
    )


    # ======================================
    # EXISTEM MAIS RESULTADOS?
    # ======================================

    tem_mais = (
        len(livros_google)
        == por_pagina
    )


    # ======================================
    # TEMPLATE
    # ======================================

    return render_template(

        "books/catalogo.html",

        livros=livros,

        generos=generos,

        idiomas=idiomas,

        anos=anos,

        livros_na_estante=(
            livros_na_estante
        ),

        busca=busca,

        genero=genero,

        idioma=idioma,

        ano=ano,

        avaliacao=avaliacao,

        ordenar=ordenar,

        pagina=pagina,

        tem_mais=tem_mais
    )