import json

from extensions import db
from models import Livro


def popular_banco():

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
            origem="banco"
        )

        db.session.add(livro)

    db.session.commit()

    print("Livros importados com sucesso!")