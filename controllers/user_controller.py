from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db
from models import Usuario

user_bp = Blueprint("user_bp", __name__, url_prefix="/user")

@user_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        nome = request.form.get("nome")
        email = request.form.get("email")
        senha = request.form.get("senha")
        # Verificar se email já existe
        if Usuario.query.filter_by(email=email).first():
            flash("E-mail já está em uso!", "danger")
            return redirect(url_for("user_bp.register"))
        novo = Usuario(
            nome=nome,
            email=email,
            senha=generate_password_hash(senha)
        )
        db.session.add(novo)
        db.session.commit()
        flash("Usuário registrado com sucesso!", "success")
        return redirect(url_for("user_bp.login"))
    return render_template("user/register.html")

@user_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        senha = request.form.get("senha")
        usuario = Usuario.query.filter_by(email=email).first()
        if usuario and check_password_hash(usuario.senha, senha):
            session["usuario_id"] = usuario.id
            flash("Login realizado!", "success")
            return redirect(url_for("home.home"))
        flash("E-mail ou senha incorretos", "danger")
    return render_template("user/login.html")

@user_bp.route("/logout")
def logout():
    session.pop("usuario_id", None)
    flash("Logout realizado!", "success")
    return redirect(url_for("home.home"))
