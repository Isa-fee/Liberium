import json
import os

from extensions import db
from models import Livro, ItemColecionavel, Usuario

from werkzeug.security import generate_password_hash


def popular_banco():

    if Livro.query.first():
        print("Livros já estão cadastrados.")
        return

    with open(
        "data/livros.json",
        encoding="utf-8"
    ) as arquivo:

        livros = json.load(arquivo)

    for item in livros:

        livro = Livro(
            titulo=item["titulo"],
            autor=item["autor"],
            descricao=item["descricao"],
            capa=item["capa"],
            genero=item["genero"],
            editora=item["editora"],
            paginas=item["paginas"],
            ano=item["ano"],
            idioma=item["idioma"],
            avaliacao=item["avaliacao"],
        )

        db.session.add(livro)

    db.session.commit()

    print("Livros importados com sucesso!")



def popular_colecionaveis():

    if ItemColecionavel.query.first():
        print("Colecionáveis já estão cadastrados.")
        return

    with open(
        "data/colecionaveis.json",
        encoding="utf-8"
    ) as arquivo:

        itens = json.load(arquivo)

    for item in itens:

        colecionavel = ItemColecionavel(
            nome=item["nome"],
            descricao=item["descricao"],
            tipo=item["tipo"],
            preco=item["preco"],
            imagem=item["imagem"]
        )

        db.session.add(colecionavel)

    db.session.commit()

    print("Colecionáveis importados com sucesso!")



# ==========================================
# ADMINISTRADOR
# ==========================================

def criar_administrador():

    email = os.getenv("ADMIN_EMAIL")
    senha = os.getenv("ADMIN_PASSWORD")

    nome = os.getenv(
        "ADMIN_NOME",
        "Administrador"
    )

    username = os.getenv(
        "ADMIN_USERNAME",
        "admin"
    )

    # ======================================
    # VERIFICAR CONFIGURAÇÃO
    # ======================================

    if not email or not senha:

        print(
            "Administrador não configurado no .env."
        )

        return

    email = email.strip().lower()
    username = username.strip().lower()

    # ======================================
    # PROCURA CONTA PELO E-MAIL
    # ======================================

    usuario = Usuario.query.filter_by(
        email=email
    ).first()

    # ======================================
    # CONTA JÁ EXISTE
    # ======================================

    if usuario:

        alterado = False

        if usuario.tipo != "administrador":

            usuario.tipo = "administrador"
            alterado = True

        if not usuario.username:

            usuario.username = username
            alterado = True

        if alterado:

            db.session.commit()

            print(
                f"{usuario.nome} atualizado como administrador(a)."
            )

        else:

            print(
                f"Administrador {usuario.nome} já está cadastrado."
            )

        return

    # ======================================
    # VERIFICAR SE O USERNAME JÁ EXISTE
    # ======================================

    username_existente = Usuario.query.filter_by(
        username=username
    ).first()

    if username_existente:

        print(
            f"O username @{username} já está sendo utilizado."
        )

        return

    # ======================================
    # CRIAR ADMINISTRADOR
    # ======================================

    administrador = Usuario(
        nome=nome,
        username=username,
        email=email,
        senha=generate_password_hash(senha),
        tipo="administrador"
    )

    db.session.add(
        administrador
    )

    db.session.commit()

    print(
        f"Administrador {nome} (@{username}) criado com sucesso!"
    )