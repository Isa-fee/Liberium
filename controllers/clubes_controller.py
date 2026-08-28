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

        # ======================================
        # PRIVACIDADE
        # ======================================

        privacidade = request.form.get(
            'privacidade',
            'publico'
        )

        privado = (
            privacidade == 'privado'
        )

        # ======================================
        # LIVRO
        # ======================================

        livro_id = request.form.get(
            'livro_id'
        )

        if not livro_id:

            return redirect(
                url_for(
                    'clubes.criar_clube'
                )
            )

        livro = db.session.get(
            Livro,
            int(livro_id)
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
            quantidade_membros=1,
            privado=privado
        )

        db.session.add(
            novo_clube
        )

        # Necessário para obter o ID antes do commit
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



# VER CLUBE
@clubes_bp.route(
    '/<int:clube_id>'
)
@login_required
def ver_clube(clube_id):

    clube = Clube.query.get_or_404(
        clube_id
    )


    # IDENTIFICAR O CRIADOR
    usuario_eh_criador = (
        clube.usuario_id == current_user.id
    )

    # BUSCAR MEMBROS DO CLUBE
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

    # VERIFICAR SE O USUÁRIO É MEMBRO
    usuario_eh_membro = (
        current_user.id in membros_ids
    )

    # GARANTIR QUE O CRIADOR SEJA MEMBRO
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

        # Atualiza as informações locais
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


    # ATUALIZAR QUANTIDADE DE MEMBROS
    quantidade_real = len(
        membros
    )

    if clube.quantidade_membros != quantidade_real:

        clube.quantidade_membros = (
            quantidade_real
        )

        db.session.commit()

    # QUEM PODE CONVIDAR?
    if clube.privado:

        # PRIVADO:
        # somente o criador
        pode_convidar = (
            usuario_eh_criador
        )

    else:

        # PÚBLICO:
        # qualquer membro
        pode_convidar = (
            usuario_eh_membro
        )
    # BUSCAR AMIZADES ACEITAS
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


    # PEGAR OS AMIGOS
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
    # AMIGOS QUE JÁ SÃO MEMBROS
    # NÃO DEVEM APARECER PARA CONVIDAR
    amigos_disponiveis = [
        amigo
        for amigo in amigos
        if amigo.id not in membros_ids
    ]


    # RENDERIZAR
    return render_template(
        'clubes/clube.html',

        clube=clube,

        membros=membros,

        amigos=amigos_disponiveis,

        usuario_eh_criador=usuario_eh_criador,

        usuario_eh_membro=usuario_eh_membro,

        pode_convidar=pode_convidar
    )

#GERENCIAR CLUBE
@clubes_bp.route(
    '/<int:clube_id>/gerenciar'
)
@login_required
def gerenciar_clube(clube_id):

    clube = Clube.query.get_or_404(
        clube_id
    )

    # Somente o criador pode gerenciar
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

    return render_template(
        'clubes/gerenciar_clube.html',
        clube=clube
    )

# EDITAR CLUBE
@clubes_bp.route(
    '/<int:clube_id>/editar',
    methods=['POST']
)
@login_required
def editar_clube(clube_id):

    clube = Clube.query.get_or_404(
        clube_id
    )
    # SOMENTE O CRIADOR
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

    # DADOS
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

    # VALIDAÇÃO
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

    # ATUALIZAR
    clube.nome = nome
    clube.descricao = descricao
    clube.genero = genero

    clube.privado = (
        privacidade == 'privado'
    )

    # NOVA IMAGEM
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

# REMOVER MEMBRO DO CLUBE
@clubes_bp.route(
    '/<int:clube_id>/remover-membro/<int:usuario_id>',
    methods=['POST']
)
@login_required
def remover_membro(clube_id, usuario_id):

    clube = Clube.query.get_or_404(
        clube_id
    )

    # SOMENTE O CRIADOR PODE REMOVER

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

    # CRIADOR NÃO PODE REMOVER A SI MESMO
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


    # PROCURAR MEMBRO
    membro = MembroClube.query.filter_by(
        clube_id=clube.id,
        usuario_id=usuario_id
    ).first()

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
    # REMOVER
    db.session.delete(
        membro
    )
    db.session.flush()

    # ATUALIZAR QUANTIDADE
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

    # Só membros podem criar discussões
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

    titulo = request.form.get(
        'titulo'
    )

    conteudo = request.form.get(
        'conteudo'
    )

    if not conteudo:

        return redirect(
            url_for(
                'clubes.ver_clube',
                clube_id=clube_id
            )
        )

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
# ENTRAR EM CLUBE PÚBLICO
# ======================================

@clubes_bp.route(
    '/<int:clube_id>/entrar',
    methods=['POST']
)
@login_required
def entrar_clube(clube_id):

    clube = Clube.query.get_or_404(
        clube_id
    )

    # ======================================
    # BLOQUEAR ENTRADA DIRETA EM PRIVADO
    # ======================================

    if clube.privado:

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

    # ======================================
    # ADICIONAR MEMBRO
    # ======================================

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

    if not clube.livro:

        return redirect(
            url_for(
                'clubes.ver_clube',
                clube_id=clube_id
            )
        )

    # ======================================
    # SOMENTE MEMBROS PODEM ATUALIZAR
    # ======================================

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

    # ======================================
    # PÁGINAS LIDAS
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

    if paginas_lidas < 0:
        paginas_lidas = 0

    if total_paginas > 0:

        paginas_lidas = min(
            paginas_lidas,
            total_paginas
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
    # VERIFICAR SE QUEM CONVIDA É MEMBRO
    # ======================================

    membro_atual = (
        MembroClube.query
        .filter_by(
            clube_id=clube.id,
            usuario_id=current_user.id
        )
        .first()
    )

    # ======================================
    # VERIFICAR PERMISSÃO PARA CONVIDAR
    # ======================================

    if clube.privado:

        # Clube privado:
        # somente o criador pode convidar

        if clube.usuario_id != current_user.id:

            return redirect(
                url_for(
                    'clubes.ver_clube',
                    clube_id=clube_id
                )
            )

    else:

        # Clube público:
        # qualquer membro pode convidar

        if not membro_atual:

            return redirect(
                url_for(
                    'clubes.ver_clube',
                    clube_id=clube_id
                )
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
    # VERIFICAR SE JÁ EXISTE CONVITE
    # ======================================

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

    # ======================================
    # VERIFICAR DONO DO CONVITE
    # ======================================

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

    # ======================================
    # VERIFICAR SE JÁ É MEMBRO
    # ======================================

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

    # ======================================
    # ATUALIZAR QUANTIDADE DE MEMBROS
    # ======================================

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