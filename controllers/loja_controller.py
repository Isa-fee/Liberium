from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from models import ItemColecionavel, UsuarioColecionavel
from extensions import db

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

    compras = UsuarioColecionavel.query.filter_by(
        usuario_id=current_user.id
    ).all()

    ids_comprados = {
        compra.item_id
        for compra in compras
    }

    return render_template(
        "loja.html",
        decoracoes=decoracoes,
        bonecos=bonecos,
        ids_comprados=ids_comprados
    )

@loja_bp.route("/comprar/<int:item_id>", methods=["POST"])
@login_required
def comprar(item_id):

    item = ItemColecionavel.query.get_or_404(item_id)

    ja_possui = UsuarioColecionavel.query.filter_by(
        usuario_id=current_user.id,
        item_id=item.id
    ).first()

    if ja_possui:

        flash(
            "Você já possui este item!",
            "warning"
        )

        return redirect(
            url_for("loja_bp.loja")
        )

    if current_user.libelulas < item.preco:

        flash(
            "Você não possui Mini Libélulas suficientes.",
            "danger"
        )

        return redirect(
            url_for("loja_bp.loja")
        )

    current_user.libelulas -= item.preco

    compra = UsuarioColecionavel(
        usuario_id=current_user.id,
        item_id=item.id
    )

    db.session.add(compra)

    db.session.commit()

    flash(
        f"{item.nome} adquirido com sucesso!",
        "success"
    )

    return redirect(
        url_for("loja_bp.loja")
    )


@loja_bp.route("/colecao")
@login_required
def colecao():

    compras = UsuarioColecionavel.query.filter_by(
        usuario_id=current_user.id
    ).all()

    decoracoes = [
        compra.item
        for compra in compras
        if compra.item.tipo == "decoracao"
    ]

    bonecos = [
        compra.item
        for compra in compras
        if compra.item.tipo == "boneco"
    ]

    return render_template(
        "colecao.html",
        decoracoes=decoracoes,
        bonecos=bonecos
    )