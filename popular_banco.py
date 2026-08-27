import json
import os

from extensions import db
from models import Livro, ItemColecionavel, Usuario, Amizade

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
# USUÁRIOS DE TESTE
# ==========================================

def popular_usuarios_teste():

    # Não cria novamente se já existirem usuários
    if Usuario.query.first():
        print("Usuários já estão cadastrados.")
        return

    usuarios = [

        Usuario(
            nome="Maria Oliveira",
            email="maria@teste.com",
            senha=generate_password_hash("123456"),
            foto="img/perfil_padrao.png",
            xp=320,
            nivel="Leitor Curioso",
            libelulas=18
        ),

        Usuario(
            nome="João Silva",
            email="joao@teste.com",
            senha=generate_password_hash("123456"),
            foto="img/perfil_padrao.png",
            xp=580,
            nivel="Explorador Literário",
            libelulas=32
        ),

        Usuario(
            nome="Ana Souza",
            email="ana@teste.com",
            senha=generate_password_hash("123456"),
            foto="img/perfil_padrao.png",
            xp=120,
            nivel="Leitor Iniciante",
            libelulas=10
        ),

        Usuario(
            nome="Lucas Santos",
            email="lucas@teste.com",
            senha=generate_password_hash("123456"),
            foto="img/perfil_padrao.png",
            xp=1050,
            nivel="Devorador de Livros",
            libelulas=45
        )
    ]

    db.session.add_all(usuarios)
    db.session.commit()

    print("Usuários de teste criados com sucesso!")

# ==========================================
# AMIZADES DE TESTE
# ==========================================

def popular_amizades_teste():

    # Evita duplicar amizades
    if Amizade.query.first():
        print("Amizades de teste já estão cadastradas.")
        return

    maria = Usuario.query.filter_by(
        email="maria@teste.com"
    ).first()

    joao = Usuario.query.filter_by(
        email="joao@teste.com"
    ).first()

    ana = Usuario.query.filter_by(
        email="ana@teste.com"
    ).first()

    lucas = Usuario.query.filter_by(
        email="lucas@teste.com"
    ).first()

    if not all([maria, joao, ana, lucas]):
        print("Usuários de teste não encontrados.")
        return

    # Maria e João são amigos
    amizade1 = Amizade(
        usuario_id=maria.id,
        amigo_id=joao.id,
        status="aceita"
    )

    # Maria recebeu solicitação da Ana
    amizade2 = Amizade(
        usuario_id=ana.id,
        amigo_id=maria.id,
        status="pendente"
    )

    # João enviou solicitação para Lucas
    amizade3 = Amizade(
        usuario_id=joao.id,
        amigo_id=lucas.id,
        status="pendente"
    )

    db.session.add_all([
        amizade1,
        amizade2,
        amizade3
    ])

    db.session.commit()

    print("Amizades de teste criadas com sucesso!")

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

    # Verifica se o administrador
    # foi configurado no .env
    if not email or not senha:

        print(
            "Administrador não configurado no .env."
        )

        return

    email = email.strip().lower()

    # Procura uma conta com esse e-mail
    usuario = Usuario.query.filter_by(
        email=email
    ).first()
    # ======================================
    # CONTA JÁ EXISTE
    # ======================================

    if usuario:

        if usuario.tipo != "administrador":

            usuario.tipo = "administrador"

            db.session.commit()

            print(
                f"{usuario.nome} agora é administrador(a)."
            )

        else:

            print(
                f"Administrador {usuario.nome} já está cadastrado."
            )

        return
    # ======================================
    # CONTA NÃO EXISTE
    # ======================================
    administrador = Usuario(
        nome=nome,
        email=email,
        senha=generate_password_hash(senha),
        tipo="administrador"
    )

    db.session.add(administrador)

    db.session.commit()

    print(
        f"Administrador {nome} criado com sucesso!"
    )