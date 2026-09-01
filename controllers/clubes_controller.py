import os

from flask import (
    Blueprint,
    redirect,
    render_template,
    request,
    url_for,
    jsonify,
    flash
)

from flask_login import (
    current_user,
    login_required
)

from werkzeug.utils import secure_filename

from utils.notificacoes import criar_notificacao
from utils.google_books import (
    buscar_google_books,
    buscar_livro_google
)

from extensions import db

from models import (
    Clube,
    Discussao,
    Livro,
    MembroClube,
    Amizade,
    Usuario,
    ConviteClube
)


clubes_bp = Blueprint(
    'clubes',
    __name__,
    url_prefix='/clubes'
)


# =========================================================
# LISTAR CLUBES
# =========================================================

@clubes_bp.route('/')
def listar_clubes():

    clubes = Clube.query.all()

    return render_template(
        'clubes/clubes.html',
        clubes=clubes
    )


# =========================================================
# PESQUISAR LIVROS PARA O CLUBE
# BANCO LOCAL + GOOGLE BOOKS
# =========================================================

@clubes_bp.route('/buscar-livros')
@login_required
def buscar_livros():

    termo = request.args.get(
        'q',
        ''
    ).strip()

    if not termo:
        return jsonify([])

    resultados = []

    # =====================================================
    # 1. BUSCAR NO BANCO LOCAL
    # =====================================================

    livros_banco = (
        Livro.query
        .filter(
            db.or_(
                Livro.titulo.ilike(
                    f'%{termo}%'
                ),
                Livro.autor.ilike(
                    f'%{termo}%'
                )
            )
        )
        .order_by(
            Livro.titulo.asc()
        )
        .limit(8)
        .all()
    )

    titulos_encontrados = set()

    for livro in livros_banco:

        titulo_normalizado = (
            livro.titulo or ''
        ).strip().lower()

        titulos_encontrados.add(
            titulo_normalizado
        )

        resultados.append({
            'id': livro.id,
            'google_id': None,
            'titulo': livro.titulo,
            'autor': livro.autor or 'Autor desconhecido',

            'capa': (
                url_for(
                    'static',
                    filename=livro.capa
                )
                if livro.capa
                else None
            ),

            'paginas': livro.paginas,
            'origem': 'banco'
        })

    # =====================================================
    # 2. COMPLEMENTAR COM GOOGLE BOOKS
    # =====================================================

    try:

        livros_google = buscar_google_books(
            termo
        )

        for livro in livros_google:

            if len(resultados) >= 16:
                break

            titulo = (
                livro.get('titulo')
                or ''
            ).strip()

            if not titulo:
                continue

            titulo_normalizado = titulo.lower()

            if titulo_normalizado in titulos_encontrados:
                continue

            google_id = (
                livro.get('google_id')
                or livro.get('id')
            )

            if not google_id:
                continue

            resultados.append({
                'id': None,
                'google_id': google_id,
                'titulo': titulo,
                'autor': (
                    livro.get('autor')
                    or 'Autor desconhecido'
                ),
                'capa': livro.get('capa'),
                'paginas': livro.get('paginas'),
                'origem': 'google'
            })

            titulos_encontrados.add(
                titulo_normalizado
            )

    except Exception as erro:

        print(
            'Erro ao consultar Google Books:',
            erro
        )

    return jsonify(
        resultados
    )


# =========================================================
# CRIAR CLUBE
# =========================================================

@clubes_bp.route(
    '/criar',
    methods=['GET', 'POST']
)
@login_required
def criar_clube():

    if request.method == 'POST':

        # =================================================
        # DADOS PRINCIPAIS
        # =================================================

        nome = request.form.get(
            'nome',
            ''
        ).strip()

        descricao = request.form.get(
            'descricao',
            ''
        ).strip()

        genero = request.form.get(
            'genero',
            ''
        ).strip()

        # =================================================
        # VALIDAÇÕES
        # =================================================

        if not nome:

            flash(
                'Digite um nome para o clube.',
                'erro'
            )

            return redirect(
                url_for(
                    'clubes.criar_clube'
                )
            )

        if not descricao:

            flash(
                'Escreva uma descrição para o clube.',
                'erro'
            )

            return redirect(
                url_for(
                    'clubes.criar_clube'
                )
            )

        if not genero:

            flash(
                'Selecione o gênero do clube.',
                'erro'
            )

            return redirect(
                url_for(
                    'clubes.criar_clube'
                )
            )

        # =================================================
        # PRIVACIDADE
        # =================================================

        privacidade = request.form.get(
            'privacidade',
            'publico'
        )

        privado = (
            privacidade == 'privado'
        )

        # =================================================
        # IMAGEM
        # =================================================

        arquivo_imagem = request.files.get(
            'imagem'
        )

        caminho_imagem = None

        if (
            arquivo_imagem
            and arquivo_imagem.filename
        ):

            nome_arquivo = secure_filename(
                arquivo_imagem.filename
            )

            pasta = os.path.join(
                'static',
                'img',
                'clubes'
            )

            os.makedirs(
                pasta,
                exist_ok=True
            )

            caminho_completo = os.path.join(
                pasta,
                nome_arquivo
            )

            arquivo_imagem.save(
                caminho_completo
            )

            caminho_imagem = os.path.join(
                'img',
                'clubes',
                nome_arquivo
            ).replace(
                '\\',
                '/'
            )

        # =================================================
        # CRIAR CLUBE
        # =================================================

        novo_clube = Clube(
            nome=nome,
            descricao=descricao,
            genero=genero,
            imagem=caminho_imagem,
            usuario_id=current_user.id,
            livro_id=None,
            quantidade_membros=1,
            privado=privado
        )

        db.session.add(
            novo_clube
        )

        db.session.flush()

        # =================================================
        # CRIADOR TAMBÉM É MEMBRO
        # =================================================

        membro_criador = MembroClube(
            clube_id=novo_clube.id,
            usuario_id=current_user.id,
            paginas_lidas=0,
            progresso_percentual=0,
            total_atualizacoes=0
        )

        db.session.add(
            membro_criador
        )

        db.session.commit()

        flash(
            'Clube criado com sucesso! Agora escolha a primeira leitura.',
            'sucesso'
        )

        return redirect(
            url_for(
                'clubes.gerenciar_clube',
                clube_id=novo_clube.id
            )
        )

    return render_template(
        'clubes/criar_clube.html'
    )


# =========================================================
# VER CLUBE
# =========================================================

@clubes_bp.route(
    '/<int:clube_id>'
)
@login_required
def ver_clube(clube_id):

    clube = Clube.query.get_or_404(
        clube_id
    )

    # =====================================================
    # IDENTIFICAR CRIADOR
    # =====================================================

    usuario_eh_criador = (
        clube.usuario_id == current_user.id
    )

    # =====================================================
    # MEMBROS
    # =====================================================

    membros = (
        MembroClube.query
        .filter_by(
            clube_id=clube.id
        )
        .all()
    )

    membros_ids = {
        membro.usuario_id
        for membro in membros
    }

    usuario_eh_membro = (
        current_user.id in membros_ids
    )

    # =====================================================
    # GARANTIR CRIADOR COMO MEMBRO
    # =====================================================

    if usuario_eh_criador and not usuario_eh_membro:

        membro_criador = MembroClube(
            clube_id=clube.id,
            usuario_id=current_user.id,
            paginas_lidas=0,
            progresso_percentual=0,
            total_atualizacoes=0
        )

        db.session.add(
            membro_criador
        )

        db.session.commit()

        membros = (
            MembroClube.query
            .filter_by(
                clube_id=clube.id
            )
            .all()
        )

        membros_ids = {
            membro.usuario_id
            for membro in membros
        }

        usuario_eh_membro = True

    # =====================================================
    # QUANTIDADE REAL DE MEMBROS
    # =====================================================

    quantidade_real = len(
        membros
    )

    if clube.quantidade_membros != quantidade_real:

        clube.quantidade_membros = (
            quantidade_real
        )

        db.session.commit()

    # =====================================================
    # PERMISSÃO PARA CONVIDAR
    # =====================================================

    if clube.privado:

        pode_convidar = (
            usuario_eh_criador
        )

    else:

        pode_convidar = (
            usuario_eh_membro
        )

    # =====================================================
    # AMIZADES ACEITAS
    # =====================================================

    amizades = (
        Amizade.query
        .filter(
            Amizade.status == 'aceita',
            db.or_(
                Amizade.usuario_id == current_user.id,
                Amizade.amigo_id == current_user.id
            )
        )
        .all()
    )

    amigos = []

    for amizade in amizades:

        if amizade.usuario_id == current_user.id:

            amigo = amizade.amigo

        else:

            amigo = amizade.usuario

        if amigo:

            amigos.append(
                amigo
            )

    amigos_disponiveis = [
        amigo
        for amigo in amigos
        if amigo.id not in membros_ids
    ]

    # =====================================================
    # DISCUSSÕES PRINCIPAIS
    #
    # Não pegamos respostas aqui.
    # As respostas serão acessadas através de
    # discussao.respostas no template.
    # =====================================================

    discussoes = (
        Discussao.query
        .filter_by(
            clube_id=clube.id,
            discussao_pai_id=None
        )
        .order_by(
            Discussao.data_criacao.desc()
        )
        .all()
    )

    return render_template(
        'clubes/clube.html',

        clube=clube,

        membros=membros,

        amigos=amigos_disponiveis,

        discussoes=discussoes,

        usuario_eh_criador=usuario_eh_criador,

        usuario_eh_membro=usuario_eh_membro,

        pode_convidar=pode_convidar
    )


# =========================================================
# GERENCIAR CLUBE
# =========================================================

@clubes_bp.route(
    '/<int:clube_id>/gerenciar'
)
@login_required
def gerenciar_clube(clube_id):

    clube = Clube.query.get_or_404(
        clube_id
    )

    if clube.usuario_id != current_user.id:

        flash(
            'Somente o criador pode gerenciar este clube.',
            'erro'
        )

        return redirect(
            url_for(
                'clubes.ver_clube',
                clube_id=clube.id
            )
        )

    membros = (
        MembroClube.query
        .filter_by(
            clube_id=clube.id
        )
        .order_by(
            MembroClube.data_entrada.asc()
        )
        .all()
    )

    return render_template(
        'clubes/gerenciar_clube.html',
        clube=clube,
        membros=membros
    )


# =========================================================
# DEFINIR LIVRO DO CLUBE
# =========================================================

@clubes_bp.route(
    '/<int:clube_id>/definir-livro',
    methods=['POST']
)
@login_required
def definir_livro(clube_id):

    clube = Clube.query.get_or_404(
        clube_id
    )

    if clube.usuario_id != current_user.id:

        flash(
            'Somente o criador pode escolher a leitura do clube.',
            'erro'
        )

        return redirect(
            url_for(
                'clubes.ver_clube',
                clube_id=clube.id
            )
        )

    origem = request.form.get(
        'origem',
        ''
    ).strip()

    livro = None

    # =====================================================
    # LIVRO LOCAL
    # =====================================================

    if origem == 'banco':

        livro_id = request.form.get(
            'livro_id'
        )

        if livro_id:

            try:

                livro = db.session.get(
                    Livro,
                    int(livro_id)
                )

            except (
                ValueError,
                TypeError
            ):

                livro = None

    # =====================================================
    # GOOGLE BOOKS
    # =====================================================

    elif origem == 'google':

        google_id = request.form.get(
            'google_id',
            ''
        ).strip()

        if google_id:

            livro = (
                Livro.query
                .filter_by(
                    google_id=google_id
                )
                .first()
            )

            if not livro:

                try:

                    dados_google = (
                        buscar_livro_google(
                            google_id
                        )
                    )

                except Exception as erro:

                    print(
                        'Erro ao buscar livro no Google Books:',
                        erro
                    )

                    dados_google = None

                if dados_google:

                    livro = Livro(
                        titulo=(
                            dados_google.get('titulo')
                            or 'Título desconhecido'
                        ),

                        autor=(
                            dados_google.get('autor')
                            or 'Autor desconhecido'
                        ),

                        descricao=(
                            dados_google.get('descricao')
                            or ''
                        ),

                        capa=dados_google.get(
                            'capa'
                        ),

                        genero=(
                            dados_google.get('genero')
                            or 'Outro'
                        ),

                        editora=dados_google.get(
                            'editora'
                        ),

                        paginas=dados_google.get(
                            'paginas'
                        ),

                        ano=dados_google.get(
                            'ano'
                        ),

                        idioma=dados_google.get(
                            'idioma'
                        ),

                        google_id=google_id,

                        origem='google'
                    )

                    db.session.add(
                        livro
                    )

                    db.session.flush()

    if not livro:

        flash(
            'Não foi possível selecionar esse livro.',
            'erro'
        )

        return redirect(
            url_for(
                'clubes.gerenciar_clube',
                clube_id=clube.id
            )
        )

    # =====================================================
    # DEFINIR LEITURA
    # =====================================================

    clube.livro_id = livro.id

    membros = (
        MembroClube.query
        .filter_by(
            clube_id=clube.id
        )
        .all()
    )

    for membro in membros:

        membro.paginas_lidas = 0
        membro.progresso_percentual = 0
        membro.total_atualizacoes = 0

    db.session.commit()

    flash(
        f'"{livro.titulo}" agora é a leitura do clube!',
        'sucesso'
    )

    return redirect(
        url_for(
            'clubes.gerenciar_clube',
            clube_id=clube.id
        )
    )


# =========================================================
# EDITAR CLUBE
# =========================================================

@clubes_bp.route(
    '/<int:clube_id>/editar',
    methods=['POST']
)
@login_required
def editar_clube(clube_id):

    clube = Clube.query.get_or_404(
        clube_id
    )

    if clube.usuario_id != current_user.id:

        flash(
            'Somente o criador pode editar este clube.',
            'erro'
        )

        return redirect(
            url_for(
                'clubes.ver_clube',
                clube_id=clube.id
            )
        )

    nome = request.form.get(
        'nome',
        ''
    ).strip()

    descricao = request.form.get(
        'descricao',
        ''
    ).strip()

    genero = request.form.get(
        'genero',
        ''
    ).strip()

    privacidade = request.form.get(
        'privacidade',
        'publico'
    )

    if not nome:

        flash(
            'O clube precisa ter um nome.',
            'erro'
        )

        return redirect(
            url_for(
                'clubes.gerenciar_clube',
                clube_id=clube.id
            )
        )

    clube.nome = nome
    clube.descricao = descricao
    clube.genero = genero

    clube.privado = (
        privacidade == 'privado'
    )

    arquivo_imagem = request.files.get(
        'imagem'
    )

    if (
        arquivo_imagem
        and arquivo_imagem.filename
    ):

        nome_arquivo = secure_filename(
            arquivo_imagem.filename
        )

        pasta = os.path.join(
            'static',
            'img',
            'clubes'
        )

        os.makedirs(
            pasta,
            exist_ok=True
        )

        caminho_completo = os.path.join(
            pasta,
            nome_arquivo
        )

        arquivo_imagem.save(
            caminho_completo
        )

        clube.imagem = os.path.join(
            'img',
            'clubes',
            nome_arquivo
        ).replace(
            '\\',
            '/'
        )

    db.session.commit()

    flash(
        'Clube atualizado com sucesso!',
        'sucesso'
    )

    return redirect(
        url_for(
            'clubes.ver_clube',
            clube_id=clube.id
        )
    )


# =========================================================
# REMOVER MEMBRO
# =========================================================

@clubes_bp.route(
    '/<int:clube_id>/remover-membro/<int:usuario_id>',
    methods=['POST']
)
@login_required
def remover_membro(clube_id, usuario_id):

    clube = Clube.query.get_or_404(
        clube_id
    )

    if clube.usuario_id != current_user.id:

        flash(
            'Somente o criador pode remover participantes.',
            'erro'
        )

        return redirect(
            url_for(
                'clubes.ver_clube',
                clube_id=clube.id
            )
        )

    if usuario_id == clube.usuario_id:

        flash(
            'O criador não pode ser removido do próprio clube.',
            'erro'
        )

        return redirect(
            url_for(
                'clubes.gerenciar_clube',
                clube_id=clube.id
            )
        )

    membro = (
        MembroClube.query
        .filter_by(
            clube_id=clube.id,
            usuario_id=usuario_id
        )
        .first()
    )

    if not membro:

        flash(
            'Este usuário não participa do clube.',
            'erro'
        )

        return redirect(
            url_for(
                'clubes.gerenciar_clube',
                clube_id=clube.id
            )
        )

    db.session.delete(
        membro
    )

    db.session.flush()

    clube.quantidade_membros = (
        MembroClube.query
        .filter_by(
            clube_id=clube.id
        )
        .count()
    )

    db.session.commit()

    flash(
        'Participante removido do clube.',
        'sucesso'
    )

    return redirect(
        url_for(
            'clubes.gerenciar_clube',
            clube_id=clube.id
        )
    )


# =========================================================
# CRIAR DISCUSSÃO
# =========================================================

@clubes_bp.route(
    '/<int:clube_id>/criar-discussao',
    methods=['POST']
)
@login_required
def criar_discussao(clube_id):

    clube = Clube.query.get_or_404(
        clube_id
    )

    # =====================================================
    # SOMENTE MEMBROS
    # =====================================================

    membro = (
        MembroClube.query
        .filter_by(
            clube_id=clube.id,
            usuario_id=current_user.id
        )
        .first()
    )

    if not membro:

        flash(
            'Você precisa participar do clube para comentar.',
            'erro'
        )

        return redirect(
            url_for(
                'clubes.ver_clube',
                clube_id=clube_id
            )
        )

    titulo = request.form.get(
        'titulo',
        ''
    ).strip()

    conteudo = request.form.get(
        'conteudo',
        ''
    ).strip()

    if not conteudo:

        flash(
            'Escreva um comentário antes de publicar.',
            'erro'
        )

        return redirect(
            url_for(
                'clubes.ver_clube',
                clube_id=clube_id
            )
        )

    nova_discussao = Discussao(
        titulo=titulo or None,
        conteudo=conteudo,
        clube_id=clube.id,
        usuario_id=current_user.id,

        # É uma discussão principal
        discussao_pai_id=None
    )

    db.session.add(
        nova_discussao
    )

    db.session.commit()

    # =====================================================
    # NOTIFICAR OUTROS MEMBROS
    # =====================================================

    membros = (
        MembroClube.query
        .filter(
            MembroClube.clube_id == clube.id,
            MembroClube.usuario_id != current_user.id
        )
        .all()
    )

    titulo_notificacao = (
        titulo
        if titulo
        else 'Novo comentário'
    )

    for membro_clube in membros:

        criar_notificacao(
            usuario_id=membro_clube.usuario_id,
            categoria="clubes",
            tipo="discussao",
            titulo="Nova discussão no clube",
            mensagem=(
                f'{current_user.nome} iniciou '
                f'"{titulo_notificacao}" '
                f'no clube {clube.nome}.'
            ),
            link=url_for(
                'clubes.ver_clube',
                clube_id=clube.id
            )
        )

    flash(
        'Comentário publicado!',
        'sucesso'
    )

    return redirect(
        url_for(
            'clubes.ver_clube',
            clube_id=clube_id
        )
    )


# =========================================================
# RESPONDER DISCUSSÃO
# =========================================================

@clubes_bp.route(
    '/<int:clube_id>/discussao/<int:discussao_id>/responder',
    methods=['POST']
)
@login_required
def responder_discussao(
    clube_id,
    discussao_id
):

    clube = Clube.query.get_or_404(
        clube_id
    )

    # =====================================================
    # SOMENTE MEMBROS PODEM RESPONDER
    # =====================================================

    membro = (
        MembroClube.query
        .filter_by(
            clube_id=clube.id,
            usuario_id=current_user.id
        )
        .first()
    )

    if not membro:

        flash(
            'Você precisa participar do clube para responder.',
            'erro'
        )

        return redirect(
            url_for(
                'clubes.ver_clube',
                clube_id=clube.id
            )
        )

    # =====================================================
    # BUSCAR DISCUSSÃO
    # =====================================================

    discussao_pai = (
        Discussao.query
        .filter_by(
            id=discussao_id,
            clube_id=clube.id
        )
        .first_or_404()
    )

    # =====================================================
    # CONTEÚDO DA RESPOSTA
    # =====================================================

    conteudo = request.form.get(
        'conteudo',
        ''
    ).strip()

    if not conteudo:

        flash(
            'Escreva uma resposta antes de enviar.',
            'erro'
        )

        return redirect(
            url_for(
                'clubes.ver_clube',
                clube_id=clube.id
            )
        )

    # =====================================================
    # SE TENTAR RESPONDER UMA RESPOSTA,
    # VINCULAMOS À DISCUSSÃO PRINCIPAL.
    #
    # Isso evita:
    #
    # comentário
    #   resposta
    #     resposta
    #       resposta...
    #
    # Todas ficam em um único nível visual.
    # =====================================================

    if discussao_pai.discussao_pai_id:

        id_discussao_principal = (
            discussao_pai.discussao_pai_id
        )

    else:

        id_discussao_principal = (
            discussao_pai.id
        )

    nova_resposta = Discussao(
        titulo=None,
        conteudo=conteudo,
        clube_id=clube.id,
        usuario_id=current_user.id,
        discussao_pai_id=id_discussao_principal
    )

    db.session.add(
        nova_resposta
    )

    db.session.commit()

    # =====================================================
    # NOTIFICAR AUTOR DA DISCUSSÃO
    # =====================================================

    discussao_principal = (
        db.session.get(
            Discussao,
            id_discussao_principal
        )
    )

    if (
        discussao_principal
        and discussao_principal.usuario_id
        != current_user.id
    ):

        criar_notificacao(
            usuario_id=discussao_principal.usuario_id,
            categoria='clubes',
            tipo='resposta_discussao',
            titulo='Responderam sua discussão',
            mensagem=(
                f'{current_user.nome} respondeu '
                f'seu comentário no clube '
                f'{clube.nome}.'
            ),
            link=url_for(
                'clubes.ver_clube',
                clube_id=clube.id
            )
        )

    flash(
        'Resposta publicada!',
        'sucesso'
    )

    return redirect(
        url_for(
            'clubes.ver_clube',
            clube_id=clube.id
        )
    )


# =========================================================
# ENTRAR EM CLUBE PÚBLICO
# =========================================================

@clubes_bp.route(
    '/<int:clube_id>/entrar',
    methods=['POST']
)
@login_required
def entrar_clube(clube_id):

    clube = Clube.query.get_or_404(
        clube_id
    )

    if clube.privado:

        return redirect(
            url_for(
                'clubes.ver_clube',
                clube_id=clube_id
            )
        )

    membro_existente = (
        MembroClube.query
        .filter_by(
            clube_id=clube.id,
            usuario_id=current_user.id
        )
        .first()
    )

    if membro_existente:

        return redirect(
            url_for(
                'clubes.ver_clube',
                clube_id=clube_id
            )
        )

    novo_membro = MembroClube(
        clube_id=clube.id,
        usuario_id=current_user.id,
        paginas_lidas=0,
        progresso_percentual=0,
        total_atualizacoes=0
    )

    db.session.add(
        novo_membro
    )

    db.session.flush()

    clube.quantidade_membros = (
        MembroClube.query
        .filter_by(
            clube_id=clube.id
        )
        .count()
    )

    db.session.commit()

    return redirect(
        url_for(
            'clubes.ver_clube',
            clube_id=clube_id
        )
    )


# =========================================================
# ATUALIZAR PROGRESSO
# =========================================================

@clubes_bp.route(
    '/<int:clube_id>/atualizar-progresso',
    methods=['POST']
)
@login_required
def atualizar_progresso(clube_id):

    clube = Clube.query.get_or_404(
        clube_id
    )

    if not clube.livro:

        return redirect(
            url_for(
                'clubes.ver_clube',
                clube_id=clube_id
            )
        )

    membro = (
        MembroClube.query
        .filter_by(
            clube_id=clube.id,
            usuario_id=current_user.id
        )
        .first()
    )

    if not membro:

        return redirect(
            url_for(
                'clubes.ver_clube',
                clube_id=clube_id
            )
        )

    try:

        paginas_lidas = int(
            request.form.get(
                'paginas_lidas',
                0
            )
        )

    except (
        ValueError,
        TypeError
    ):

        paginas_lidas = 0

    total_paginas = (
        clube.livro.paginas or 0
    )

    if paginas_lidas < 0:

        paginas_lidas = 0

    if total_paginas > 0:

        paginas_lidas = min(
            paginas_lidas,
            total_paginas
        )

    membro.paginas_lidas = (
        paginas_lidas
    )

    if total_paginas > 0:

        membro.progresso_percentual = round(
            (
                paginas_lidas
                / total_paginas
            ) * 100
        )

    else:

        membro.progresso_percentual = 0

    membro.total_atualizacoes = (
        membro.total_atualizacoes or 0
    ) + 1

    db.session.commit()

    return redirect(
        url_for(
            'clubes.ver_clube',
            clube_id=clube_id
        )
    )


# =========================================================
# ENVIAR CONVITE
# =========================================================

@clubes_bp.route(
    '/<int:clube_id>/enviar-convite/<int:usuario_id>',
    methods=['POST']
)
@login_required
def enviar_convite(
    clube_id,
    usuario_id
):

    clube = Clube.query.get_or_404(
        clube_id
    )

    amigo = Usuario.query.get_or_404(
        usuario_id
    )

    membro_atual = (
        MembroClube.query
        .filter_by(
            clube_id=clube.id,
            usuario_id=current_user.id
        )
        .first()
    )

    if clube.privado:

        if clube.usuario_id != current_user.id:

            return redirect(
                url_for(
                    'clubes.ver_clube',
                    clube_id=clube_id
                )
            )

    else:

        if not membro_atual:

            return redirect(
                url_for(
                    'clubes.ver_clube',
                    clube_id=clube_id
                )
            )

    if amigo.id == current_user.id:

        return redirect(
            url_for(
                'clubes.ver_clube',
                clube_id=clube_id
            )
        )

    membro_existente = (
        MembroClube.query
        .filter_by(
            clube_id=clube.id,
            usuario_id=amigo.id
        )
        .first()
    )

    if membro_existente:

        return redirect(
            url_for(
                'clubes.ver_clube',
                clube_id=clube_id
            )
        )

    convite_existente = (
        ConviteClube.query
        .filter_by(
            clube_id=clube.id,
            destinatario_id=amigo.id,
            status='pendente'
        )
        .first()
    )

    if convite_existente:

        return redirect(
            url_for(
                'clubes.ver_clube',
                clube_id=clube_id
            )
        )

    novo_convite = ConviteClube(
        clube_id=clube.id,
        remetente_id=current_user.id,
        destinatario_id=amigo.id,
        status='pendente'
    )

    db.session.add(
        novo_convite
    )

    db.session.commit()

    criar_notificacao(
        usuario_id=amigo.id,
        categoria='clubes',
        tipo='convite_clube',
        titulo='Novo convite para clube',
        mensagem=(
            f'{current_user.nome} convidou você '
            f'para participar do clube {clube.nome}.'
        ),
        link=url_for(
            'clubes.convites'
        )
    )

    return redirect(
        url_for(
            'clubes.ver_clube',
            clube_id=clube_id
        )
    )


# =========================================================
# CONVITES RECEBIDOS
# =========================================================

@clubes_bp.route('/convites')
@login_required
def convites():

    convites_recebidos = (
        ConviteClube.query
        .filter_by(
            destinatario_id=current_user.id,
            status='pendente'
        )
        .order_by(
            ConviteClube.data_criacao.desc()
        )
        .all()
    )

    return render_template(
        'clubes/convites.html',
        convites=convites_recebidos
    )


# =========================================================
# ACEITAR CONVITE
# =========================================================

@clubes_bp.route(
    '/convites/<int:convite_id>/aceitar',
    methods=['POST']
)
@login_required
def aceitar_convite(convite_id):

    convite = ConviteClube.query.get_or_404(
        convite_id
    )

    if convite.destinatario_id != current_user.id:

        return redirect(
            url_for(
                'clubes.convites'
            )
        )

    if convite.status != 'pendente':

        return redirect(
            url_for(
                'clubes.convites'
            )
        )

    membro_existente = (
        MembroClube.query
        .filter_by(
            clube_id=convite.clube_id,
            usuario_id=current_user.id
        )
        .first()
    )

    if not membro_existente:

        novo_membro = MembroClube(
            clube_id=convite.clube_id,
            usuario_id=current_user.id,
            paginas_lidas=0,
            progresso_percentual=0,
            total_atualizacoes=0
        )

        db.session.add(
            novo_membro
        )

        db.session.flush()

    clube = Clube.query.get(
        convite.clube_id
    )

    if clube:

        clube.quantidade_membros = (
            MembroClube.query
            .filter_by(
                clube_id=clube.id
            )
            .count()
        )

    convite.status = 'aceita'

    db.session.commit()

    if clube:

        criar_notificacao(
            usuario_id=convite.remetente_id,
            categoria='clubes',
            tipo='convite_aceito',
            titulo='Convite aceito!',
            mensagem=(
                f'{current_user.nome} aceitou seu convite '
                f'para participar do clube {clube.nome}.'
            ),
            link=url_for(
                'clubes.ver_clube',
                clube_id=clube.id
            )
        )

    return redirect(
        url_for(
            'clubes.ver_clube',
            clube_id=convite.clube_id
        )
    )


# =========================================================
# RECUSAR CONVITE
# =========================================================

@clubes_bp.route(
    '/convites/<int:convite_id>/recusar',
    methods=['POST']
)
@login_required
def recusar_convite(convite_id):

    convite = ConviteClube.query.get_or_404(
        convite_id
    )

    if convite.destinatario_id != current_user.id:

        return redirect(
            url_for(
                'clubes.convites'
            )
        )

    if convite.status != 'pendente':

        return redirect(
            url_for(
                'clubes.convites'
            )
        )

    convite.status = 'recusada'

    db.session.commit()

    return redirect(
        url_for(
            'clubes.convites'
        )
    )