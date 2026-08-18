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
    Estante
)

from extensions import db


amigos_bp = Blueprint(
    "amigos_bp",
    __name__,
    url_prefix="/amigos"
)


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
    # SOLICITAÇÕES RECEBIDAS
    # -----------------------------------------------------

    solicitacoes = Amizade.query.filter_by(
        amigo_id=current_user.id,
        status="pendente"
    ).all()


    # -----------------------------------------------------
    # SUGESTÕES
    # -----------------------------------------------------

    ids_excluidos = {current_user.id}

    for amizade in amizades:

        ids_excluidos.add(amizade.usuario_id)
        ids_excluidos.add(amizade.amigo_id)

    for solicitacao in Amizade.query.filter(
        (
            (Amizade.usuario_id == current_user.id) |
            (Amizade.amigo_id == current_user.id)
        )
    ).all():

        ids_excluidos.add(solicitacao.usuario_id)
        ids_excluidos.add(solicitacao.amigo_id)


    sugestoes = Usuario.query.filter(
        ~Usuario.id.in_(ids_excluidos)
    ).limit(6).all()


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
    # PESQUISA
    # -----------------------------------------------------

    busca = request.args.get(
        "busca",
        ""
    ).strip()

    resultados_busca = []

    if busca:

        resultados_busca = Usuario.query.filter(
            Usuario.nome.ilike(f"%{busca}%"),
            Usuario.id != current_user.id
        ).all()


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


    # Verifica se já existe alguma relação
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
            "Já existe uma solicitação ou amizade com esse leitor.",
            "erro"
        )

        return redirect(
            url_for("amigos_bp.amigos")
        )


    nova_amizade = Amizade(
        usuario_id=current_user.id,
        amigo_id=usuario_id,
        status="pendente"
    )

    db.session.add(nova_amizade)
    db.session.commit()


    flash(
        f"Solicitação enviada para {usuario.nome}!",
        "sucesso"
    )


    return redirect(
        url_for("amigos_bp.amigos")
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


    # Só quem recebeu pode aceitar
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


    db.session.delete(amizade)

    db.session.commit()


    flash(
        "Solicitação recusada.",
        "sucesso"
    )


    return redirect(
        url_for("amigos_bp.amigos")
    )


# =========================================================
# PERFIL PÚBLICO
# =========================================================

@amigos_bp.route(
    "/perfil/<int:usuario_id>"
)
@login_required
def perfil_usuario(usuario_id):

    usuario = Usuario.query.get_or_404(
        usuario_id
    )

    # Livros do usuário
    estante = Estante.query.filter_by(
        usuario_id=usuario.id
    ).all()

    livros_lidos = [
        item for item in estante
        if item.status == "lido"
    ]

    leitura_atual = next(
        (
            item for item in estante
            if item.status == "lendo"
        ),
        None
    )

    return render_template(
        "user/perfil_amigo.html",

        usuario=usuario,

        estante=estante,

        livros_lidos=livros_lidos,

        leitura_atual=leitura_atual
    )