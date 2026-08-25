import os
from extensions import db
from flask import Blueprint, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from models import Clube, Discussao, Livro, MembroClube
from werkzeug.utils import secure_filename

clubes_bp = Blueprint('clubes', __name__, url_prefix='/clubes')


# ======================================
# LISTAR CLUBES
# ======================================


@clubes_bp.route('/')
def listar_clubes():
    clubes = Clube.query.all()

    return render_template('clubes/clubes.html', clubes=clubes)


# ======================================
# PESQUISAR LIVROS
# ======================================


@clubes_bp.route('/buscar-livros')
@login_required
def buscar_livros():
    termo = request.args.get('q', '').strip()

    if not termo:
        return []

    livros = (
        Livro.query.filter(
            db.or_(
                Livro.titulo.ilike(f'%{termo}%'),
                Livro.autor.ilike(f'%{termo}%'),
            )
        )
        .order_by(Livro.titulo.asc())
        .limit(10)
        .all()
    )

    resultados = []

    for livro in livros:
        resultados.append({
            'id': livro.id,
            'titulo': livro.titulo,
            'autor': livro.autor,
            'capa': livro.capa,
        })

    return resultados


# ======================================
# CRIAR CLUBE
# ======================================


@clubes_bp.route('/criar', methods=['GET', 'POST'])
@login_required
def criar_clube():
    if request.method == 'POST':
        nome = request.form.get('nome')
        descricao = request.form.get('descricao')
        genero = request.form.get('genero')

        # ID do livro escolhido na pesquisa
        livro_id = request.form.get('livro_id')

        # Verifica se realmente foi escolhido um livro
        if not livro_id:
            return redirect(url_for('clubes.criar_clube'))

        # Confirma que o livro existe no banco
        livro = Livro.query.get(livro_id)

        if not livro:
            return redirect(url_for('clubes.criar_clube'))

        # ======================================
        # IMAGEM
        # ======================================

        arquivo_imagem = request.files.get('imagem')

        caminho_imagem = None

        if arquivo_imagem and arquivo_imagem.filename:
            nome_arquivo = secure_filename(arquivo_imagem.filename)

            pasta = os.path.join('static', 'img', 'clubes')

            os.makedirs(pasta, exist_ok=True)

            caminho_completo = os.path.join(pasta, nome_arquivo)

            arquivo_imagem.save(caminho_completo)

            caminho_imagem = os.path.join(
                'img', 'clubes', nome_arquivo
            ).replace('\\', '/')

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
        )

        db.session.add(novo_clube)

        # Precisamos gerar o ID do clube
        db.session.flush()

        # Criador entra automaticamente
        membro_criador = MembroClube(
            clube_id=novo_clube.id,
            usuario_id=current_user.id,
            paginas_lidas=0,
            progresso_percentual=0,
            total_atualizacoes=0
        )

        db.session.add(membro_criador)

        # Registra o membro antes de contar
        db.session.flush()

        # Sincroniza a quantidade real
        novo_clube.quantidade_membros = MembroClube.query.filter_by(
            clube_id=novo_clube.id
        ).count()

        db.session.commit()

        return redirect(url_for('clubes.listar_clubes'))

    return render_template('clubes/criar_clube.html')


# ======================================
# VER CLUBE
# ======================================


@clubes_bp.route('/<int:clube_id>')
@login_required
def ver_clube(clube_id):
    clube = Clube.query.get_or_404(clube_id)

    return render_template('clubes/clube.html', clube=clube)


# ======================================
# CRIAR DISCUSSÃO
# ======================================


@clubes_bp.route('/<int:clube_id>/criar-discussao', methods=['POST'])
@login_required
def criar_discussao(clube_id):
    clube = Clube.query.get_or_404(clube_id)

    titulo = request.form.get('titulo')
    conteudo = request.form.get('conteudo')

    # Validação simples
    if not conteudo:
        return redirect(url_for('clubes.ver_clube', clube_id=clube_id))

    nova_discussao = Discussao(
        titulo=titulo,
        conteudo=conteudo,
        clube_id=clube.id,
        usuario_id=current_user.id,
    )

    db.session.add(nova_discussao)
    db.session.commit()

    return redirect(url_for('clubes.ver_clube', clube_id=clube_id))

# ======================================
# ATUALIZAR PROGRESSO NO CLUBE
# ======================================
@clubes_bp.route('/<int:clube_id>/atualizar-progresso', methods=['POST'])
@login_required
def atualizar_progresso(clube_id):
    clube = Clube.query.get_or_404(clube_id)
    # Clube precisa ter um livro
    if not clube.livro:
        return redirect(
            url_for(
                'clubes.ver_clube',
                clube_id=clube_id
            )
        )

    # ======================================
    # PEGAR PÁGINA INFORMADA
    # ======================================

    try:
        paginas_lidas = int(
            request.form.get(
                'paginas_lidas',
                0
            )
        )
    except (ValueError, TypeError):
        paginas_lidas = 0
    total_paginas = clube.livro.paginas or 0

    # Não permite página negativa
    if paginas_lidas < 0:
        paginas_lidas = 0

    # Não permite passar do total do livro
    if total_paginas > 0:
        paginas_lidas = min(
            paginas_lidas,
            total_paginas
        )

    # ======================================
    # BUSCAR MEMBRO
    # ======================================

    membro = MembroClube.query.filter_by(
        clube_id=clube.id,
        usuario_id=current_user.id
    ).first()

    # Caso ainda não exista, cria
    if not membro:
        membro = MembroClube(
            clube_id=clube.id,
            usuario_id=current_user.id,
            paginas_lidas=0,
            progresso_percentual=0,
            total_atualizacoes=0
        )

        db.session.add(membro)

        # Faz o INSERT antes de contar
        db.session.flush()

        # Atualiza a quantidade com o número REAL
        # de membros cadastrados nesse clube
        clube.quantidade_membros = MembroClube.query.filter_by(
            clube_id=clube.id
        ).count()

    # ======================================
    # ATUALIZAR PROGRESSO
    # ======================================

    membro.paginas_lidas = paginas_lidas
    if total_paginas > 0:
        membro.progresso_percentual = round(
            (paginas_lidas / total_paginas) * 100
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
