from flask import Blueprint, render_template, request, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user

from extensions import db
from models import Usuario, Estante, UsuarioInsignia, MetaLeitura, Atividade, UsuarioColecionavel
from utils.insignias import verificar_insignias
from utils.gamificacao import atualizar_meta_leitura

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

        verificar_insignias(novo_usuario)

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

    from datetime import date

    livros_lidos = Estante.query.filter_by(
        usuario_id=current_user.id,
        status="lido"
    ).count()

    livros_lendo = Estante.query.filter_by(
        usuario_id=current_user.id,
        status="lendo"
    ).count()

    quero_ler = Estante.query.filter_by(
        usuario_id=current_user.id,
        status="quero ler"
    ).count()

    total_livros = Estante.query.filter_by(
        usuario_id=current_user.id
    ).count()

    # ======================================
    # ATIVIDADES RECENTES
    # ======================================

    atividades = Atividade.query.filter_by(
        usuario_id=current_user.id
    ).order_by(
        Atividade.data_criacao.desc()
    ).limit(5).all()

    # ======================================
    # INSÍGNIAS
    # ======================================

    insignias = UsuarioInsignia.query.filter_by(
        usuario_id=current_user.id
    ).all()

    hoje = date.today()

    # ======================================
    # META DO MÊS ATUAL
    # ======================================

    meta = MetaLeitura.query.filter_by(
        usuario_id=current_user.id,
        mes=hoje.month,
        ano=hoje.year
    ).first()

    percentual_meta = 0
    livros_restantes = 0

    if meta:

        meta = atualizar_meta_leitura(current_user)

        if meta.quantidade > 0:

            percentual_meta = round(
                (meta.progresso / meta.quantidade) * 100
            )

        if percentual_meta > 100:
            percentual_meta = 100

        livros_restantes = max(
            meta.quantidade - meta.progresso,
            0
        )

        db.session.commit()
    # ======================================
    # MINHA COLEÇÃO
    # ======================================

    colecao = UsuarioColecionavel.query.filter_by(
        usuario_id=current_user.id
    ).order_by(
        UsuarioColecionavel.data_aquisicao.desc()
    ).limit(4).all()
    # ======================================
    # ENVIAR DADOS PARA O PERFIL
    # ======================================

    return render_template(
        "user/perfil.html",
        livros_lidos=livros_lidos,
        livros_lendo=livros_lendo,
        quero_ler=quero_ler,
        total_livros=total_livros,
        insignias=insignias,
        meta=meta,
        percentual_meta=percentual_meta,
        livros_restantes=livros_restantes,
        atividades=atividades,
        colecao=colecao
    )

@user_bp.route("/meta", methods=["POST"])
@login_required
def definir_meta():

    from datetime import date

    quantidade = request.form.get(
        "quantidade",
        type=int
    )

    if not quantidade or quantidade < 1:

        flash(
            "Digite uma quantidade válida de livros.",
            "danger"
        )

        return redirect(
            url_for("user_bp.perfil")
        )

    hoje = date.today()

    meta = MetaLeitura.query.filter_by(
        usuario_id=current_user.id,
        mes=hoje.month,
        ano=hoje.year
    ).order_by(
        MetaLeitura.id.desc()
    ).first()

    # Se já existe uma meta
    if meta:

        # Se a meta foi concluída,
        # cria uma nova meta
        if meta.concluida:

            nova_meta = MetaLeitura(
                usuario_id=current_user.id,
                quantidade=quantidade,
                progresso=0,
                mes=hoje.month,
                ano=hoje.year,
                data_inicio=hoje,
                concluida=False,
                recompensa_recebida=False
            )

            db.session.add(nova_meta)

        else:

            # Meta ainda não concluída:
            # apenas altera a quantidade
            meta.quantidade = quantidade

    else:

        # Primeira meta do mês
        meta = MetaLeitura(
            usuario_id=current_user.id,
            quantidade=quantidade,
            progresso=0,
            mes=hoje.month,
            ano=hoje.year,
            data_inicio=hoje,
            concluida=False,
            recompensa_recebida=False
        )

        db.session.add(meta)

    db.session.commit()

    flash(
        f"Meta de {quantidade} livros definida!",
        "success"
    )

    return redirect(
        url_for("user_bp.perfil")
    )