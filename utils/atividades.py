from extensions import db
from models import Atividade


def registrar_atividade(
    usuario,
    tipo,
    mensagem,
    livro=None
):

    atividade = Atividade(
        usuario_id=usuario.id,
        livro_id=livro.id if livro else None,
        tipo=tipo,
        mensagem=mensagem
    )

    db.session.add(atividade)