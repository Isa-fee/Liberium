from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user

from extensions import db
from models import Notificacao


notificacoes_bp = Blueprint(
    "notificacoes",
    __name__,
    url_prefix="/notificacoes"
)


# ==========================================
# FUNÇÃO AUXILIAR
# ==========================================

def criar_notificacao(
    usuario_id,
    tipo,
    titulo,
    mensagem,
    link=None
):
    notificacao = Notificacao(
        usuario_id=usuario_id,
        tipo=tipo,
        titulo=titulo,
        mensagem=mensagem,
        link=link
    )

    db.session.add(notificacao)


# ==========================================
# LISTAR NOTIFICAÇÕES
# ==========================================

@notificacoes_bp.route("/")
@login_required
def listar():

    notificacoes = (
        Notificacao.query
        .filter_by(usuario_id=current_user.id)
        .order_by(Notificacao.data_criacao.desc())
        .all()
    )

    return render_template(
        "notificacoes/notificacoes.html",
        notificacoes=notificacoes
    )


# ==========================================
# ABRIR NOTIFICAÇÃO
# ==========================================

@notificacoes_bp.route("/abrir/<int:notificacao_id>")
@login_required
def abrir(notificacao_id):

    notificacao = Notificacao.query.filter_by(
        id=notificacao_id,
        usuario_id=current_user.id
    ).first_or_404()

    if not notificacao.lida:
        notificacao.lida = True
        db.session.commit()

    if notificacao.link:
        return redirect(notificacao.link)

    return redirect(
        url_for("notificacoes.listar")
    )


# ==========================================
# MARCAR UMA COMO LIDA
# ==========================================

@notificacoes_bp.route(
    "/marcar-lida/<int:notificacao_id>",
    methods=["POST"]
)
@login_required
def marcar_lida(notificacao_id):

    notificacao = Notificacao.query.filter_by(
        id=notificacao_id,
        usuario_id=current_user.id
    ).first_or_404()

    notificacao.lida = True

    db.session.commit()

    return redirect(
        url_for("notificacoes.listar")
    )


# ==========================================
# MARCAR TODAS COMO LIDAS
# ==========================================

@notificacoes_bp.route(
    "/marcar-todas-lidas",
    methods=["POST"]
)
@login_required
def marcar_todas_lidas():

    Notificacao.query.filter_by(
        usuario_id=current_user.id,
        lida=False
    ).update(
        {"lida": True},
        synchronize_session=False
    )

    db.session.commit()

    return redirect(
        url_for("notificacoes.listar")
    )