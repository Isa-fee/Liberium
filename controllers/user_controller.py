import os
import uuid

from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
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

@user_bp.route("/configuracoes", methods=["GET", "POST"])
@login_required
def configuracoes():

    if request.method == "POST":

        nome = request.form.get("nome", "").strip()
        email = request.form.get("email", "").strip().lower()

        senha_atual = request.form.get("senha_atual", "")
        nova_senha = request.form.get("nova_senha", "")
        confirmar_senha = request.form.get("confirmar_senha", "")

        # Validar nome
        if not nome:
            flash("O nome não pode ficar vazio.", "danger")
            return redirect(url_for("user_bp.configuracoes"))

        # Validar e-mail
        if not email:
            flash("O e-mail não pode ficar vazio.", "danger")
            return redirect(url_for("user_bp.configuracoes"))

        usuario_existente = Usuario.query.filter(
            Usuario.email == email,
            Usuario.id != current_user.id
        ).first()

        if usuario_existente:
            flash(
                "Este e-mail já está sendo usado por outro usuário.",
                "danger"
            )
            return redirect(url_for("user_bp.configuracoes"))

        # Alterar senha
        quer_alterar_senha = (
            senha_atual or nova_senha or confirmar_senha
        )

        if quer_alterar_senha:

            if not senha_atual:
                flash(
                    "Digite sua senha atual para alterar a senha.",
                    "danger"
                )
                return redirect(url_for("user_bp.configuracoes"))

            if not check_password_hash(
                current_user.senha,
                senha_atual
            ):
                flash(
                    "A senha atual está incorreta.",
                    "danger"
                )
                return redirect(url_for("user_bp.configuracoes"))

            if not nova_senha:
                flash(
                    "Digite uma nova senha.",
                    "danger"
                )
                return redirect(url_for("user_bp.configuracoes"))

            if nova_senha != confirmar_senha:
                flash(
                    "As novas senhas não coincidem.",
                    "danger"
                )
                return redirect(url_for("user_bp.configuracoes"))

            if len(nova_senha) < 6:
                flash(
                    "A nova senha deve ter pelo menos 6 caracteres.",
                    "danger"
                )
                return redirect(url_for("user_bp.configuracoes"))

            current_user.senha = generate_password_hash(nova_senha)

        # Atualizar nome e e-mail
        current_user.nome = nome
        current_user.email = email

        # Alterar foto
        foto = request.files.get("foto")

        if foto and foto.filename:

            extensoes_permitidas = {
                "jpg",
                "jpeg",
                "png",
                "webp"
            }

            nome_original = secure_filename(foto.filename)

            extensao = nome_original.rsplit(
                ".",
                1
            )[-1].lower()

            if extensao not in extensoes_permitidas:
                flash(
                    "Formato de imagem inválido. "
                    "Use JPG, JPEG, PNG ou WEBP.",
                    "danger"
                )
                return redirect(url_for("user_bp.configuracoes"))

            pasta_perfis = os.path.join(
                current_app.static_folder,
                "img",
                "perfis"
            )

            os.makedirs(
                pasta_perfis,
                exist_ok=True
            )

            novo_nome = f"{uuid.uuid4().hex}.{extensao}"

            caminho_arquivo = os.path.join(
                pasta_perfis,
                novo_nome
            )

            foto.save(caminho_arquivo)

            # Apagar foto anterior
            if current_user.foto:

                foto_anterior = os.path.join(
                    current_app.static_folder,
                    current_user.foto
                )

                if (
                    os.path.isfile(foto_anterior)
                    and current_user.foto.startswith("img/perfis/")
                ):
                    os.remove(foto_anterior)

            current_user.foto = f"img/perfis/{novo_nome}"

        db.session.commit()

        flash(
            "Perfil atualizado com sucesso!",
            "success"
        )

        return redirect(
            url_for("user_bp.configuracoes")
        )

    return render_template(
        "user/configuracoes.html"
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