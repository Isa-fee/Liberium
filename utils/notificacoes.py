from extensions import db
from models import Notificacao


def criar_notificacao(
    usuario_id,
    categoria,
    tipo,
    titulo,
    mensagem,
    link=None
):
    notificacao = Notificacao(
        usuario_id=usuario_id,
        categoria=categoria,
        tipo=tipo,
        titulo=titulo,
        mensagem=mensagem,
        link=link,
        lida=False
    )

    db.session.add(notificacao)
    db.session.commit()

    return notificacao