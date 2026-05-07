from flask import Blueprint, render_template, request, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user

from extensions import db
from models import Usuario

user_bp = Blueprint("user_bp", __name__, url_prefix="/user")


@user_bp.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        nome = request.form.get("nome")
        email = request.form.get("email")
        senha = request.form.get("senha")
        confirmar_senha = request.form.get("confirmar_senha")

        if senha != confirmar_senha:
            flash("As senhas não coincidem!", "danger")
            return redirect(url_for("user_bp.register"))

        usuario_existente = Usuario.query.filter_by(email=email).first()

        if usuario_existente:
            flash("E-mail já cadastrado!", "danger")
            return redirect(url_for("user_bp.register"))

        novo_usuario = Usuario(
            nome=nome,
            email=email,
            senha=generate_password_hash(senha)
        )

        db.session.add(novo_usuario)
        db.session.commit()

        flash("Cadastro realizado com sucesso!", "success")

        return redirect(url_for("user_bp.login"))

    return render_template("user/register.html")


@user_bp.route("/login", methods=["GET", "POST"])
def login():

    if current_user.is_authenticated:
        return redirect(url_for("home.home"))

    if request.method == "POST":

        email = request.form.get("email")
        senha = request.form.get("senha")

        usuario = Usuario.query.filter_by(email=email).first()

        if usuario and check_password_hash(usuario.senha, senha):

            login_user(usuario)

            flash("Login realizado com sucesso!", "success")

            return redirect(url_for("home.home"))

        flash("E-mail ou senha inválidos!", "danger")

    return render_template("user/login.html")


@user_bp.route("/logout")
@login_required
def logout():

    logout_user()

    flash("Logout realizado com sucesso!", "success")

    return redirect(url_for("user_bp.login"))

@user_bp.route("/perfil")
@login_required
def perfil():

    return render_template(
        "user/perfil.html",
        usuario=current_user
    )