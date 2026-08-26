import os

from extensions import db

from flask import (
    Blueprint,
    redirect,
    render_template,
    request,
    url_for
)

from flask_login import (
    current_user,
    login_required
)

from models import (
    Clube,
    Discussao,
    Livro,
    MembroClube,
    Amizade,
    Usuario,
    ConviteClube
)

from werkzeug.utils import secure_filename


clubes_bp = Blueprint(
    'clubes',
    __name__,
    url_prefix='/clubes'
)


# ======================================
# LISTAR CLUBES
# ======================================

@clubes_bp.route('/')
def listar_clubes():

    clubes = Clube.query.all()

    return render_template(
        'clubes/clubes.html',
        clubes=clubes
    )


# ======================================
# PESQUISAR LIVROS
# ======================================

@clubes_bp.route('/buscar-livros')
@login_required
def buscar_livros():

    termo = request.args.get(
        'q',
        ''
    ).strip()

    if not termo:
        return []

    livros = (
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
        .limit(10)
        .all()
    )

    resultados = []

    for livro in livros:

        resultados.append({
            'id': livro.id,
            'titulo': livro.titulo,
            'autor': livro.autor,
            'capa': livro.capa
        })

    return resultados


# ======================================
# CRIAR CLUBE
# ======================================

@clubes_bp.route(
    '/criar',
    methods=['GET', 'POST']
)
@login_required
def criar_clube():

    if request.method == 'POST':

        nome = request.form.get(
            'nome'
        )

        descricao = request.form.get(
            'descricao'
        )

        genero = request.form.get(
            'genero'
        )

        # ID do livro escolhido
        livro_id = request.form.get(
            'livro_id'
        )

        # ======================================
        # VERIFICAR LIVRO
        # ======================================

        if not livro_id:

            return redirect(
                url_for(
                    'clubes.criar_clube'
                )
            )

        livro = Livro.query.get(
            livro_id
        )

        if not livro:

            return redirect(
                url_for(
                    'clubes.criar_clube'
                )
            )

        # ======================================
        # IMAGEM
        # ======================================

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

        # ======================================
        # CRIAR CLUBE
        # ======================================

        novo_clube = Clube(
            nome=nome,
            descricao=descricao,
            genero=genero,
            imagem=caminho_imagem,
            usuario_id=current_user.id,
            livro_id=livro.id,
            quantidade_membros=1
        )

        db.session.add(
            novo_clube
        )

        # Gera o ID do clube
        db.session.flush()

        # ======================================
        # ADICIONAR CRIADOR COMO MEMBRO
        # ======================================

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

        db.session.flush()

        # ======================================
        # ATUALIZAR QUANTIDADE DE MEMBROS
        # ======================================

        novo_clube.quantidade_membros = (
            MembroClube.query
            .filter_by(
                clube_id=novo_clube.id
            )
            .count()
        )

        db.session.commit()

        return redirect(
            url_for(
                'clubes.listar_clubes'
            )
        )

    return render_template(
        'clubes/criar_clube.html'
    )


# ======================================
# VER CLUBE
# ======================================

@clubes_bp.route(
    '/<int:clube_id>'
)
@login_required
def ver_clube(clube_id):

    clube = Clube.query.get_or_404(
        clube_id
    )

    # ======================================
    # BUSCAR AMIZADES ACEITAS
    # ======================================

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

    # ======================================
    # PEGAR O OUTRO USUÁRIO
    # ======================================

    amigos = []

    for amizade in amizades:

        if amizade.usuario_id == current_user.id:

            amigo = amizade.amigo

        else:

            amigo = amizade.usuario

        if amigo:
            amigos.append(amigo)

    # ======================================
    # BUSCAR MEMBROS DO CLUBE
    # ======================================

    membros = (
        MembroClube.query
        .filter_by(
            clube_id=clube.id
        )
        .all()
    )

    # IDs das pessoas que já estão no clube
    membros_ids = {
        membro.usuario_id
        for membro in membros
    }

    # ======================================
    # REMOVER QUEM JÁ ESTÁ NO CLUBE
    # ======================================

    amigos_disponiveis = [
        amigo
        for amigo in amigos
        if amigo.id not in membros_ids
    ]

    # ======================================
    # ENVIAR PARA O HTML
    # ======================================

    return render_template(
        'clubes/clube.html',
        clube=clube,
        amigos=amigos_disponiveis
    )


# ======================================
# CRIAR DISCUSSÃO
# ======================================

@clubes_bp.route(
    '/<int:clube_id>/criar-discussao',
    methods=['POST']
)
@login_required
def criar_discussao(clube_id):

    clube = Clube.query.get_or_404(
        clube_id
    )

    titulo = request.form.get(
        'titulo'
    )

    conteudo = request.form.get(
        'conteudo'
    )

    # ======================================
    # VALIDAR CONTEÚDO
    # ======================================

    if not conteudo:

        return redirect(
            url_for(
                'clubes.ver_clube',
                clube_id=clube_id
            )
        )

    # ======================================
    # CRIAR DISCUSSÃO
    # ======================================

    nova_discussao = Discussao(
        titulo=titulo,
        conteudo=conteudo,
        clube_id=clube.id,
        usuario_id=current_user.id
    )

    db.session.add(
        nova_discussao
    )

    db.session.commit()

    return redirect(
        url_for(
            'clubes.ver_clube',
            clube_id=clube_id
        )
    )


# ======================================
# ATUALIZAR PROGRESSO NO CLUBE
# ======================================

@clubes_bp.route(
    '/<int:clube_id>/atualizar-progresso',
    methods=['POST']
)
@login_required
def atualizar_progresso(clube_id):

    clube = Clube.query.get_or_404(
        clube_id
    )

    # ======================================
    # VERIFICAR LIVRO
    # ======================================

    if not clube.livro:

        return redirect(
            url_for(
                'clubes.ver_clube',
                clube_id=clube_id
            )
        )

    # ======================================
    # PEGAR PÁGINA
    # ======================================

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

    # ======================================
    # NÃO PERMITIR VALORES NEGATIVOS
    # ======================================

    if paginas_lidas < 0:

        paginas_lidas = 0

    # ======================================
    # NÃO PASSAR DO TOTAL
    # ======================================

    if total_paginas > 0:

        paginas_lidas = min(
            paginas_lidas,
            total_paginas
        )

    # ======================================
    # BUSCAR MEMBRO
    # ======================================

    membro = (
        MembroClube.query
        .filter_by(
            clube_id=clube.id,
            usuario_id=current_user.id
        )
        .first()
    )

    # ======================================
    # CASO NÃO EXISTA, CRIAR
    # ======================================

    if not membro:

        membro = MembroClube(
            clube_id=clube.id,
            usuario_id=current_user.id,
            paginas_lidas=0,
            progresso_percentual=0,
            total_atualizacoes=0
        )

        db.session.add(
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

    # ======================================
    # ATUALIZAR PROGRESSO
    # ======================================

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
# ======================================
# ENVIAR CONVITE PARA O CLUBE
# ======================================

@clubes_bp.route(
    '/<int:clube_id>/enviar-convite/<int:usuario_id>',
    methods=['POST']
)
@login_required
def enviar_convite(clube_id, usuario_id):

    clube = Clube.query.get_or_404(
        clube_id
    )

    amigo = Usuario.query.get_or_404(
        usuario_id
    )

    # ======================================
    # NÃO PODE CONVIDAR A SI MESMO
    # ======================================

    if amigo.id == current_user.id:

        return redirect(
            url_for(
                'clubes.ver_clube',
                clube_id=clube_id
            )
        )

    # ======================================
    # VERIFICAR SE JÁ É MEMBRO
    # ======================================

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

    # ======================================
    # VERIFICAR SE JÁ EXISTE CONVITE PENDENTE
    # ======================================

    convite_existente = (
        ConviteClube.query
        .filter_by(
            clube_id=clube.id,
            remetente_id=current_user.id,
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

    # ======================================
    # CRIAR CONVITE
    # ======================================

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

    return redirect(
        url_for(
            'clubes.ver_clube',
            clube_id=clube_id
        )
    )

# ======================================
# CONVITES RECEBIDOS
# ======================================

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
# ======================================
# ACEITAR CONVITE
# ======================================

@clubes_bp.route(
    '/convites/<int:convite_id>/aceitar',
    methods=['POST']
)
@login_required
def aceitar_convite(convite_id):

    convite = ConviteClube.query.get_or_404(
        convite_id
    )

    # Verifica se o convite pertence ao usuário logado
    if convite.destinatario_id != current_user.id:

        return redirect(
            url_for('clubes.convites')
        )

    # Só pode aceitar convite pendente
    if convite.status != 'pendente':

        return redirect(
            url_for('clubes.convites')
        )

    # Verifica se já está no clube
    membro_existente = MembroClube.query.filter_by(
        clube_id=convite.clube_id,
        usuario_id=current_user.id
    ).first()

    if not membro_existente:

        novo_membro = MembroClube(
            clube_id=convite.clube_id,
            usuario_id=current_user.id,
            paginas_lidas=0,
            progresso_percentual=0,
            total_atualizacoes=0
        )

        db.session.add(novo_membro)

    # Marca o convite como aceito
    convite.status = 'aceita'

    db.session.commit()

    return redirect(
        url_for(
            'clubes.ver_clube',
            clube_id=convite.clube_id
        )
    )


# ======================================
# RECUSAR CONVITE
# ======================================

@clubes_bp.route(
    '/convites/<int:convite_id>/recusar',
    methods=['POST']
)
@login_required
def recusar_convite(convite_id):

    convite = ConviteClube.query.get_or_404(
        convite_id
    )

    # Verifica se o convite pertence ao usuário logado
    if convite.destinatario_id != current_user.id:

        return redirect(
            url_for('clubes.convites')
        )

    # Só pode recusar convite pendente
    if convite.status != 'pendente':

        return redirect(
            url_for('clubes.convites')
        )

    # Marca o convite como recusado
    convite.status = 'recusada'

    db.session.commit()

    return redirect(
        url_for('clubes.convites')
    )