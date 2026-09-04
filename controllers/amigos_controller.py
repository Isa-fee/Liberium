from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    request,
    flash
)

from flask_login import (
    login_required,
    current_user
)

from models import (
    Usuario,
    Amizade,
    Estante,
    DecoracaoEstante,
    ElogioEstante,
    MembroClube
)

from utils.notificacoes import criar_notificacao
from controllers.estante_controller import montar_prateleira
from extensions import db


amigos_bp = Blueprint(
    "amigos_bp",
    __name__,
    url_prefix="/amigos"
)


# =========================================================
# GERAR SUGESTÕES DE AMIZADE
# =========================================================

def gerar_sugestoes_amizade(usuario_id, ids_excluidos, limite=6):

    # =====================================================
    # DADOS DO USUÁRIO ATUAL
    # =====================================================

    minhas_amizades = Amizade.query.filter(
        Amizade.status == "aceita",
        (
            (Amizade.usuario_id == usuario_id) |
            (Amizade.amigo_id == usuario_id)
        )
    ).all()

    meus_amigos_ids = set()

    for amizade in minhas_amizades:

        if amizade.usuario_id == usuario_id:
            meus_amigos_ids.add(amizade.amigo_id)
        else:
            meus_amigos_ids.add(amizade.usuario_id)


    # -----------------------------------------------------
    # CLUBES DO USUÁRIO
    # -----------------------------------------------------

    meus_clubes_ids = {
        membro.clube_id
        for membro in MembroClube.query.filter_by(
            usuario_id=usuario_id
        ).all()
    }


    # -----------------------------------------------------
    # LIVROS DO USUÁRIO
    # -----------------------------------------------------

    minha_estante = Estante.query.filter_by(
        usuario_id=usuario_id
    ).all()

    meus_livros_lidos = {
        item.livro_id
        for item in minha_estante
        if item.status == "lido"
    }

    meus_livros_lendo = {
        item.livro_id
        for item in minha_estante
        if item.status == "lendo"
    }

    meus_livros_quero_ler = {
        item.livro_id
        for item in minha_estante
        if item.status == "quero_ler"
    }


    # =====================================================
    # POSSÍVEIS SUGESTÕES
    # =====================================================

    candidatos = Usuario.query.filter(
        ~Usuario.id.in_(ids_excluidos)
    ).all()

    sugestoes = []


    # =====================================================
    # ANALISAR CADA CANDIDATO
    # =====================================================

    for candidato in candidatos:

        pontuacao = 0


        # -------------------------------------------------
        # AMIGOS EM COMUM
        # -------------------------------------------------

        amizades_candidato = Amizade.query.filter(
            Amizade.status == "aceita",
            (
                (Amizade.usuario_id == candidato.id) |
                (Amizade.amigo_id == candidato.id)
            )
        ).all()

        amigos_candidato_ids = set()

        for amizade in amizades_candidato:

            if amizade.usuario_id == candidato.id:
                amigos_candidato_ids.add(
                    amizade.amigo_id
                )
            else:
                amigos_candidato_ids.add(
                    amizade.usuario_id
                )

        amigos_comuns_ids = (
            meus_amigos_ids &
            amigos_candidato_ids
        )

        amigos_comuns = len(
            amigos_comuns_ids
        )

        pontuacao += amigos_comuns * 5


        # -------------------------------------------------
        # CLUBES EM COMUM
        # -------------------------------------------------

        clubes_candidato_ids = {
            membro.clube_id
            for membro in MembroClube.query.filter_by(
                usuario_id=candidato.id
            ).all()
        }

        clubes_comuns_ids = (
            meus_clubes_ids &
            clubes_candidato_ids
        )

        clubes_comuns = len(
            clubes_comuns_ids
        )

        pontuacao += clubes_comuns * 4


        # -------------------------------------------------
        # ESTANTE DO CANDIDATO
        # -------------------------------------------------

        estante_candidato = Estante.query.filter_by(
            usuario_id=candidato.id
        ).all()

        livros_lidos_candidato = {
            item.livro_id
            for item in estante_candidato
            if item.status == "lido"
        }

        livros_lendo_candidato = {
            item.livro_id
            for item in estante_candidato
            if item.status == "lendo"
        }

        livros_quero_ler_candidato = {
            item.livro_id
            for item in estante_candidato
            if item.status == "quero_ler"
        }


        # -------------------------------------------------
        # LIVROS LIDOS EM COMUM
        # -------------------------------------------------

        livros_lidos_comuns_ids = (
            meus_livros_lidos &
            livros_lidos_candidato
        )

        livros_lidos_comuns = len(
            livros_lidos_comuns_ids
        )

        pontuacao += livros_lidos_comuns * 3


        # -------------------------------------------------
        # LIVROS SENDO LIDOS EM COMUM
        # -------------------------------------------------

        livros_lendo_comuns_ids = (
            meus_livros_lendo &
            livros_lendo_candidato
        )

        livros_lendo_comuns = len(
            livros_lendo_comuns_ids
        )

        pontuacao += livros_lendo_comuns * 4


        # -------------------------------------------------
        # QUERO LER EM COMUM
        # -------------------------------------------------

        livros_quero_ler_comuns_ids = (
            meus_livros_quero_ler &
            livros_quero_ler_candidato
        )

        livros_quero_ler_comuns = len(
            livros_quero_ler_comuns_ids
        )

        pontuacao += livros_quero_ler_comuns


        # =================================================
        # GUARDAR RECOMENDAÇÃO
        # =================================================

        sugestoes.append({

            "usuario": candidato,

            "pontuacao": pontuacao,

            "amigos_comuns": amigos_comuns,

            "clubes_comuns": clubes_comuns,

            "livros_lidos_comuns": livros_lidos_comuns,

            "livros_lendo_comuns": livros_lendo_comuns,

            "livros_quero_ler_comuns": livros_quero_ler_comuns
        })


    # =====================================================
    # ORDENAR POR RELEVÂNCIA
    # =====================================================

    sugestoes.sort(
        key=lambda sugestao: (
            sugestao["pontuacao"],
            sugestao["amigos_comuns"],
            sugestao["clubes_comuns"],
            sugestao["livros_lendo_comuns"],
            sugestao["livros_lidos_comuns"]
        ),
        reverse=True
    )


    # =====================================================
    # RETORNAR APENAS O LIMITE
    # =====================================================

    return sugestoes[:limite]

# =========================================================
# PÁGINA PRINCIPAL
# =========================================================

@amigos_bp.route("/")
@login_required
def amigos():

    # -----------------------------------------------------
    # AMIGOS ACEITOS
    # -----------------------------------------------------

    amizades = Amizade.query.filter(
        Amizade.status == "aceita",
        (
            (Amizade.usuario_id == current_user.id) |
            (Amizade.amigo_id == current_user.id)
        )
    ).all()

    amigos = []

    for amizade in amizades:

        if amizade.usuario_id == current_user.id:
            amigo = amizade.amigo

        else:
            amigo = amizade.usuario

        amigos.append(amigo)


    # -----------------------------------------------------
    # LEITURA ATUAL DOS AMIGOS
    # -----------------------------------------------------

    for amigo in amigos:

        amigo.leitura_atual = Estante.query.filter_by(
            usuario_id=amigo.id,
            status="lendo"
        ).first()


    # -----------------------------------------------------
    # SOLICITAÇÕES RECEBIDAS
    # -----------------------------------------------------

    solicitacoes = Amizade.query.filter_by(
        amigo_id=current_user.id,
        status="pendente"
    ).all()


    # -----------------------------------------------------
    # SUGESTÕES PERSONALIZADAS
    # -----------------------------------------------------

    ids_excluidos = {current_user.id}


    # -----------------------------------------------------
    # EXCLUIR AMIGOS
    # -----------------------------------------------------

    for amizade in amizades:

        ids_excluidos.add(
            amizade.usuario_id
        )

        ids_excluidos.add(
            amizade.amigo_id
        )


    # -----------------------------------------------------
    # EXCLUIR SOLICITAÇÕES EXISTENTES
    # -----------------------------------------------------

    relacoes_existentes = Amizade.query.filter(
        (
            (Amizade.usuario_id == current_user.id) |
            (Amizade.amigo_id == current_user.id)
        )
    ).all()


    for relacao in relacoes_existentes:

        ids_excluidos.add(
            relacao.usuario_id
        )

        ids_excluidos.add(
            relacao.amigo_id
        )


    # -----------------------------------------------------
    # GERAR RECOMENDAÇÕES
    # -----------------------------------------------------

    sugestoes = gerar_sugestoes_amizade(
        current_user.id,
        ids_excluidos,
        limite=6
    )


    # -----------------------------------------------------
    # LIVROS LIDOS
    # -----------------------------------------------------

    livros_lidos = Estante.query.filter_by(
        usuario_id=current_user.id,
        status="lido"
    ).count()


    # -----------------------------------------------------
    # LIVRO ATUAL
    # -----------------------------------------------------

    leitura_atual = Estante.query.filter_by(
        usuario_id=current_user.id,
        status="lendo"
    ).first()


    # -----------------------------------------------------
    # PESQUISA POR NOME OU @USERNAME
    # -----------------------------------------------------

    busca = request.args.get(
        "busca",
        ""
    ).strip()

    resultados_busca = []


    if busca:

        # Se o usuário pesquisar:
        #
        # @isacosta
        #
        # transforma em:
        #
        # isacosta

        termo_username = busca.lstrip("@")


        resultados_busca = Usuario.query.filter(

            Usuario.id != current_user.id,

            db.or_(

                Usuario.nome.ilike(
                    f"%{busca}%"
                ),

                Usuario.username.ilike(
                    f"%{termo_username}%"
                )

            )

        ).all()


    # -----------------------------------------------------
    # RENDERIZAR
    # -----------------------------------------------------

    return render_template(
        "user/amigos.html",

        amigos=amigos,

        solicitacoes=solicitacoes,

        sugestoes=sugestoes,

        resultados_busca=resultados_busca,

        busca=busca,

        livros_lidos=livros_lidos,

        leitura_atual=leitura_atual
    )


# =========================================================
# RANKING DE LEITURA
# =========================================================

@amigos_bp.route("/ranking")
@login_required
def ranking():

    # =====================================================
    # 1. BUSCAR AMIZADES ACEITAS
    # =====================================================

    amizades = Amizade.query.filter(
        Amizade.status == "aceita",
        (
            (Amizade.usuario_id == current_user.id) |
            (Amizade.amigo_id == current_user.id)
        )
    ).all()


    # =====================================================
    # 2. PEGAR OS AMIGOS DO USUÁRIO
    # =====================================================

    usuarios_ranking = [
        current_user
    ]


    for amizade in amizades:

        if amizade.usuario_id == current_user.id:

            amigo = amizade.amigo

        else:

            amigo = amizade.usuario


        if amigo:

            usuarios_ranking.append(
                amigo
            )


    # =====================================================
    # 3. EVITAR USUÁRIOS DUPLICADOS
    # =====================================================

    usuarios_unicos = {}

    for usuario in usuarios_ranking:

        usuarios_unicos[
            usuario.id
        ] = usuario


    usuarios_ranking = list(
        usuarios_unicos.values()
    )


    # =====================================================
    # 4. MONTAR DADOS DO RANKING
    # =====================================================

    ranking_dados = []


    for usuario in usuarios_ranking:

        # -------------------------------------------------
        # ESTANTE DO USUÁRIO
        # -------------------------------------------------

        itens_estante = Estante.query.filter_by(
            usuario_id=usuario.id
        ).all()


        # -------------------------------------------------
        # LIVROS LIDOS
        # -------------------------------------------------

        livros_lidos = 0


        # -------------------------------------------------
        # PÁGINAS LIDAS
        # -------------------------------------------------

        paginas_lidas = 0


        for item in itens_estante:

            # =============================================
            # LIVRO FINALIZADO
            # =============================================

            if item.status == "lido":

                livros_lidos += 1


                if (
                    item.livro
                    and item.livro.paginas
                ):

                    paginas_lidas += (
                        item.livro.paginas
                    )


            # =============================================
            # LIVRO SENDO LIDO
            # =============================================

            elif item.status == "lendo":

                if item.pagina_atual:

                    paginas_lidas += (
                        item.pagina_atual
                    )


        # -------------------------------------------------
        # ADICIONAR AO RANKING
        # -------------------------------------------------

        ranking_dados.append({

            "usuario": usuario,

            "livros_lidos": livros_lidos,

            "paginas_lidas": paginas_lidas,

            "sou_eu": (
                usuario.id
                == current_user.id
            )

        })


    # =====================================================
    # 5. CRITÉRIO ESCOLHIDO
    # =====================================================

    criterio = request.args.get(
        "criterio",
        "livros"
    )


    if criterio not in [
        "livros",
        "paginas"
    ]:

        criterio = "livros"


    # =====================================================
    # 6. ORDENAR RANKING
    # =====================================================

    if criterio == "paginas":

        ranking_dados.sort(
            key=lambda pessoa: (
                pessoa["paginas_lidas"],
                pessoa["livros_lidos"]
            ),
            reverse=True
        )

    else:

        ranking_dados.sort(
            key=lambda pessoa: (
                pessoa["livros_lidos"],
                pessoa["paginas_lidas"]
            ),
            reverse=True
        )


    # =====================================================
    # 7. DEFINIR POSIÇÃO
    # =====================================================

    for indice, pessoa in enumerate(
        ranking_dados,
        start=1
    ):

        pessoa["posicao"] = indice


    # =====================================================
    # 8. DESCOBRIR POSIÇÃO DO USUÁRIO LOGADO
    # =====================================================

    minha_posicao = None


    for pessoa in ranking_dados:

        if pessoa["sou_eu"]:

            minha_posicao = pessoa[
                "posicao"
            ]

            break


    # =====================================================
    # 9. RENDERIZAR
    # =====================================================

    return render_template(
        "user/ranking.html",

        ranking=ranking_dados,

        criterio=criterio,

        minha_posicao=minha_posicao
    )


# =========================================================
# ENVIAR SOLICITAÇÃO
# =========================================================

@amigos_bp.route(
    "/adicionar/<int:usuario_id>",
    methods=["POST"]
)
@login_required
def adicionar_amigo(usuario_id):

    if usuario_id == current_user.id:

        flash(
            "Você não pode adicionar a si mesmo.",
            "erro"
        )

        return redirect(
            url_for("amigos_bp.amigos")
        )


    usuario = Usuario.query.get_or_404(
        usuario_id
    )


    # -----------------------------------------------------
    # VERIFICAR SE JÁ EXISTE RELAÇÃO
    # -----------------------------------------------------

    amizade = Amizade.query.filter(
        (
            (Amizade.usuario_id == current_user.id) &
            (Amizade.amigo_id == usuario_id)
        )
        |
        (
            (Amizade.usuario_id == usuario_id) &
            (Amizade.amigo_id == current_user.id)
        )
    ).first()


    if amizade:

        flash(
            "Já existe uma solicitação ou amizade "
            "com esse leitor.",
            "erro"
        )

        return redirect(
            url_for("amigos_bp.amigos")
        )


    # -----------------------------------------------------
    # CRIAR SOLICITAÇÃO
    # -----------------------------------------------------

    nova_amizade = Amizade(
        usuario_id=current_user.id,
        amigo_id=usuario_id,
        status="pendente"
    )

    db.session.add(
        nova_amizade
    )

    db.session.commit()


    # -----------------------------------------------------
    # NOTIFICAÇÃO
    # -----------------------------------------------------

    criar_notificacao(
        usuario_id=usuario.id,
        categoria="social",
        tipo="amizade",
        titulo="Nova solicitação de amizade",
        mensagem=(
            f"{current_user.nome} enviou uma "
            "solicitação de amizade para você."
        ),
        link=url_for(
            "amigos_bp.solicitacoes"
        )
    )


    flash(
        f"Solicitação enviada para "
        f"{usuario.nome}!",
        "sucesso"
    )


    return redirect(
        url_for(
            "amigos_bp.perfil_usuario",
            usuario_id=usuario_id
        )
    )


# =========================================================
# ACEITAR SOLICITAÇÃO
# =========================================================

@amigos_bp.route(
    "/aceitar/<int:amizade_id>",
    methods=["POST"]
)
@login_required
def aceitar_amizade(amizade_id):

    amizade = Amizade.query.get_or_404(
        amizade_id
    )


    # -----------------------------------------------------
    # SÓ QUEM RECEBEU PODE ACEITAR
    # -----------------------------------------------------

    if amizade.amigo_id != current_user.id:

        flash(
            "Você não pode aceitar essa solicitação.",
            "erro"
        )

        return redirect(
            url_for("amigos_bp.amigos")
        )


    amizade.status = "aceita"

    db.session.commit()


    # -----------------------------------------------------
    # NOTIFICAÇÃO
    # -----------------------------------------------------

    criar_notificacao(
        usuario_id=amizade.usuario_id,
        categoria="social",
        tipo="amizade_aceita",
        titulo="Solicitação de amizade aceita!",
        mensagem=(
            f"{current_user.nome} aceitou sua "
            "solicitação de amizade."
        ),
        link=url_for(
            "amigos_bp.perfil_usuario",
            usuario_id=current_user.id
        )
    )


    flash(
        "Amizade aceita! 🌿",
        "sucesso"
    )


    return redirect(
        url_for("amigos_bp.amigos")
    )


# =========================================================
# RECUSAR SOLICITAÇÃO
# =========================================================

@amigos_bp.route(
    "/recusar/<int:amizade_id>",
    methods=["POST"]
)
@login_required
def recusar_amizade(amizade_id):

    amizade = Amizade.query.get_or_404(
        amizade_id
    )


    if amizade.amigo_id != current_user.id:

        flash(
            "Você não pode recusar essa solicitação.",
            "erro"
        )

        return redirect(
            url_for("amigos_bp.amigos")
        )


    db.session.delete(
        amizade
    )

    db.session.commit()


    flash(
        "Solicitação recusada.",
        "sucesso"
    )


    return redirect(
        url_for("amigos_bp.amigos")
    )


# =========================================================
# PÁGINA DE SOLICITAÇÕES
# =========================================================

@amigos_bp.route("/solicitacoes")
@login_required
def solicitacoes():

    solicitacoes = Amizade.query.filter_by(
        amigo_id=current_user.id,
        status="pendente"
    ).all()


    return render_template(
        "user/solicitacoes.html",
        solicitacoes=solicitacoes
    )


# =========================================================
# ENCONTRAR LEITORES
# =========================================================

@amigos_bp.route("/encontrar")
@login_required
def encontrar_leitores():

    busca = request.args.get(
        "busca",
        ""
    ).strip()

    resultados = []


    if busca:

        # -------------------------------------------------
        # PERMITIR BUSCA COM @
        # -------------------------------------------------

        termo_username = busca.lstrip("@")


        # -------------------------------------------------
        # BUSCAR POR NOME OU USERNAME
        # -------------------------------------------------

        resultados = Usuario.query.filter(

            Usuario.id != current_user.id,

            db.or_(

                Usuario.nome.ilike(
                    f"%{busca}%"
                ),

                Usuario.username.ilike(
                    f"%{termo_username}%"
                )

            )

        ).all()


    return render_template(
        "user/encontrar_leitores.html",

        resultados=resultados,

        busca=busca
    )


# =========================================================
# PERFIL DE OUTRO USUÁRIO
# =========================================================

@amigos_bp.route(
    "/perfil/<int:usuario_id>"
)
@login_required
def perfil_usuario(usuario_id):

    usuario = Usuario.query.get_or_404(
        usuario_id
    )


    # =====================================================
    # LIVROS
    # =====================================================

    livros_lidos = Estante.query.filter_by(
        usuario_id=usuario.id,
        status="lido"
    ).all()


    livros_lendo = Estante.query.filter_by(
        usuario_id=usuario.id,
        status="lendo"
    ).order_by(
        Estante.posicao
    ).all()


    # =====================================================
    # QUANTIDADE DE AMIGOS
    # =====================================================

    quantidade_amigos = Amizade.query.filter(
        Amizade.status == "aceita",
        (
            (Amizade.usuario_id == usuario.id) |
            (Amizade.amigo_id == usuario.id)
        )
    ).count()


    # =====================================================
    # ESTANTE
    # =====================================================

    estante = Estante.query.filter_by(
        usuario_id=usuario.id
    ).all()


    # =====================================================
    # ELOGIOS
    # =====================================================

    elogios = ElogioEstante.query.filter_by(
        destinatario_id=usuario.id
    ).order_by(
        ElogioEstante.data.desc()
    ).all()


    # =====================================================
    # RELAÇÃO DE AMIZADE COM O USUÁRIO LOGADO
    # =====================================================

    amizade = None


    if usuario.id != current_user.id:

        amizade = Amizade.query.filter(
            (
                (Amizade.usuario_id == current_user.id) &
                (Amizade.amigo_id == usuario.id)
            )
            |
            (
                (Amizade.usuario_id == usuario.id) &
                (Amizade.amigo_id == current_user.id)
            )
        ).first()


    # =====================================================
    # RENDERIZAR
    # =====================================================

    return render_template(
        "user/perfil_amigo.html",

        usuario=usuario,

        livros_lidos=livros_lidos,

        livros_lendo=livros_lendo,

        quantidade_amigos=quantidade_amigos,

        estante=estante,

        elogios=elogios,

        amizade=amizade
    )


# =========================================================
# DESFAZER AMIZADE
# =========================================================

@amigos_bp.route(
    "/desfazer-amizade/<int:amizade_id>",
    methods=["POST"]
)
@login_required
def desfazer_amizade(amizade_id):

    amizade = Amizade.query.get_or_404(
        amizade_id
    )


    # -----------------------------------------------------
    # SEGURANÇA
    # -----------------------------------------------------

    if (
        current_user.id != amizade.usuario_id
        and current_user.id != amizade.amigo_id
    ):

        flash(
            "Você não pode desfazer esta amizade.",
            "erro"
        )

        return redirect(
            url_for("amigos_bp.amigos")
        )


    # -----------------------------------------------------
    # DESCOBRIR O OUTRO USUÁRIO
    # -----------------------------------------------------

    if current_user.id == amizade.usuario_id:

        outro_usuario_id = amizade.amigo_id

    else:

        outro_usuario_id = amizade.usuario_id


    db.session.delete(
        amizade
    )

    db.session.commit()


    flash(
        "Amizade desfeita.",
        "sucesso"
    )


    return redirect(
        url_for(
            "amigos_bp.perfil_usuario",
            usuario_id=outro_usuario_id
        )
    )


# =========================================================
# CANCELAR SOLICITAÇÃO ENVIADA
# =========================================================

@amigos_bp.route(
    "/cancelar-solicitacao/<int:amizade_id>",
    methods=["POST"]
)
@login_required
def cancelar_solicitacao(amizade_id):

    amizade = Amizade.query.get_or_404(
        amizade_id
    )


    # -----------------------------------------------------
    # SÓ QUEM ENVIOU PODE CANCELAR
    # -----------------------------------------------------

    if amizade.usuario_id != current_user.id:

        flash(
            "Você não pode cancelar esta solicitação.",
            "erro"
        )

        return redirect(
            url_for("amigos_bp.amigos")
        )


    # -----------------------------------------------------
    # PRECISA ESTAR PENDENTE
    # -----------------------------------------------------

    if amizade.status != "pendente":

        flash(
            "Esta solicitação não está mais pendente.",
            "erro"
        )

        return redirect(
            url_for(
                "amigos_bp.perfil_usuario",
                usuario_id=amizade.amigo_id
            )
        )


    outro_usuario_id = amizade.amigo_id


    db.session.delete(
        amizade
    )

    db.session.commit()


    flash(
        "Solicitação cancelada.",
        "sucesso"
    )


    return redirect(
        url_for(
            "amigos_bp.perfil_usuario",
            usuario_id=outro_usuario_id
        )
    )


# =========================================================
# ESTANTE DE OUTRO USUÁRIO
# =========================================================

@amigos_bp.route(
    "/estante/<int:usuario_id>"
)
@login_required
def estante_amigo(usuario_id):

    usuario = Usuario.query.get_or_404(
        usuario_id
    )


    livros = Estante.query.filter_by(
        usuario_id=usuario.id
    ).order_by(
        Estante.posicao
    ).all()


    decoracoes = DecoracaoEstante.query.filter_by(
        usuario_id=usuario.id
    ).order_by(
        DecoracaoEstante.posicao
    ).all()


    lendo = montar_prateleira(
        livros,
        decoracoes
    )


    return render_template(
        "books/estante_usuario.html",

        usuario=usuario,

        lendo=lendo
    )


# =========================================================
# ENVIAR ELOGIO
# =========================================================

@amigos_bp.route(
    "/elogio/<int:usuario_id>",
    methods=["POST"]
)
@login_required
def enviar_elogio(usuario_id):

    usuario = Usuario.query.get_or_404(
        usuario_id
    )


    mensagem = request.form.get(
        "mensagem",
        ""
    ).strip()


    # -----------------------------------------------------
    # MENSAGEM VAZIA
    # -----------------------------------------------------

    if not mensagem:

        flash(
            "Escreva um elogio antes de enviar.",
            "warning"
        )

        return redirect(
            url_for(
                "amigos_bp.estante_amigo",
                usuario_id=usuario_id
            )
        )


    # -----------------------------------------------------
    # TAMANHO MÁXIMO
    # -----------------------------------------------------

    if len(mensagem) > 300:

        flash(
            "O elogio pode ter no máximo "
            "300 caracteres.",
            "warning"
        )

        return redirect(
            url_for(
                "amigos_bp.estante_amigo",
                usuario_id=usuario_id
            )
        )


    # -----------------------------------------------------
    # NÃO PODE ELOGIAR A SI MESMO
    # -----------------------------------------------------

    if usuario_id == current_user.id:

        flash(
            "Você não pode enviar um elogio "
            "para si mesmo.",
            "warning"
        )

        return redirect(
            url_for(
                "amigos_bp.estante_amigo",
                usuario_id=usuario_id
            )
        )


    # -----------------------------------------------------
    # CRIAR ELOGIO
    # -----------------------------------------------------

    elogio = ElogioEstante(
        autor_id=current_user.id,
        destinatario_id=usuario_id,
        mensagem=mensagem
    )


    db.session.add(
        elogio
    )

    db.session.commit()


    # -----------------------------------------------------
    # NOTIFICAÇÃO
    # -----------------------------------------------------

    criar_notificacao(
        usuario_id=usuario.id,
        categoria="social",
        tipo="elogio",
        titulo="Você recebeu um elogio!",
        mensagem=(
            f"{current_user.nome} deixou um elogio "
            "na sua estante."
        ),
        link=url_for(
            "amigos_bp.estante_amigo",
            usuario_id=usuario.id
        )
    )


    flash(
        "Elogio enviado! 💚",
        "success"
    )


    return redirect(
        url_for(
            "amigos_bp.estante_amigo",
            usuario_id=usuario_id
        )
    )