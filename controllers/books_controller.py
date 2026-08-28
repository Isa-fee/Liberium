from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from datetime import date
from random import choice
import os
from uuid import uuid4
from werkzeug.utils import secure_filename

from utils.gamificacao import adicionar_xp, adicionar_libelulas
from utils.insignias import verificar_insignias
from utils.atividades import registrar_atividade
from utils.google_books import (buscar_google_books, buscar_livro_google)

from models import (
    Livro,
    Estante,
    DecoracaoEstante,
    SolicitacaoLivro,
    Atividade,
    Clube
)
from extensions import db

EXTENSOES_CAPA = {"png", "jpg", "jpeg", "webp"}


def extensao_permitida(nome_arquivo):

    return (
        "." in nome_arquivo
        and nome_arquivo.rsplit(".", 1)[1].lower()
        in EXTENSOES_CAPA
    )

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

    # ==================================
    # ITEM DO USUÁRIO NA ESTANTE
    # ==================================

    item_estante = Estante.query.filter_by(
        usuario_id=current_user.id,
        livro_id=id
    ).first()

    # ==================================
    # RESENHAS DO LIVRO
    # ==================================

    resenhas = Estante.query.filter(
        Estante.livro_id == id,
        Estante.nota.isnot(None),
        Estante.resenha.isnot(None),
        Estante.resenha != ""
    ).order_by(
        Estante.data_resenha.desc()
    ).all()

    # ==================================
    # MÉDIA DAS AVALIAÇÕES
    # ==================================

    notas = [
        item.nota
        for item in resenhas
        if item.nota is not None
    ]

    if notas:

        media_avaliacoes = round(
            sum(notas) / len(notas),
            1
        )

    else:

        media_avaliacoes = None

    return render_template(
        "books/books.html",
        livro=livro,
        item_estante=item_estante,
        resenhas=resenhas,
        media_avaliacoes=media_avaliacoes,
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
# SOLICITAR CADASTRO DE LIVRO
# ======================================

@books_bp.route(
    "/solicitar",
    methods=["GET", "POST"]
)
@login_required
def solicitar_livro():

    if request.method == "POST":

        titulo = request.form.get(
            "titulo",
            ""
        ).strip()

        autor = request.form.get(
            "autor",
            ""
        ).strip()

        descricao = request.form.get(
            "descricao",
            ""
        ).strip()

        arquivo_capa = request.files.get("capa")

        capa = None

        if arquivo_capa and arquivo_capa.filename:

            if not extensao_permitida(arquivo_capa.filename):

                flash(
                    "Formato de capa inválido. Use JPG, JPEG, PNG ou WEBP.",
                    "warning"
                )

                return redirect(
                    url_for("books_bp.solicitar_livro")
                )

            nome_original = secure_filename(
                arquivo_capa.filename
            )

            extensao = nome_original.rsplit(
                ".",
                1
            )[1].lower()

            nome_arquivo = (
                f"{uuid4().hex}.{extensao}"
            )

            pasta = os.path.join(
                "static",
                "img",
                "capas",
                "solicitacoes"
            )

            os.makedirs(
                pasta,
                exist_ok=True
            )

            caminho_completo = os.path.join(
                pasta,
                nome_arquivo
            )

            arquivo_capa.save(
                caminho_completo
            )

            capa = (
                f"img/capas/solicitacoes/{nome_arquivo}"
            )

        genero = request.form.get(
            "genero",
            ""
        ).strip()

        editora = request.form.get(
            "editora",
            ""
        ).strip()

        paginas = request.form.get(
            "paginas",
            type=int
        )

        ano = request.form.get(
            "ano",
            ""
        ).strip()

        idioma = request.form.get(
            "idioma",
            ""
        ).strip()

        isbn = request.form.get(
            "isbn",
            ""
        ).strip()

        # ==================================
        # CAMPOS OBRIGATÓRIOS
        # ==================================

        if not titulo or not autor:

            flash(
                "Informe pelo menos o título e o autor do livro.",
                "warning"
            )

            return redirect(
                url_for(
                    "books_bp.solicitar_livro",
                    titulo=titulo
                )
            )

        # ==================================
        # VERIFICAR SE JÁ EXISTE
        # ==================================

        livro_existente = Livro.query.filter(
            db.func.lower(Livro.titulo)
            == titulo.lower()
        ).first()

        if livro_existente:

            flash(
                "Esse livro já está cadastrado no Liberium.",
                "warning"
            )

            return redirect(
                url_for(
                    "books_bp.ver",
                    id=livro_existente.id
                )
            )

        # ==================================
        # EVITAR SOLICITAÇÃO REPETIDA
        # ==================================

        solicitacao_existente = (
            SolicitacaoLivro.query.filter(
                SolicitacaoLivro.solicitante_id
                == current_user.id,

                db.func.lower(
                    SolicitacaoLivro.titulo
                )
                == titulo.lower(),

                SolicitacaoLivro.status
                == "pendente"
            ).first()
        )

        if solicitacao_existente:

            flash(
                "Você já possui uma solicitação pendente para esse livro.",
                "warning"
            )

            return redirect(
                url_for("books_bp.catalogo")
            )

        # ==================================
        # CRIAR SOLICITAÇÃO
        # ==================================

        solicitacao = SolicitacaoLivro(
            titulo=titulo,
            autor=autor,
            descricao=descricao or None,
            capa=capa or None,
            genero=genero or None,
            editora=editora or None,
            paginas=paginas,
            ano=ano or None,
            idioma=idioma or None,
            isbn=isbn or None,
            solicitante_id=current_user.id,
            status="pendente"
        )

        db.session.add(
            solicitacao
        )

        db.session.commit()

        flash(
            "Solicitação enviada! "
            "Um administrador irá analisar o cadastro do livro.",
            "success"
        )

        return redirect(
            url_for("books_bp.catalogo")
        )

    # ==================================
    # GET
    # ==================================

    titulo = request.args.get(
        "titulo",
        ""
    )

    return render_template(
        "books/solicitar_livro.html",
        titulo=titulo
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
        url_for("estante_bp.estante")
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
# ======================================
# PAINEL - SOLICITAÇÕES DE LIVROS
# ======================================

@books_bp.route("/admin/solicitacoes")
@login_required
def solicitacoes_admin():

    # ==================================
    # SOMENTE ADMINISTRADORES
    # ==================================

    if current_user.tipo != "administrador":

        flash(
            "Você não possui permissão para acessar essa página.",
            "danger"
        )

        return redirect(
            url_for("home.home")
        )

    # ==================================
    # BUSCAR SOLICITAÇÕES
    # ==================================

    solicitacoes = SolicitacaoLivro.query.order_by(
        SolicitacaoLivro.data_solicitacao.desc()
    ).all()

    # ==================================
    # LIVROS APROVADOS
    #
    # Guarda o livro atual correspondente
    # a cada solicitação aprovada.
    #
    # Assim, se o administrador alterar
    # a capa depois, a tela de solicitações
    # mostra a capa atualizada.
    # ==================================

    livros_aprovados = {}

    for solicitacao in solicitacoes:

        if solicitacao.status == "aprovado":

            livro = Livro.query.filter(
                db.func.lower(Livro.titulo)
                == solicitacao.titulo.lower()
            ).first()

            if livro:

                livros_aprovados[
                    solicitacao.id
                ] = livro

    # ==================================
    # TEMPLATE
    # ==================================

    return render_template(
        "books/solicitacoes_admin.html",
        solicitacoes=solicitacoes,
        livros_aprovados=livros_aprovados
    )
# ======================================
# APROVAR SOLICITAÇÃO
# ======================================

@books_bp.route(
    "/admin/solicitacoes/<int:solicitacao_id>/aprovar",
    methods=["POST"]
)
@login_required
def aprovar_solicitacao(solicitacao_id):

    # SOMENTE ADMINISTRADORES
    if current_user.tipo != "administrador":

        flash(
            "Você não possui permissão para realizar essa ação.",
            "danger"
        )

        return redirect(
            url_for("home.home")
        )

    solicitacao = SolicitacaoLivro.query.get_or_404(
        solicitacao_id
    )

    # Não processar duas vezes
    if solicitacao.status != "pendente":

        flash(
            "Essa solicitação já foi analisada.",
            "warning"
        )

        return redirect(
            url_for("books_bp.solicitacoes_admin")
        )
    # ==================================
    # VERIFICAR SE LIVRO JÁ EXISTE
    # ==================================

    livro_existente = Livro.query.filter(
        db.func.lower(Livro.titulo)
        == solicitacao.titulo.lower()
    ).first()

    if livro_existente:

        solicitacao.status = "aprovado"

        db.session.commit()

        flash(
            "O livro já estava cadastrado. "
            "A solicitação foi marcada como aprovada.",
            "warning"
        )

        return redirect(
            url_for("books_bp.solicitacoes_admin")
        )
    # ==================================
    # CRIAR LIVRO
    # ==================================

    novo_livro = Livro(
        titulo=solicitacao.titulo,
        autor=solicitacao.autor,
        descricao=solicitacao.descricao,
        capa=solicitacao.capa,
        genero=solicitacao.genero,
        editora=solicitacao.editora,
        paginas=solicitacao.paginas,
        ano=solicitacao.ano,
        idioma=solicitacao.idioma,

        avaliacao=None,
        destaque=False,
        google_id=None,
        origem="solicitacao"
    )

    db.session.add(
        novo_livro
    )
    solicitacao.status = "aprovado"
    db.session.commit()
    flash(
        f'"{solicitacao.titulo}" foi aprovado e adicionado ao catálogo!',
        "success"
    )
    return redirect(
        url_for("books_bp.solicitacoes_admin")
    )
# ======================================
# RECUSAR SOLICITAÇÃO
# ======================================

@books_bp.route(
    "/admin/solicitacoes/<int:solicitacao_id>/recusar",
    methods=["POST"]
)
@login_required
def recusar_solicitacao(solicitacao_id):

    # SOMENTE ADMINISTRADORES
    if current_user.tipo != "administrador":

        flash(
            "Você não possui permissão para realizar essa ação.",
            "danger"
        )

        return redirect(
            url_for("home.home")
        )

    solicitacao = SolicitacaoLivro.query.get_or_404(
        solicitacao_id
    )

    if solicitacao.status != "pendente":

        flash(
            "Essa solicitação já foi analisada.",
            "warning"
        )

        return redirect(
            url_for("books_bp.solicitacoes_admin")
        )

    solicitacao.status = "recusado"

    db.session.commit()

    flash(
        f'A solicitação de "{solicitacao.titulo}" foi recusada.',
        "success"
    )

    return redirect(
        url_for("books_bp.solicitacoes_admin")
    )
# ======================================
# ADMIN - EDITAR LIVRO
# ======================================

@books_bp.route(
    "/admin/livros/<int:livro_id>/editar",
    methods=["GET", "POST"]
)
@login_required
def editar_livro_admin(livro_id):

    # ==================================
    # SOMENTE ADMINISTRADORES
    # ==================================

    if current_user.tipo != "administrador":

        flash(
            "Você não possui permissão para realizar essa ação.",
            "danger"
        )

        return redirect(
            url_for("home.home")
        )

    livro = Livro.query.get_or_404(
        livro_id
    )

    # ==================================
    # SALVAR ALTERAÇÕES
    # ==================================

    if request.method == "POST":

        titulo = request.form.get(
            "titulo",
            ""
        ).strip()

        autor = request.form.get(
            "autor",
            ""
        ).strip()

        descricao = request.form.get(
            "descricao",
            ""
        ).strip()

        arquivo_capa = request.files.get("capa")

        genero = request.form.get(
            "genero",
            ""
        ).strip()

        editora = request.form.get(
            "editora",
            ""
        ).strip()

        paginas = request.form.get(
            "paginas",
            type=int
        )

        ano = request.form.get(
            "ano",
            ""
        ).strip()

        idioma = request.form.get(
            "idioma",
            ""
        ).strip()

        # ==================================
        # VALIDAÇÃO
        # ==================================

        if not titulo or not autor:

            flash(
                "Título e autor são obrigatórios.",
                "warning"
            )

            return redirect(
                url_for(
                    "books_bp.editar_livro_admin",
                    livro_id=livro.id
                )
            )

        # ==================================
        # ATUALIZAR LIVRO
        # ==================================

        livro.titulo = titulo
        livro.autor = autor
        livro.descricao = descricao or None

        # ==================================
        # ALTERAR CAPA
        # ==================================

        if arquivo_capa and arquivo_capa.filename:

            if not extensao_permitida(arquivo_capa.filename):

                flash(
                    "Formato de capa inválido. Use JPG, JPEG, PNG ou WEBP.",
                    "warning"
                )

                return redirect(
                    url_for(
                        "books_bp.editar_livro_admin",
                        livro_id=livro.id
                    )
                )

            nome_original = secure_filename(
                arquivo_capa.filename
            )

            extensao = nome_original.rsplit(
                ".",
                1
            )[1].lower()

            nome_arquivo = (
                f"{uuid4().hex}.{extensao}"
            )

            pasta = os.path.join(
                "static",
                "img",
                "capas",
                "solicitacoes"
            )

            os.makedirs(
                pasta,
                exist_ok=True
            )

            caminho_completo = os.path.join(
                pasta,
                nome_arquivo
            )

            arquivo_capa.save(
                caminho_completo
            )

            livro.capa = (
                f"img/capas/solicitacoes/{nome_arquivo}"
            )

        livro.genero = genero or None
        livro.editora = editora or None
        livro.paginas = paginas
        livro.ano = ano or None
        livro.idioma = idioma or None

        db.session.commit()

        flash(
            f'"{livro.titulo}" foi atualizado com sucesso!',
            "success"
        )

        return redirect(
            url_for(
                "books_bp.ver",
                id=livro.id
            )
        )

    # ==================================
    # EXIBIR FORMULÁRIO
    # ==================================

    return render_template(
        "books/editar_livro_admin.html",
        livro=livro
    )

# ======================================
# ADMIN - EXCLUIR LIVRO
# ======================================
@books_bp.route(
    "/admin/livros/<int:livro_id>/excluir",
    methods=["POST"]
)
@login_required
def excluir_livro_admin(livro_id):
    # ==================================
    # SOMENTE ADMINISTRADORES
    # ==================================
    if current_user.tipo != "administrador":
        flash(
            "Você não possui permissão para realizar essa ação.",
            "danger"
        )
        return redirect(
            url_for("home.home")
        )
    livro = Livro.query.get_or_404(
        livro_id
    )
    titulo_livro = livro.titulo
    # ==================================
    # ATUALIZAR SOLICITAÇÃO ORIGINAL
    # ==================================

    solicitacao = SolicitacaoLivro.query.filter(
        db.func.lower(SolicitacaoLivro.titulo)
        == livro.titulo.lower(),

        SolicitacaoLivro.status
        == "aprovado"
    ).first()

    if solicitacao:
        solicitacao.status = "excluido"
    # ==================================
    # REMOVER DAS ESTANTES
    # ==================================
    Estante.query.filter_by(
        livro_id=livro.id
    ).delete(
        synchronize_session=False
    )
    # ==================================
    # REMOVER ATIVIDADES RELACIONADAS
    # ==================================
    Atividade.query.filter_by(
        livro_id=livro.id
    ).delete(
        synchronize_session=False
    )
    # ==================================
    # REMOVER LIVRO DOS CLUBES
    # ==================================
    # O clube continua existindo.
    # Apenas fica sem leitura atual.
    clubes = Clube.query.filter_by(
        livro_id=livro.id
    ).all()
    for clube in clubes:
        clube.livro_id = None
    # ==================================
    # EXCLUIR O LIVRO
    # ==================================
    db.session.delete(
        livro
    )
    db.session.commit()
    flash(
        f'"{titulo_livro}" foi excluído do catálogo.',
        "success"
    )
    return redirect(
        url_for("books_bp.catalogo")
    )