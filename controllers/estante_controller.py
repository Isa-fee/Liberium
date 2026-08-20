from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from datetime import date

from utils.gamificacao import adicionar_xp, adicionar_libelulas
from utils.insignias import verificar_insignias
from utils.atividades import registrar_atividade

from models import Estante, DecoracaoEstante, UsuarioColecionavel
from extensions import db


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

    return render_template(
        "books/estante_usuario.html",
        usuario=usuario,
        itens_lendo=itens_lendo,
        itens_lidos=itens_lidos,
        itens_quero_ler=itens_quero_ler
    )
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

    nota = int(
        request.form["nota"]
    )

    if nota < 1 or nota > 5:

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

    data_leitura = request.form.get(
        "data_leitura"
    )

    if data_leitura:

        data_leitura = date.fromisoformat(
            data_leitura
        )

    # ======================================
    # PRIMEIRA AVALIAÇÃO
    # ======================================

    if item.nota is None:

        registrar_atividade(
            current_user,
            "avaliacao",
            f'Você avaliou "{item.livro.titulo}" com {nota} estrelas.',
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

    resenha_nova = request.form.get(
        "resenha",
        ""
    ).strip()

    if not item.resenha and resenha_nova:

        registrar_atividade(
            current_user,
            "resenha",
            f'Você escreveu uma resenha para "{item.livro.titulo}".',
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
    # SALVAR AVALIAÇÃO
    # ======================================

    item.nota = nota
    item.resenha = resenha_nova
    item.data_leitura = data_leitura

    db.session.commit()

    # ======================================
    # VERIFICAR INSÍGNIAS
    # ======================================

    verificar_insignias(current_user)

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