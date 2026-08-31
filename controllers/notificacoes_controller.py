from datetime import datetime, timedelta

from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    request,
    abort
)

from flask_login import (
    login_required,
    current_user
)

from extensions import db
from models import Notificacao


notificacoes_bp = Blueprint(
    "notificacoes",
    __name__,
    url_prefix="/notificacoes"
)


# ==========================================
# LISTAR NOTIFICAÇÕES
# ==========================================

@notificacoes_bp.route("/")
@login_required
def listar():

    # --------------------------------------
    # Remove notificações com mais de 10 dias
    # --------------------------------------

    limite = datetime.utcnow() - timedelta(days=10)

    Notificacao.query.filter(
        Notificacao.usuario_id == current_user.id,
        Notificacao.data_criacao < limite
    ).delete(
        synchronize_session=False
    )

    db.session.commit()

    # --------------------------------------
    # Filtro por categoria
    # --------------------------------------

    categoria = request.args.get(
        "categoria",
        "todas"
    )

    consulta = Notificacao.query.filter_by(
        usuario_id=current_user.id
    )

    if categoria == "nao_lidas":
        consulta = consulta.filter_by(
            lida=False
        )

    elif categoria != "todas":
        consulta = consulta.filter_by(
            categoria=categoria
        )

    notificacoes = consulta.order_by(
        Notificacao.data_criacao.desc()
    ).all()

    return render_template(
        "notificacoes/notificacoes.html",
        notificacoes=notificacoes,
        categoria_atual=categoria
    )


# ==========================================
# ABRIR NOTIFICAÇÃO
# ==========================================

@notificacoes_bp.route(
    "/<int:notificacao_id>/abrir",
    methods=["POST"]
)
@login_required
def abrir(notificacao_id):

    notificacao = Notificacao.query.get_or_404(
        notificacao_id
    )

    # Segurança:
    # usuário só pode abrir a própria notificação.

    if notificacao.usuario_id != current_user.id:
        abort(403)

    notificacao.lida = True

    db.session.commit()

    if notificacao.link:
        return redirect(notificacao.link)

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


# ==========================================
# EXCLUIR NOTIFICAÇÃO
# ==========================================

@notificacoes_bp.route(
    "/<int:notificacao_id>/excluir",
    methods=["POST"]
)
@login_required
def excluir(notificacao_id):

    notificacao = Notificacao.query.get_or_404(
        notificacao_id
    )

    if notificacao.usuario_id != current_user.id:
        abort(403)

    db.session.delete(notificacao)
    db.session.commit()

    return redirect(
        url_for("notificacoes.listar")
    )