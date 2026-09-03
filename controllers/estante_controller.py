from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file
from flask_login import login_required, current_user
from datetime import date, datetime

from utils.gamificacao import adicionar_xp, adicionar_libelulas
from utils.insignias import verificar_insignias
from utils.atividades import registrar_atividade
from utils.notificacoes import criar_notificacao

from models import Estante, DecoracaoEstante, UsuarioColecionavel, ElogioEstante, ComentarioResenha
from extensions import db


#teste

from utils.gerar_imagem import gerar_card_livro_concluido

estante_bp = Blueprint(
    "estante_bp",
    __name__,
    url_prefix="/books"
)


# ======================================
# CALCULAR PRÓXIMA POSIÇÃO
# ======================================

def proxima_posicao(usuario_id, prateleira):

    ultimo_livro = Estante.query.filter_by(
        usuario_id=usuario_id,
        status=prateleira
    ).order_by(
        Estante.posicao.desc()
    ).first()

    ultima_decoracao = DecoracaoEstante.query.filter_by(
        usuario_id=usuario_id,
        prateleira=prateleira
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

    return maior_posicao + 1


# ======================================
# VISUALIZAR ESTANTE
# ======================================

def montar_prateleira(livros, decoracoes):

    itens = []

    # ------------------------------
    # LIVROS
    # ------------------------------

    for livro in livros:

        itens.append({
            "tipo": "livro",
            "objeto": livro,
            "posicao": livro.posicao
        })

    # ------------------------------
    # DECORAÇÕES
    # ------------------------------

    for decoracao in decoracoes:

        itens.append({
            "tipo": "decoracao",
            "objeto": decoracao,
            "posicao": decoracao.posicao
        })

    # ------------------------------
    # ORDENAR TUDO JUNTO
    # ------------------------------

    itens.sort(
        key=lambda item: item["posicao"]
    )

    return itens


@estante_bp.route("/estante")
@login_required
def estante():

    # ==================================
    # LIVROS
    # ==================================

    lendo = Estante.query.filter_by(
        usuario_id=current_user.id,
        status="lendo"
    ).order_by(
        Estante.posicao
    ).all()

    lidos = Estante.query.filter_by(
        usuario_id=current_user.id,
        status="lido"
    ).order_by(
        Estante.posicao
    ).all()

    quero_ler = Estante.query.filter_by(
        usuario_id=current_user.id,
        status="quero ler"
    ).order_by(
        Estante.posicao
    ).all()

    # ==================================
    # DECORAÇÕES
    # ==================================

    decoracoes_lendo = DecoracaoEstante.query.filter_by(
        usuario_id=current_user.id,
        prateleira="lendo"
    ).order_by(
        DecoracaoEstante.posicao
    ).all()

    decoracoes_lidos = DecoracaoEstante.query.filter_by(
        usuario_id=current_user.id,
        prateleira="lidos"
    ).order_by(
        DecoracaoEstante.posicao
    ).all()

    decoracoes_quero_ler = DecoracaoEstante.query.filter_by(
        usuario_id=current_user.id,
        prateleira="quero ler"
    ).order_by(
        DecoracaoEstante.posicao
    ).all()

    # ==================================
    # MONTAR PRATELEIRAS
    # ==================================

    itens_lendo = montar_prateleira(
        lendo,
        decoracoes_lendo
    )

    itens_lidos = montar_prateleira(
        lidos,
        decoracoes_lidos
    )

    itens_quero_ler = montar_prateleira(
        quero_ler,
        decoracoes_quero_ler
    )

    return render_template(
        "books/estante.html",
        itens_lendo=itens_lendo,
        itens_lidos=itens_lidos,
        itens_quero_ler=itens_quero_ler
    )

# ======================================
# VISUALIZAR ESTANTE DE OUTRO USUÁRIO
# ======================================

@estante_bp.route("/estante/<int:usuario_id>")
@login_required
def estante_usuario(usuario_id):

    from models import Usuario

    usuario = Usuario.query.get_or_404(usuario_id)

    # ==================================
    # LIVROS
    # ==================================

    lendo = Estante.query.filter_by(
        usuario_id=usuario.id,
        status="lendo"
    ).order_by(
        Estante.posicao
    ).all()

    lidos = Estante.query.filter_by(
        usuario_id=usuario.id,
        status="lido"
    ).order_by(
        Estante.posicao
    ).all()

    quero_ler = Estante.query.filter_by(
        usuario_id=usuario.id,
        status="quero ler"
    ).order_by(
        Estante.posicao
    ).all()

    # ==================================
    # DECORAÇÕES
    # ==================================

    decoracoes_lendo = DecoracaoEstante.query.filter_by(
        usuario_id=usuario.id,
        prateleira="lendo"
    ).order_by(
        DecoracaoEstante.posicao
    ).all()

    decoracoes_lidos = DecoracaoEstante.query.filter_by(
        usuario_id=usuario.id,
        prateleira="lidos"
    ).order_by(
        DecoracaoEstante.posicao
    ).all()

    decoracoes_quero_ler = DecoracaoEstante.query.filter_by(
        usuario_id=usuario.id,
        prateleira="quero ler"
    ).order_by(
        DecoracaoEstante.posicao
    ).all()

    # ==================================
    # MONTAR PRATELEIRAS
    # ==================================

    itens_lendo = montar_prateleira(
        lendo,
        decoracoes_lendo
    )

    itens_lidos = montar_prateleira(
        lidos,
        decoracoes_lidos
    )

    itens_quero_ler = montar_prateleira(
        quero_ler,
        decoracoes_quero_ler
    )

    elogios = ElogioEstante.query.filter_by(
    destinatario_id=usuario.id
    ).order_by(
        ElogioEstante.data.desc()
    ).all()

    return render_template(
        "books/estante_usuario.html",
        usuario=usuario,
        itens_lendo=itens_lendo,
        itens_lidos=itens_lidos,
        itens_quero_ler=itens_quero_ler,
        elogios=elogios    )
# REORDENAR ESTANTE
# ======================================

@estante_bp.route(
    "/estante/reordenar",
    methods=["POST"]
)

@login_required
def reordenar_estante():

    dados = request.get_json()

    if not dados:
        return {
            "sucesso": False,
            "erro": "Dados inválidos."
        }, 400

    prateleira = dados.get("prateleira")
    ordem = dados.get("ordem")

    if prateleira not in [
        "lendo",
        "lidos",
        "quero ler"
    ]:
        return {
            "sucesso": False,
            "erro": "Prateleira inválida."
        }, 400

    if not isinstance(ordem, list):
        return {
            "sucesso": False,
            "erro": "Ordem inválida."
        }, 400

    # ======================================
    # ATUALIZAR POSIÇÕES
    # ======================================

    for item in ordem:

        item_id = item.get("id")
        tipo = item.get("tipo")
        posicao = item.get("posicao")

        if item_id is None or posicao is None:
            continue

        # ==================================
        # LIVRO
        # ==================================

        if tipo == "livro":

            livro = Estante.query.filter_by(
                id=item_id,
                usuario_id=current_user.id
            ).first()

            if not livro:
                continue

            # Livro NÃO pode mudar de prateleira.
            if livro.status != prateleira:
                continue

            livro.posicao = posicao

        # ==================================
        # DECORAÇÃO
        # ==================================

        elif tipo == "decoracao":

            decoracao = DecoracaoEstante.query.filter_by(
                id=item_id,
                usuario_id=current_user.id
            ).first()

            if not decoracao:
                continue

            # Decoração PODE mudar de prateleira.
            decoracao.prateleira = prateleira
            decoracao.posicao = posicao

    db.session.commit()

    return {
        "sucesso": True
    }

# ======================================
# DECORAR
# ======================================

@estante_bp.route(
    "/decorar/<int:usuario_item_id>",
    methods=["POST"]
)
@login_required
def decorar_estante(usuario_item_id):

    compra = UsuarioColecionavel.query.filter_by(
        id=usuario_item_id,
        usuario_id=current_user.id
    ).first_or_404()

    # ==================================
    # VERIFICAR SE JÁ ESTÁ NA ESTANTE
    # ==================================

    ja_esta_na_estante = DecoracaoEstante.query.filter_by(
        usuario_id=current_user.id,
        usuario_item_id=compra.id
    ).first()

    if ja_esta_na_estante:

        flash(
            "Este item já está na sua estante!",
            "warning"
        )

        return redirect(
            url_for("loja_bp.colecao")
        )

    # ==================================
    # PEGAR PRATELEIRA
    # ==================================

    prateleira = request.form.get("prateleira")

    if prateleira not in [
        "lendo",
        "lidos",
        "quero ler"
    ]:

        flash(
            "Prateleira inválida.",
            "danger"
        )

        return redirect(
            url_for("loja_bp.colecao")
        )

    # ==================================
    # CALCULAR POSIÇÃO
    # ==================================

    posicao = proxima_posicao(
        current_user.id,
        prateleira
    )

    # ==================================
    # CRIAR DECORAÇÃO
    # ==================================

    decoracao = DecoracaoEstante(
        usuario_id=current_user.id,
        usuario_item_id=compra.id,
        prateleira=prateleira,
        posicao=posicao
    )

    db.session.add(decoracao)
    db.session.commit()

    flash(
        f"{compra.item.nome} foi colocado na estante!",
        "success"
    )

    return redirect(
        url_for("estante_bp.estante")
    )

# ======================================
# REMOVER DECORAÇÃO DA ESTANTE
# ======================================

@estante_bp.route(
    "/decoracao/remover/<int:decoracao_id>",
    methods=["POST"]
)
@login_required
def remover_decoracao(decoracao_id):

    decoracao = DecoracaoEstante.query.filter_by(
        id=decoracao_id,
        usuario_id=current_user.id
    ).first_or_404()

    db.session.delete(decoracao)
    db.session.commit()

    flash(
        "Decoração removida da estante!",
        "success"
    )

    return redirect(
        url_for("estante_bp.estante")
    )


# ======================================
# ATUALIZAR PROGRESSO
# ======================================

@estante_bp.route(
    "/progresso/<int:id>",
    methods=["POST"]
)
@login_required
def atualizar_progresso(id):

    item = Estante.query.filter_by(
        usuario_id=current_user.id,
        livro_id=id
    ).first_or_404()

    pagina = int(
        request.form["pagina"]
    )

    if pagina < 0:
        pagina = 0

    if pagina > item.livro.paginas:
        pagina = item.livro.paginas

    # Guarda o status anterior
    status_anterior = item.status

    item.pagina_atual = pagina

    item.progresso = round(
        (pagina / item.livro.paginas) * 100
    )

    # ==================================
    # AINDA NÃO COMEÇOU
    # ==================================

    if item.progresso == 0:

        item.status = "quero ler"

    # ==================================
    # COMEÇOU A LER
    # ==================================

    elif item.progresso < 100:

        item.status = "lendo"

        if status_anterior == "quero ler":

            # Livro mudou de prateleira.
            # Coloca no final da nova prateleira.

            item.posicao = proxima_posicao(
                current_user.id,
                "lendo"
            )

            registrar_atividade(
                current_user,
                "inicio_leitura",
                f'Você começou a ler "{item.livro.titulo}".',
                item.livro
            )

    # ==================================
    # CONCLUIU
    # ==================================

    else:

        if item.status != "lido":

            registrar_atividade(
                current_user,
                "conclusao",
                f'Você terminou de ler "{item.livro.titulo}".',
                item.livro
            )

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

        # Se mudou para "lido",
        # coloca no final da prateleira.

        if item.status != "lido":

            item.posicao = proxima_posicao(
                current_user.id,
                "lido"
            )

        item.status = "lido"

        if item.data_leitura is None:

            item.data_leitura = date.today()

    db.session.commit()

    verificar_insignias(current_user)

    flash(
        "Progresso atualizado!",
        "success"
    )

    return redirect(
        url_for(
            "books_bp.ver",
            id=id
        )
    )

# ======================================
# FAVORITAR / DESFAVORITAR LIVRO
# ======================================

@estante_bp.route(
    "/favoritar/<int:livro_id>",
    methods=["POST"]
)
@login_required
def favoritar_livro(livro_id):

    item = Estante.query.filter_by(
        usuario_id=current_user.id,
        livro_id=livro_id
    ).first_or_404()

    # ==================================
    # SOMENTE LIVROS LIDOS
    # ==================================

    if item.status != "lido":

        flash(
            "Você só pode favoritar livros que já terminou de ler.",
            "warning"
        )

        return redirect(
            url_for(
                "books_bp.ver",
                id=livro_id
            )
        )

    # ==================================
    # ALTERNAR FAVORITO
    # ==================================

    item.favorito = not item.favorito

    db.session.commit()

    # ==================================
    # MENSAGEM
    # ==================================

    if item.favorito:

        flash(
            f'"{item.livro.titulo}" foi adicionado aos seus favoritos! ♥',
            "success"
        )

    else:

        flash(
            f'"{item.livro.titulo}" foi removido dos seus favoritos.',
            "success"
        )

    return redirect(
        url_for(
            "books_bp.ver",
            id=livro_id
        )
    )


# ======================================
# AVALIAR LIVRO / ESCREVER RESENHA
# ======================================

@estante_bp.route(
    "/avaliar/<int:id>",
    methods=["POST"]
)
@login_required
def avaliar(id):

    item = Estante.query.filter_by(
        usuario_id=current_user.id,
        livro_id=id
    ).first_or_404()

    # ======================================
    # NOTA
    # ======================================

    nota = request.form.get(
        "nota",
        type=int
    )

    if nota is None or nota < 1 or nota > 5:

        flash(
            "A nota deve ser entre 1 e 5.",
            "danger"
        )

        return redirect(
            url_for(
                "books_bp.ver",
                id=id
            )
        )

    # ======================================
    # TÍTULO DA RESENHA
    # ======================================

    titulo_resenha = request.form.get(
        "titulo_resenha",
        ""
    ).strip()

    # ======================================
    # TEXTO DA RESENHA
    # ======================================

    resenha_nova = request.form.get(
        "resenha",
        ""
    ).strip()

    # ======================================
    # SPOILER
    # ======================================

    tem_spoiler = (
        request.form.get("tem_spoiler")
        == "on"
    )

    # ======================================
    # DATA DA LEITURA
    # ======================================

    data_leitura = request.form.get(
        "data_leitura"
    )

    if data_leitura:

        try:

            data_leitura = date.fromisoformat(
                data_leitura
            )

        except ValueError:

            data_leitura = item.data_leitura

    else:

        data_leitura = item.data_leitura

    # ======================================
    # PRIMEIRA AVALIAÇÃO
    # ======================================

    primeira_avaliacao = (
        item.nota is None
    )

    if primeira_avaliacao:

        registrar_atividade(
            current_user,
            "avaliacao",
            (
                f'Você avaliou '
                f'"{item.livro.titulo}" '
                f'com {nota} estrelas.'
            ),
            item.livro
        )

        adicionar_xp(
            current_user,
            15,
            "avaliar um livro"
        )

        adicionar_libelulas(
            current_user,
            2,
            "avaliar um livro"
        )

    # ======================================
    # PRIMEIRA RESENHA
    # ======================================

    primeira_resenha = (
        not item.resenha
        and bool(resenha_nova)
    )

    if primeira_resenha:

        registrar_atividade(
            current_user,
            "resenha",
            (
                f'Você escreveu uma resenha '
                f'para "{item.livro.titulo}".'
            ),
            item.livro
        )

        adicionar_xp(
            current_user,
            50,
            "escrever uma resenha"
        )

        adicionar_libelulas(
            current_user,
            5,
            "escrever uma resenha"
        )

    # ======================================
    # DATA DA RESENHA
    # ======================================

    # Só registra a data na primeira vez.
    # Editar depois não muda a data original.
    if primeira_resenha:

        item.data_resenha = datetime.utcnow()

    # ======================================
    # SALVAR AVALIAÇÃO / RESENHA
    # ======================================

    item.nota = nota
    item.titulo_resenha = (
        titulo_resenha or None
    )
    item.resenha = (
        resenha_nova or None
    )
    item.tem_spoiler = tem_spoiler
    item.data_leitura = data_leitura

    db.session.commit()

    # ======================================
    # VERIFICAR INSÍGNIAS
    # ======================================

    verificar_insignias(
        current_user
    )

    flash(
        "Avaliação salva!",
        "success"
    )

    return redirect(
        url_for(
            "books_bp.ver",
            id=id
        )
    )


# ======================================
# REMOVER DA ESTANTE
# ======================================

@estante_bp.route(
    "/remover-estante/<int:livro_id>",
    methods=["POST"]
)
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

    return redirect(
        url_for(
            "estante_bp.estante"
        )
    )

# ======================================
# MINHAS RESENHAS
# ======================================

@estante_bp.route("/minhas-resenhas")
@login_required
def minhas_resenhas():

    resenhas = Estante.query.filter(
        Estante.usuario_id == current_user.id,
        Estante.nota.isnot(None),
        Estante.resenha.isnot(None),
        Estante.resenha != ""
    ).order_by(
        Estante.id.desc()
    ).all()

    return render_template(
        "books/minhas_resenhas.html",
        resenhas=resenhas
    )

# ======================================
# VISUALIZAR RESENHA
# ======================================

@estante_bp.route("/resenha/<int:resenha_id>")
@login_required
def ver_resenha(resenha_id):

    resenha = Estante.query.get_or_404(
        resenha_id
    )

    # Só consideramos resenha se houver texto
    if not resenha.resenha:

        flash(
            "Essa resenha não está disponível.",
            "warning"
        )

        return redirect(
            url_for("books_bp.ver", id=resenha.livro_id)
        )

    comentarios = ComentarioResenha.query.filter_by(
        estante_id=resenha.id
    ).order_by(
        ComentarioResenha.data_criacao.asc()
    ).all()

    return render_template(
        "books/resenha.html",
        resenha=resenha,
        comentarios=comentarios
    )


# ======================================
# COMENTAR RESENHA
# ======================================

@estante_bp.route(
    "/resenha/<int:resenha_id>/comentar",
    methods=["POST"]
)
@login_required
def comentar_resenha(resenha_id):

    resenha = Estante.query.get_or_404(
        resenha_id
    )

    if not resenha.resenha:

        flash(
            "Essa resenha não está disponível.",
            "warning"
        )

        return redirect(
            url_for(
                "books_bp.ver",
                id=resenha.livro_id
            )
        )

    # ======================================
    # PEGAR COMENTÁRIO
    # ======================================

    texto = request.form.get(
        "texto",
        ""
    ).strip()

    if not texto:

        flash(
            "Digite um comentário.",
            "warning"
        )

        return redirect(
            url_for(
                "estante_bp.ver_resenha",
                resenha_id=resenha.id
            )
        )

    if len(texto) > 500:

        flash(
            "O comentário deve ter no máximo 500 caracteres.",
            "warning"
        )

        return redirect(
            url_for(
                "estante_bp.ver_resenha",
                resenha_id=resenha.id
            )
        )

    # ======================================
    # CRIAR COMENTÁRIO
    # ======================================

    comentario = ComentarioResenha(
        estante_id=resenha.id,
        usuario_id=current_user.id,
        texto=texto
    )

    db.session.add(
        comentario
    )

    db.session.commit()

    # ======================================
    # NOTIFICAR DONO DA RESENHA
    # ======================================

    # Não cria notificação se o usuário
    # comentou na própria resenha.
    if resenha.usuario_id != current_user.id:

        criar_notificacao(
            usuario_id=resenha.usuario_id,
            categoria="social",
            tipo="comentario_resenha",
            titulo="Novo comentário na sua resenha",
            mensagem=(
                f'{current_user.nome} comentou na sua '
                f'resenha de "{resenha.livro.titulo}".'
            ),
            link=url_for(
                "estante_bp.ver_resenha",
                resenha_id=resenha.id
            )
        )

    flash(
        "Comentário publicado!",
        "success"
    )

    return redirect(
        url_for(
            "estante_bp.ver_resenha",
            resenha_id=resenha.id
        )
    )
# ======================================
# EDITAR COMENTÁRIO
# ======================================

@estante_bp.route(
    "/comentario/<int:comentario_id>/editar",
    methods=["POST"]
)
@login_required
def editar_comentario(comentario_id):

    comentario = ComentarioResenha.query.get_or_404(
        comentario_id
    )

    # ==================================
    # SOMENTE O AUTOR PODE EDITAR
    # ==================================

    if comentario.usuario_id != current_user.id:

        flash(
            "Você não pode editar este comentário.",
            "danger"
        )

        return redirect(
            url_for(
                "estante_bp.ver_resenha",
                resenha_id=comentario.estante_id
            )
        )

    texto = request.form.get(
        "texto",
        ""
    ).strip()

    if not texto:

        flash(
            "O comentário não pode ficar vazio.",
            "warning"
        )

        return redirect(
            url_for(
                "estante_bp.ver_resenha",
                resenha_id=comentario.estante_id
            )
        )

    if len(texto) > 500:

        flash(
            "O comentário deve ter no máximo 500 caracteres.",
            "warning"
        )

        return redirect(
            url_for(
                "estante_bp.ver_resenha",
                resenha_id=comentario.estante_id
            )
        )

    comentario.texto = texto
    comentario.data_edicao = datetime.utcnow()

    db.session.commit()

    flash(
        "Comentário atualizado!",
        "success"
    )

    return redirect(
        url_for(
            "estante_bp.ver_resenha",
            resenha_id=comentario.estante_id
        )
    )


# ======================================
# EXCLUIR COMENTÁRIO
# ======================================

@estante_bp.route(
    "/comentario/<int:comentario_id>/excluir",
    methods=["POST"]
)
@login_required
def excluir_comentario(comentario_id):

    comentario = ComentarioResenha.query.get_or_404(
        comentario_id
    )

    # ==================================
    # SOMENTE O AUTOR PODE EXCLUIR
    # ==================================

    if comentario.usuario_id != current_user.id:

        flash(
            "Você não pode excluir este comentário.",
            "danger"
        )

        return redirect(
            url_for(
                "estante_bp.ver_resenha",
                resenha_id=comentario.estante_id
            )
        )

    resenha_id = comentario.estante_id

    db.session.delete(
        comentario
    )

    db.session.commit()

    flash(
        "Comentário excluído!",
        "success"
    )

    return redirect(
        url_for(
            "estante_bp.ver_resenha",
            resenha_id=resenha_id
        )
    )


# =========================================================
# TESTE — CARD DE LIVRO CONCLUÍDO
# =========================================================

@estante_bp.route(
    "/teste-compartilhar/<int:livro_id>"
)
@login_required
def teste_compartilhar(livro_id):

    # -----------------------------------------------------
    # PROCURAR O LIVRO NA ESTANTE DO USUÁRIO
    # -----------------------------------------------------

    item_estante = Estante.query.filter_by(
        usuario_id=current_user.id,
        livro_id=livro_id,
        status="lido"
    ).first_or_404()


    livro = item_estante.livro


    # -----------------------------------------------------
    # GERAR CARD
    # -----------------------------------------------------

    caminho = gerar_card_livro_concluido(
        usuario=current_user,
        livro=livro,
        nota=item_estante.nota
    )


    # -----------------------------------------------------
    # MOSTRAR IMAGEM NO NAVEGADOR
    # -----------------------------------------------------

    return send_file(
        caminho,
        mimetype="image/png"
    )