from extensions import db
from models import Insignia, UsuarioInsignia, Estante
from flask import flash


INSIGNIAS = [

    {
        "nome": "Primeiro Livro",
        "descricao": "Adicionar o primeiro livro à estante.",
        "emoji": "🥉"
    },

    {
        "nome": "Primeira Resenha",
        "descricao": "Publicar a primeira resenha.",
        "emoji": "🥉"
    },

    {
        "nome": "Primeira Avaliação",
        "descricao": "Avaliar o primeiro livro.",
        "emoji": "🥉"
    },

    {
        "nome": "5 Livros",
        "descricao": "Concluir cinco livros.",
        "emoji": "📚"
    },

    {
        "nome": "10 Livros",
        "descricao": "Concluir dez livros.",
        "emoji": "📚"
    },

    {
        "nome": "25 Livros",
        "descricao": "Concluir vinte e cinco livros.",
        "emoji": "🥇"
    },

    {
        "nome": "50 Livros",
        "descricao": "Concluir cinquenta livros.",
        "emoji": "🏆"
    },

    {
        "nome": "100 Livros",
        "descricao": "Concluir cem livros.",
        "emoji": "👑"
    }

]



def criar_insignias():

    for item in INSIGNIAS:

        existe = Insignia.query.filter_by(
            nome=item["nome"]
        ).first()


        if not existe:

            insignia = Insignia(
                nome=item["nome"],
                descricao=item["descricao"],
                emoji=item["emoji"]
            )

            db.session.add(insignia)


    db.session.commit()




def desbloquear_insignia(usuario, nome):


    insignia = Insignia.query.filter_by(
        nome=nome
    ).first()


    if not insignia:
        return



    possui = UsuarioInsignia.query.filter_by(
        usuario_id=usuario.id,
        insignia_id=insignia.id
    ).first()


    if possui:
        return



    nova = UsuarioInsignia(
        usuario_id=usuario.id,
        insignia_id=insignia.id
    )


    db.session.add(nova)

    db.session.commit()

    flash(f"🏅 Nova insígnia conquistada: {insignia.emoji} {insignia.nome}!",
    "success")



def verificar_insignias(usuario):


    livros_lidos = Estante.query.filter_by(
        usuario_id=usuario.id,
        status="lido"
    ).count()


    total_livros = Estante.query.filter_by(
        usuario_id=usuario.id
    ).count()

    resenhas = Estante.query.filter(
    Estante.usuario_id == usuario.id,
    Estante.resenha != ""
    ).count()


    if resenhas >= 1:

        desbloquear_insignia(
            usuario,
            "Primeira Resenha"
        )

    avaliacoes = Estante.query.filter(
    Estante.usuario_id == usuario.id,
    Estante.nota != None
    ).count()


    if avaliacoes >= 1:

        desbloquear_insignia(
            usuario,
            "Primeira Avaliação"
        )



    # Primeiro livro

    if total_livros >= 1:
        desbloquear_insignia(
            usuario,
            "Primeiro Livro"
        )



    # Quantidade de livros


    if livros_lidos >= 5:
        desbloquear_insignia(
            usuario,
            "5 Livros"
        )


    if livros_lidos >= 10:
        desbloquear_insignia(
            usuario,
            "10 Livros"
        )


    if livros_lidos >= 25:
        desbloquear_insignia(
            usuario,
            "25 Livros"
        )


    if livros_lidos >= 50:
        desbloquear_insignia(
            usuario,
            "50 Livros"
        )


    if livros_lidos >= 100:
        desbloquear_insignia(
            usuario,
            "100 Livros"
        )
