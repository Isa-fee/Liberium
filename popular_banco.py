import json

from app import create_app
from extensions import db
from models import Livro

app = create_app()

with app.app_context():

    with open(
        "data/livros.json",
        encoding="utf-8"
    ) as arquivo:

        livros = json.load(arquivo)

    for item in livros:

        existe = Livro.query.filter_by(
            titulo=item["titulo"]
        ).first()

        if existe:
            continue

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
            avaliacao=item["avaliacao"]
        )

        db.session.add(livro)

    db.session.commit()

    print("Livros importados com sucesso!")