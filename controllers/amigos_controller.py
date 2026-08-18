from flask import Blueprint, render_template
from flask_login import login_required, current_user

from models import Usuario, Estante


amigos_bp = Blueprint(
    "amigos_bp",
    __name__,
    url_prefix="/amigos"
)


@amigos_bp.route("/")
@login_required
def amigos():

    # -----------------------------------------
    # USUÁRIOS
    # -----------------------------------------

    usuarios = Usuario.query.filter(
        Usuario.id != current_user.id
    ).all()

    # Por enquanto, todos os usuários aparecem
    # como sugestões.
    amigos = []

    sugestoes = usuarios[:6]


    # -----------------------------------------
    # LIVROS LIDOS
    # -----------------------------------------

    livros_lidos = Estante.query.filter_by(
        usuario_id=current_user.id,
        status="lido"
    ).count()


    # -----------------------------------------
    # LIVRO ATUAL
    # -----------------------------------------

    livro_atual_estante = Estante.query.filter_by(
        usuario_id=current_user.id,
        status="lendo"
    ).first()

    livro_atual = None

    if livro_atual_estante:
        livro_atual = livro_atual_estante.livro


    # -----------------------------------------
    # RENDER
    # -----------------------------------------

    return render_template(
        "user/amigos.html",

        amigos=amigos,

        sugestoes=sugestoes,

        quantidade_amigos=0,

        livros_lidos=livros_lidos,

        livro_atual=livro_atual
    )