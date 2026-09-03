import os
import uuid
import re

from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from flask_login import login_user, logout_user, login_required, current_user

from extensions import db
from models import (
    Usuario,
    Estante,
    ComentarioResenha,
    UsuarioInsignia,
    UsuarioColecionavel,
    DecoracaoEstante,
    MetaLeitura,
    Atividade,
    Amizade,
    Clube,
    MembroClube,
    ConviteClube,
    Discussao,
    ElogioEstante,
    SolicitacaoLivro,
    Notificacao,
    Anotacao
)
from utils.insignias import verificar_insignias
from utils.gamificacao import atualizar_meta_leitura

user_bp = Blueprint("user_bp", __name__, url_prefix="/user")


@user_bp.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        nome = request.form.get(
            "nome",
            ""
        ).strip()

        username = request.form.get(
            "username",
            ""
        ).strip().lower()

        email = request.form.get(
            "email",
            ""
        ).strip().lower()

        senha = request.form.get(
            "senha",
            ""
        )

        confirmar_senha = request.form.get(
            "confirmar_senha",
            ""
        )

        tipo = request.form.get(
            "tipo",
            "leitor"
        )

        # ==================================
        # VALIDAR TIPO DE USUÁRIO
        # ==================================

        tipos_permitidos = [
            "leitor",
            "autor"
        ]

        if tipo not in tipos_permitidos:
            tipo = "leitor"

        # ==================================
        # VALIDAR CAMPOS OBRIGATÓRIOS
        # ==================================

        if (
            not nome
            or not username
            or not email
            or not senha
        ):

            flash(
                "Preencha todos os campos obrigatórios.",
                "danger"
            )

            return redirect(
                url_for("user_bp.register")
            )

        # ==================================
        # VALIDAR USERNAME
        # ==================================

        if len(username) < 3 or len(username) > 30:

            flash(
                "O @ deve ter entre 3 e 30 caracteres.",
                "danger"
            )

            return redirect(
                url_for("user_bp.register")
            )

        if not re.fullmatch(
            r"[a-z0-9._]+",
            username
        ):

            flash(
                "O @ pode conter apenas letras, números, "
                "ponto e underline.",
                "danger"
            )

            return redirect(
                url_for("user_bp.register")
            )

        # ==================================
        # VERIFICAR USERNAME
        # ==================================

        username_existente = Usuario.query.filter_by(
            username=username
        ).first()

        if username_existente:

            flash(
                "Este @ já está sendo usado.",
                "danger"
            )

            return redirect(
                url_for("user_bp.register")
            )

        # ==================================
        # CONFIRMAR SENHA
        # ==================================

        if senha != confirmar_senha:

            flash(
                "As senhas não coincidem!",
                "danger"
            )

            return redirect(
                url_for("user_bp.register")
            )

        # ==================================
        # VERIFICAR E-MAIL
        # ==================================

        usuario_existente = Usuario.query.filter_by(
            email=email
        ).first()

        if usuario_existente:

            flash(
                "E-mail já cadastrado!",
                "danger"
            )

            return redirect(
                url_for("user_bp.register")
            )

        # ==================================
        # CRIAR USUÁRIO
        # ==================================

        novo_usuario = Usuario(
            nome=nome,
            username=username,
            email=email,
            senha=generate_password_hash(senha),
            tipo=tipo
        )

        db.session.add(
            novo_usuario
        )

        db.session.commit()

        verificar_insignias(
            novo_usuario
        )

        flash(
            "Cadastro realizado com sucesso!",
            "success"
        )

        return redirect(
            url_for("user_bp.login")
        )

    return render_template(
        "user/register.html"
    )


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
        colecao=colecao,
        hoje=hoje
)

@user_bp.route("/configuracoes", methods=["GET", "POST"])
@login_required
def configuracoes():

    if request.method == "POST":

        nome = request.form.get("nome", "").strip()
        username = request.form.get("username", "").strip().lower()
        email = request.form.get("email", "").strip().lower()

        senha_atual = request.form.get("senha_atual", "")
        nova_senha = request.form.get("nova_senha", "")
        confirmar_senha = request.form.get("confirmar_senha", "")

        # Validar nome
        if not nome:
            flash("O nome não pode ficar vazio.", "danger")
            return redirect(url_for("user_bp.configuracoes"))
        if not username:
            flash(
                "O nome de usuário não pode ficar vazio.",
                "danger"
            )

            return redirect(
                url_for("user_bp.configuracoes")
            )


        if len(username) < 3 or len(username) > 30:

            flash(
                "O @ deve ter entre 3 e 30 caracteres.",
                "danger"
            )

            return redirect(
                url_for("user_bp.configuracoes")
            )


        if not re.fullmatch(
            r"[a-z0-9._]+",
            username
        ):

            flash(
                "O @ pode conter apenas letras, números, "
                "ponto e underline.",
                "danger"
            )

            return redirect(
                url_for("user_bp.configuracoes")
            )


        username_existente = Usuario.query.filter(
            Usuario.username == username,
            Usuario.id != current_user.id
        ).first()


        if username_existente:

            flash(
                "Este @ já está sendo usado por outro usuário.",
                "danger"
            )

            return redirect(
                url_for("user_bp.configuracoes")
            )

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

            if len(nova_senha) < 3:
                flash(
                    "A nova senha deve ter pelo menos 3 caracteres.",
                    "danger"
                )
                return redirect(url_for("user_bp.configuracoes"))

            current_user.senha = generate_password_hash(nova_senha)

        # Atualizar dados pessoais
        current_user.nome = nome
        current_user.username = username
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

@user_bp.route("/excluir-conta", methods=["POST"])
@login_required
def excluir_conta():

    usuario_id = current_user.id

    # =====================================================
    # CONFIRMAÇÃO
    # =====================================================

    senha = request.form.get(
        "senha_exclusao",
        ""
    )

    if not senha:

        flash(
            "Digite sua senha para confirmar a exclusão da conta.",
            "danger"
        )

        return redirect(
            url_for("user_bp.configuracoes")
        )

    if not check_password_hash(
        current_user.senha,
        senha
    ):

        flash(
            "Senha incorreta. A conta não foi excluída.",
            "danger"
        )

        return redirect(
            url_for("user_bp.configuracoes")
        )

    try:

        # =================================================
        # FOTO DO PERFIL
        # Guardamos o caminho para apagar depois.
        # =================================================

        foto_usuario = current_user.foto


        # =================================================
        # CLUBES CRIADOS PELO USUÁRIO
        # =================================================

        clubes_criados = Clube.query.filter_by(
            usuario_id=usuario_id
        ).all()

        for clube in clubes_criados:

            # Procura outro membro para assumir o clube.
            novo_criador = MembroClube.query.filter(
                MembroClube.clube_id == clube.id,
                MembroClube.usuario_id != usuario_id
            ).order_by(
                MembroClube.data_entrada.asc(),
                MembroClube.id.asc()
            ).first()

            if novo_criador:

                # -----------------------------------------
                # TRANSFERE O CLUBE
                # -----------------------------------------

                clube.usuario_id = novo_criador.usuario_id

            else:

                # -----------------------------------------
                # NINGUÉM MAIS ESTÁ NO CLUBE
                # EXCLUI TUDO RELACIONADO AO CLUBE
                # -----------------------------------------

                Anotacao.query.filter_by(
                    clube_id=clube.id
                ).update(
                    {
                        Anotacao.clube_id: None
                    },
                    synchronize_session=False
                )

                Discussao.query.filter_by(
                    clube_id=clube.id
                ).delete(
                    synchronize_session=False
                )

                ConviteClube.query.filter_by(
                    clube_id=clube.id
                ).delete(
                    synchronize_session=False
                )

                MembroClube.query.filter_by(
                    clube_id=clube.id
                ).delete(
                    synchronize_session=False
                )

                db.session.delete(clube)


        # =================================================
        # CONVITES DE CLUBES
        # =================================================

        ConviteClube.query.filter(
            db.or_(
                ConviteClube.remetente_id == usuario_id,
                ConviteClube.destinatario_id == usuario_id
            )
        ).delete(
            synchronize_session=False
        )


        # =================================================
        # MEMBRO DE CLUBES
        # =================================================

        MembroClube.query.filter_by(
            usuario_id=usuario_id
        ).delete(
            synchronize_session=False
        )


        # =================================================
        # DISCUSSÕES DO USUÁRIO
        # =================================================

        Discussao.query.filter_by(
            usuario_id=usuario_id
        ).delete(
            synchronize_session=False
        )


        # =================================================
        # ELOGIOS
        # =================================================

        ElogioEstante.query.filter(
            db.or_(
                ElogioEstante.autor_id == usuario_id,
                ElogioEstante.destinatario_id == usuario_id
            )
        ).delete(
            synchronize_session=False
        )


        # =================================================
        # AMIZADES
        # =================================================

        Amizade.query.filter(
            db.or_(
                Amizade.usuario_id == usuario_id,
                Amizade.amigo_id == usuario_id
            )
        ).delete(
            synchronize_session=False
        )


        # =================================================
        # ANOTAÇÕES
        # =================================================

        Anotacao.query.filter_by(
            usuario_id=usuario_id
        ).delete(
            synchronize_session=False
        )


        # =================================================
        # NOTIFICAÇÕES
        # =================================================

        Notificacao.query.filter_by(
            usuario_id=usuario_id
        ).delete(
            synchronize_session=False
        )


        # =================================================
        # SOLICITAÇÕES DE LIVROS
        # =================================================

        SolicitacaoLivro.query.filter_by(
            solicitante_id=usuario_id
        ).delete(
            synchronize_session=False
        )


        # =================================================
        # DECORAÇÕES
        # Deve vir antes da coleção.
        # =================================================

        DecoracaoEstante.query.filter_by(
            usuario_id=usuario_id
        ).delete(
            synchronize_session=False
        )


        # =================================================
        # COLEÇÃO
        # =================================================

        UsuarioColecionavel.query.filter_by(
            usuario_id=usuario_id
        ).delete(
            synchronize_session=False
        )


        # =================================================
        # INSÍGNIAS
        # =================================================

        UsuarioInsignia.query.filter_by(
            usuario_id=usuario_id
        ).delete(
            synchronize_session=False
        )


        # =================================================
        # METAS
        # =================================================

        MetaLeitura.query.filter_by(
            usuario_id=usuario_id
        ).delete(
            synchronize_session=False
        )


        # =================================================
        # ATIVIDADES
        # =================================================

        Atividade.query.filter_by(
            usuario_id=usuario_id
        ).delete(
            synchronize_session=False
        )


        # =================================================
        # COMENTÁRIOS EM RESENHAS
        # =================================================

        ComentarioResenha.query.filter_by(
            usuario_id=usuario_id
        ).delete(
            synchronize_session=False
        )


        # =================================================
        # ESTANTE
        # Comentários das próprias resenhas precisam sair
        # antes das entradas da estante.
        # =================================================

        estantes_usuario = Estante.query.filter_by(
            usuario_id=usuario_id
        ).all()

        ids_estantes = [
            item.id
            for item in estantes_usuario
        ]

        if ids_estantes:

            ComentarioResenha.query.filter(
                ComentarioResenha.estante_id.in_(
                    ids_estantes
                )
            ).delete(
                synchronize_session=False
            )

        Estante.query.filter_by(
            usuario_id=usuario_id
        ).delete(
            synchronize_session=False
        )


        # =================================================
        # USUÁRIO
        # =================================================

        usuario = db.session.get(
            Usuario,
            usuario_id
        )

        logout_user()

        db.session.delete(usuario)

        db.session.commit()


        # =================================================
        # APAGAR FOTO DO DISCO
        # =================================================

        if (
            foto_usuario
            and foto_usuario.startswith("img/perfis/")
        ):

            caminho_foto = os.path.join(
                current_app.static_folder,
                foto_usuario
            )

            if os.path.isfile(caminho_foto):

                try:
                    os.remove(caminho_foto)

                except OSError:
                    pass


        flash(
            "Sua conta foi excluída permanentemente.",
            "success"
        )

        return redirect(
            url_for("user_bp.login")
        )


    except Exception:

        db.session.rollback()

        current_app.logger.exception(
            "Erro ao excluir conta do usuário %s.",
            usuario_id
        )

        flash(
            "Não foi possível excluir sua conta. "
            "Tente novamente.",
            "danger"
        )

        return redirect(
            url_for("user_bp.configuracoes")
        )


@user_bp.route("/meta", methods=["POST"])
@login_required
def definir_meta():

    from datetime import date, timedelta
    import calendar

    quantidade = request.form.get(
        "quantidade",
        type=int
    )

    periodo = request.form.get("periodo")

    data_inicio_str = request.form.get("data_inicio")
    data_fim_str = request.form.get("data_fim")

    # ==========================================
    # VALIDA QUANTIDADE
    # ==========================================

    if not quantidade or quantidade < 1:

        flash(
            "Digite uma quantidade válida de livros.",
            "danger"
        )

        return redirect(
            url_for("user_bp.perfil")
        )

    # ==========================================
    # DATA DE INÍCIO
    # ==========================================

    hoje = date.today()

    if data_inicio_str:

        try:

            data_inicio = date.fromisoformat(
                data_inicio_str
            )

        except ValueError:

            flash(
                "Data de início inválida.",
                "danger"
            )

            return redirect(
                url_for("user_bp.perfil")
            )

    else:

        data_inicio = hoje

    # ==========================================
    # CALCULA DATA DE FIM
    # ==========================================

    if periodo == "1_mes":

        # Um mês a partir da data inicial
        mes = data_inicio.month + 1
        ano = data_inicio.year

        if mes > 12:
            mes = 1
            ano += 1

        ultimo_dia = calendar.monthrange(
            ano,
            mes
        )[1]

        dia = min(
            data_inicio.day,
            ultimo_dia
        )

        data_fim = date(
            ano,
            mes,
            dia
        ) - timedelta(days=1)

    elif periodo == "3_meses":

        mes = data_inicio.month + 3
        ano = data_inicio.year

        while mes > 12:
            mes -= 12
            ano += 1

        ultimo_dia = calendar.monthrange(
            ano,
            mes
        )[1]

        dia = min(
            data_inicio.day,
            ultimo_dia
        )

        data_fim = date(
            ano,
            mes,
            dia
        ) - timedelta(days=1)

    elif periodo == "6_meses":

        mes = data_inicio.month + 6
        ano = data_inicio.year

        while mes > 12:
            mes -= 12
            ano += 1

        ultimo_dia = calendar.monthrange(
            ano,
            mes
        )[1]

        dia = min(
            data_inicio.day,
            ultimo_dia
        )

        data_fim = date(
            ano,
            mes,
            dia
        ) - timedelta(days=1)

    elif periodo == "1_ano":

        try:

            data_fim = data_inicio.replace(
                year=data_inicio.year + 1
            ) - timedelta(days=1)

        except ValueError:

            # Caso seja 29 de fevereiro
            data_fim = data_inicio.replace(
                year=data_inicio.year + 1,
                day=28
            ) - timedelta(days=1)

    elif periodo == "personalizado":

        if not data_fim_str:

            flash(
                "Escolha uma data de término.",
                "danger"
            )

            return redirect(
                url_for("user_bp.perfil")
            )

        try:

            data_fim = date.fromisoformat(
                data_fim_str
            )

        except ValueError:

            flash(
                "Data de término inválida.",
                "danger"
            )

            return redirect(
                url_for("user_bp.perfil")
            )

    else:

        flash(
            "Escolha um período válido para sua meta.",
            "danger"
        )

        return redirect(
            url_for("user_bp.perfil")
        )

    # ==========================================
    # VALIDAÇÃO DO PERÍODO
    # ==========================================

    if data_fim < data_inicio:

        flash(
            "A data de término deve ser posterior à data de início.",
            "danger"
        )

        return redirect(
            url_for("user_bp.perfil")
        )

    # ==========================================
    # PROCURA META ATIVA
    # ==========================================

    meta = MetaLeitura.query.filter(
        MetaLeitura.usuario_id == current_user.id,
        MetaLeitura.data_inicio <= hoje,
        MetaLeitura.data_fim >= hoje
    ).order_by(
        MetaLeitura.id.desc()
    ).first()

    # ==========================================
    # SE JÁ EXISTE META
    # ==========================================

    if meta:

        # Se a meta foi concluída,
        # permite criar uma nova.
        if meta.concluida:

            nova_meta = MetaLeitura(
                usuario_id=current_user.id,
                quantidade=quantidade,
                progresso=0,
                mes=data_inicio.month,
                ano=data_inicio.year,
                data_inicio=data_inicio,
                data_fim=data_fim,
                concluida=False,
                recompensa_recebida=False
            )

            db.session.add(nova_meta)

        else:

            # Edita a meta atual
            meta.quantidade = quantidade
            meta.data_inicio = data_inicio
            meta.data_fim = data_fim
            meta.mes = data_inicio.month
            meta.ano = data_inicio.year

    # ==========================================
    # PRIMEIRA META
    # ==========================================

    else:

        nova_meta = MetaLeitura(
            usuario_id=current_user.id,
            quantidade=quantidade,
            progresso=0,
            mes=data_inicio.month,
            ano=data_inicio.year,
            data_inicio=data_inicio,
            data_fim=data_fim,
            concluida=False,
            recompensa_recebida=False
        )

        db.session.add(nova_meta)

    db.session.commit()

    flash(
        f"Meta de {quantidade} livros criada com sucesso!",
        "success"
    )

    return redirect(
        url_for("user_bp.perfil")
    )


@user_bp.route("/meta/excluir", methods=["POST"])
@login_required
def excluir_meta():

    from datetime import date

    hoje = date.today()

    meta = MetaLeitura.query.filter(
        MetaLeitura.usuario_id == current_user.id,
        MetaLeitura.data_inicio <= hoje,
        MetaLeitura.data_fim >= hoje
    ).order_by(
        MetaLeitura.id.desc()
    ).first()

    if not meta:

        flash(
            "Você não possui uma meta de leitura ativa.",
            "danger"
        )

        return redirect(
            url_for("user_bp.perfil")
        )

    db.session.delete(meta)

    db.session.commit()

    flash(
        "Meta de leitura excluída.",
        "success"
    )

    return redirect(
        url_for("user_bp.perfil")
    )