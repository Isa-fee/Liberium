import json

from extensions import db
from models import Livro, ItemColecionavel



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
        )

        db.session.add(livro)

    db.session.commit()

    print("Livros importados com sucesso!")



def popular_colecionaveis():

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