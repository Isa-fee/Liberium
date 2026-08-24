import os
import requests
from bs4 import BeautifulSoup


def buscar_google_books(termo):

    url = (
        "https://www.googleapis.com/"
        "books/v1/volumes"
    )

    parametros = {
        "q": termo,
        "maxResults": 20,
        "printType": "books"
    }

    # ==================================
    # CHAVE DA API
    # ==================================

    api_key = os.getenv(
        "GOOGLE_BOOKS_API_KEY"
    )

    if api_key:
        parametros["key"] = api_key

    # ==================================
    # FAZER REQUISIÇÃO
    # ==================================

    try:

        resposta = requests.get(
            url,
            params=parametros,
            timeout=5
        )

        resposta.raise_for_status()

        dados = resposta.json()

    except requests.RequestException as erro:

        print(
            "Erro ao acessar Google Books:",
            erro
        )

        return []

    # ==================================
    # ORGANIZAR RESULTADOS
    # ==================================

    livros = []

    for item in dados.get(
        "items",
        []
    ):

        info = item.get(
            "volumeInfo",
            {}
        )

        autores = info.get(
            "authors",
            []
        )

        categorias = info.get(
            "categories",
            []
        )

        imagens = info.get(
            "imageLinks",
            {}
        )

        livro = {

            "google_id": item.get(
                "id"
            ),

            "titulo": info.get(
                "title",
                "Título não informado"
            ),

            "autor": (
                ", ".join(autores)
                if autores
                else "Autor não informado"
            ),

           "descricao": BeautifulSoup(
                info.get(
                    "description",
                    "Sinopse não disponível."
                ),
                "html.parser"
            ).get_text(" ", strip=True),

            "capa": (
                imagens.get("thumbnail")
                or imagens.get("smallThumbnail")
            ),

            "genero": (
                categorias[0]
                if categorias
                else "Não informado"
            ),

            "editora": info.get(
                "publisher",
                "Não informada"
            ),

            "paginas": info.get(
                "pageCount"
            ),

            "ano": info.get(
                "publishedDate",
                "Não informado"
            ),

            "idioma": info.get(
                "language",
                "Não informado"
            ),

            "avaliacao": info.get(
                "averageRating"
            ),

            "origem": "google"
        }

        livros.append(
            livro
        )

    return livros

def buscar_livro_google(google_id):

    url = (
        "https://www.googleapis.com/"
        f"books/v1/volumes/{google_id}"
    )

    parametros = {}

    api_key = os.getenv(
        "GOOGLE_BOOKS_API_KEY"
    )

    if api_key:
        parametros["key"] = api_key

    try:

        resposta = requests.get(
            url,
            params=parametros,
            timeout=5
        )

        resposta.raise_for_status()

        item = resposta.json()

    except requests.RequestException as erro:

        print(
            "Erro ao buscar livro no Google:",
            erro
        )

        return None

    info = item.get(
        "volumeInfo",
        {}
    )

    autores = info.get(
        "authors",
        []
    )

    categorias = info.get(
        "categories",
        []
    )

    imagens = info.get(
        "imageLinks",
        {}
    )

    return {

        "google_id": item.get(
            "id"
        ),

        "titulo": info.get(
            "title",
            "Título não informado"
        ),

        "autor": (
            ", ".join(autores)
            if autores
            else "Autor não informado"
        ),

        "descricao": BeautifulSoup(
            info.get(
                "description",
                "Sinopse não disponível."
            ),
            "html.parser"
        ).get_text(" ", strip=True),

        "capa": (
            imagens.get("thumbnail")
            or imagens.get("smallThumbnail")
        ),

        "genero": (
            categorias[0]
            if categorias
            else "Não informado"
        ),

        "editora": info.get(
            "publisher",
            "Não informada"
        ),

        "paginas": info.get(
            "pageCount"
        ),

        "ano": info.get(
            "publishedDate",
            "Não informado"
        ),

        "idioma": info.get(
            "language",
            "Não informado"
        ),

        "avaliacao": info.get(
            "averageRating"
        ),

        "origem": "google"
    }