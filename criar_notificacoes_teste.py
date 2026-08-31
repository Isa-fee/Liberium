from app import create_app
from extensions import db
from models import Notificacao, Usuario
from datetime import datetime, timedelta


app = create_app()


with app.app_context():

    # IMPORTANTE:
    # coloque aqui o ID do usuário que você está usando.
    # Pelo seu erro anterior, parece ser o 6.
    usuario_id = 6

    usuario = Usuario.query.get(usuario_id)

    if not usuario:
        print("Usuário não encontrado!")
        exit()

    notificacoes = [

        Notificacao(
            usuario_id=usuario.id,
            categoria="social",
            tipo="solicitacao_amizade",
            titulo="Nova solicitação de amizade",
            mensagem="Beatriz enviou uma solicitação de amizade para você.",
            link="/amigos",
            lida=False,
            data_criacao=datetime.utcnow()
        ),

        Notificacao(
            usuario_id=usuario.id,
            categoria="livros",
            tipo="livro_disponivel",
            titulo="Livro disponível no catálogo!",
            mensagem=(
                "O livro que você solicitou, Extraordinário, "
                "foi adicionado ao catálogo do Liberium."
            ),
            link="/books",
            lida=False,
            data_criacao=datetime.utcnow() - timedelta(hours=2)
        ),

        Notificacao(
            usuario_id=usuario.id,
            categoria="clubes",
            tipo="convite_clube",
            titulo="Convite para clube de leitura",
            mensagem=(
                "Você recebeu um convite para participar "
                "do clube Páginas Noturnas."
            ),
            link="/clubes",
            lida=False,
            data_criacao=datetime.utcnow() - timedelta(days=1)
        ),

        Notificacao(
            usuario_id=usuario.id,
            categoria="social",
            tipo="amizade_aceita",
            titulo="Solicitação de amizade aceita!",
            mensagem="Lucas aceitou sua solicitação de amizade.",
            link="/amigos",
            lida=True,
            data_criacao=datetime.utcnow() - timedelta(days=3)
        ),

        Notificacao(
            usuario_id=usuario.id,
            categoria="conquistas",
            tipo="nova_insignia",
            titulo="Nova insígnia conquistada!",
            mensagem=(
                "Parabéns! Você conquistou a insígnia "
                "Explorador de Mundos."
            ),
            link="/perfil",
            lida=True,
            data_criacao=datetime.utcnow() - timedelta(days=5)
        )

    ]

    db.session.add_all(notificacoes)
    db.session.commit()

    print("Notificações de teste criadas!")