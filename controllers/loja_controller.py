from flask import Blueprint, render_template
from flask_login import login_required
from models import ItemColecionavel


loja_bp = Blueprint(
    "loja_bp",
    __name__,
    url_prefix="/loja"
)


@loja_bp.route("/")
@login_required
def loja():

    itens = ItemColecionavel.query.all()

    decoracoes = [
        item for item in itens
        if item.tipo == "decoracao"
    ]

    bonecos = [
        item for item in itens
        if item.tipo == "boneco"
    ]

    return render_template(
        "loja.html",
        decoracoes=decoracoes,
        bonecos=bonecos
    )