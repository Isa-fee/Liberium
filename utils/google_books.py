import os
import requests
from bs4 import BeautifulSoup

def normalizar_capa(imagens, google_id=None):

    capa = (
        imagens.get("extraLarge")
        or imagens.get("large")
        or imagens.get("medium")
        or imagens.get("small")
        or imagens.get("thumbnail")
        or imagens.get("smallThumbnail")
    )

    if capa:
        capa = capa.replace("http://", "https://")

        # Algumas URLs publisher vêm codificadas incorretamente
        if "content%3Fid=" not in capa:
            return capa

    # Fallback usando diretamente o ID do Google Books
    if google_id:
        return (
            "https://books.google.com/books/content"
            f"?id={google_id}"
            "&printsec=frontcover"
            "&img=1"
            "&zoom=2"
            "&source=gbs_api"
        )

    return None

def buscar_google_books(
    termo,
    start_index=0,
    max_results=20,
    idioma=None
):

    url = (
        "https://www.googleapis.com/"
        "books/v1/volumes"
    )

    parametros = {
        "q": termo,
        "maxResults": max_results,
        "startIndex": start_index,
        "printType": "books"
    }

    # ==================================
    # FILTRO DE IDIOMA
    # ==================================

    if idioma:
        parametros["langRestrict"] = idioma

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

            "id": None,

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
            ).get_text(
                " ",
                strip=True
            ),

           "capa": normalizar_capa(
                imagens,
                item.get("id")
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
        print("===================================")
        print("LIVRO:", livro["titulo"])
        print("CAPA:", livro["capa"])
        print("===================================")

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

        "capa": normalizar_capa(
            imagens,
            item.get("id")
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