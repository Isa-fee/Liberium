from flask import Blueprint, render_template
from flask_login import login_required, current_user

from models import Usuario


amigos_bp = Blueprint(
    "amigos_bp",
    __name__,
    url_prefix="/amigos"
)


@amigos_bp.route("/")
@login_required
def amigos():

    amigos = Usuario.query.filter(
        Usuario.id != current_user.id
    ).all()

    return render_template(
        "amigos/amigos.html",
        amigos=amigos
    )