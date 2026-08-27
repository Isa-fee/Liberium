from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    flash
)
from flask_login import (login_required, current_user)
from models import Livro, SolicitacaoLivro
# ======================================
# BLUEPRINT ADMIN
# ======================================

admin_bp = Blueprint(
    "admin_bp",
    __name__,
    url_prefix="/admin"
)
# ======================================
# PAINEL ADMINISTRATIVO
# ======================================

@admin_bp.route("/")
@login_required
def painel():
    # ==================================
    # SOMENTE ADMINISTRADORES
    # ==================================
    if current_user.tipo != "administrador":
        flash(
            "Você não possui permissão para acessar o painel administrativo.",
            "danger"
        )
        return redirect(
            url_for("home.home")
        )
    # ==================================
    # ESTATÍSTICAS
    # ==================================

    total_livros = Livro.query.count()

    solicitacoes_pendentes = (
        SolicitacaoLivro.query.filter_by(
            status="pendente"
        ).count()
    )
    # ==================================
    # TEMPLATE
    # ==================================

    return render_template(
        "admin/painel.html",
        total_livros=total_livros,
        solicitacoes_pendentes=solicitacoes_pendentes
    )