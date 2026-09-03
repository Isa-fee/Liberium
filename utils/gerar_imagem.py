import os
import textwrap
from io import BytesIO

import requests

from PIL import (
    Image,
    ImageDraw,
    ImageFont,
    ImageFilter
)


# =========================================================
# CONFIGURAÇÕES
# =========================================================

LARGURA = 1080
ALTURA = 1920


# =========================================================
# CORES DO LIBERIUM
# =========================================================

FUNDO = "#FDFCFB"

VERDE = "#879D84"
VERDE_ESCURO = "#435342"
VERDE_CLARO = "#E8EEE6"

MARROM = "#442B1A"
MARROM_CLARO = "#765C4A"

BEGE = "#F3EEE7"
BEGE_ESCURO = "#E5D9CC"

BRANCO = "#FFFFFF"
CINZA = "#8C8178"


# =========================================================
# CAMINHOS
# =========================================================

BASE_DIR = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        ".."
    )
)

STATIC_DIR = os.path.join(
    BASE_DIR,
    "static"
)

PASTA_COMPARTILHAMENTOS = os.path.join(
    STATIC_DIR,
    "img",
    "compartilhamentos"
)

os.makedirs(
    PASTA_COMPARTILHAMENTOS,
    exist_ok=True
)


# =========================================================
# FONTES
# =========================================================

def buscar_fonte(
    tamanho,
    negrito=False
):
    """
    Procura uma fonte disponível no Windows.
    Caso não encontre, usa a fonte padrão do Pillow.
    """

    fontes_normais = [
        "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/calibri.ttf",
        "C:/Windows/Fonts/segoeui.ttf",
    ]

    fontes_negrito = [
        "C:/Windows/Fonts/arialbd.ttf",
        "C:/Windows/Fonts/calibrib.ttf",
        "C:/Windows/Fonts/seguisb.ttf",
    ]

    lista = (
        fontes_negrito
        if negrito
        else fontes_normais
    )

    for caminho in lista:

        if os.path.exists(caminho):

            return ImageFont.truetype(
                caminho,
                tamanho
            )

    return ImageFont.load_default()


# =========================================================
# FONTES UTILIZADAS
# =========================================================

FONTE_LOGO = buscar_fonte(
    44,
    True
)

FONTE_SUBLOGO = buscar_fonte(
    23
)

FONTE_SECAO = buscar_fonte(
    27,
    True
)

FONTE_TITULO = buscar_fonte(
    58,
    True
)

FONTE_AUTOR = buscar_fonte(
    34
)

FONTE_NOTA = buscar_fonte(
    28,
    True
)

FONTE_NOME = buscar_fonte(
    34,
    True
)

FONTE_USERNAME = buscar_fonte(
    26
)

FONTE_FRASE = buscar_fonte(
    27
)

FONTE_RODAPE = buscar_fonte(
    22
)


# =========================================================
# TEXTO CENTRALIZADO
# =========================================================

def desenhar_texto_centralizado(
    draw,
    texto,
    y,
    fonte,
    cor,
    largura_maxima=850,
    espacamento=10
):

    palavras = texto.split()

    linhas = []

    linha_atual = ""

    for palavra in palavras:

        teste = (
            linha_atual + " " + palavra
        ).strip()

        caixa = draw.textbbox(
            (0, 0),
            teste,
            font=fonte
        )

        largura = (
            caixa[2] - caixa[0]
        )

        if largura <= largura_maxima:

            linha_atual = teste

        else:

            if linha_atual:
                linhas.append(
                    linha_atual
                )

            linha_atual = palavra

    if linha_atual:

        linhas.append(
            linha_atual
        )


    alturas = []

    for linha in linhas:

        caixa = draw.textbbox(
            (0, 0),
            linha,
            font=fonte
        )

        alturas.append(
            caixa[3] - caixa[1]
        )


    altura_total = (
        sum(alturas)
        +
        espacamento
        *
        max(
            len(linhas) - 1,
            0
        )
    )


    y_atual = y


    for indice, linha in enumerate(
        linhas
    ):

        caixa = draw.textbbox(
            (0, 0),
            linha,
            font=fonte
        )

        largura = (
            caixa[2] - caixa[0]
        )

        x = (
            LARGURA - largura
        ) // 2

        draw.text(
            (x, y_atual),
            linha,
            font=fonte,
            fill=cor
        )

        y_atual += (
            alturas[indice]
            +
            espacamento
        )


    return (
        y_atual,
        altura_total
    )


# =========================================================
# CARREGAR IMAGEM
# =========================================================

def carregar_imagem(
    caminho
):

    if not caminho:
        return None


    try:

        # =================================================
        # IMAGEM EXTERNA
        # =================================================

        if caminho.startswith(
            (
                "http://",
                "https://"
            )
        ):

            response = requests.get(
                caminho,
                timeout=10
            )

            response.raise_for_status()

            return Image.open(
                BytesIO(
                    response.content
                )
            ).convert("RGBA")


        # =================================================
        # IMAGEM LOCAL
        # =================================================

        caminho_limpo = caminho.replace(
            "\\",
            "/"
        )

        if caminho_limpo.startswith(
            "static/"
        ):

            caminho_completo = os.path.join(
                BASE_DIR,
                caminho_limpo
            )

        else:

            caminho_completo = os.path.join(
                STATIC_DIR,
                caminho_limpo
            )


        if os.path.exists(
            caminho_completo
        ):

            return Image.open(
                caminho_completo
            ).convert("RGBA")


    except Exception as erro:

        print(
            "Erro ao carregar imagem:",
            erro
        )


    return None


# =========================================================
# CORTAR IMAGEM PARA PREENCHER
# =========================================================

def cortar_para_preencher(
    imagem,
    largura,
    altura
):

    proporcao_imagem = (
        imagem.width
        /
        imagem.height
    )

    proporcao_destino = (
        largura
        /
        altura
    )


    if (
        proporcao_imagem
        >
        proporcao_destino
    ):

        nova_altura = altura

        nova_largura = int(
            altura
            *
            proporcao_imagem
        )

    else:

        nova_largura = largura

        nova_altura = int(
            largura
            /
            proporcao_imagem
        )


    imagem = imagem.resize(
        (
            nova_largura,
            nova_altura
        ),
        Image.Resampling.LANCZOS
    )


    esquerda = (
        nova_largura
        -
        largura
    ) // 2

    topo = (
        nova_altura
        -
        altura
    ) // 2


    return imagem.crop(
        (
            esquerda,
            topo,
            esquerda + largura,
            topo + altura
        )
    )


# =========================================================
# CÍRCULO COM FOTO
# =========================================================

def criar_avatar(
    foto,
    nome,
    tamanho=110
):

    avatar = Image.new(
        "RGBA",
        (
            tamanho,
            tamanho
        ),
        (
            0,
            0,
            0,
            0
        )
    )


    draw_avatar = ImageDraw.Draw(
        avatar
    )


    imagem_foto = carregar_imagem(
        foto
    )


    # =====================================================
    # FOTO EXISTE
    # =====================================================

    if imagem_foto:

        imagem_foto = cortar_para_preencher(
            imagem_foto,
            tamanho,
            tamanho
        )


        mascara = Image.new(
            "L",
            (
                tamanho,
                tamanho
            ),
            0
        )


        draw_mascara = ImageDraw.Draw(
            mascara
        )

        draw_mascara.ellipse(
            (
                0,
                0,
                tamanho,
                tamanho
            ),
            fill=255
        )


        avatar.paste(
            imagem_foto,
            (
                0,
                0
            ),
            mascara
        )


    # =====================================================
    # SEM FOTO
    # =====================================================

    else:

        draw_avatar.ellipse(
            (
                0,
                0,
                tamanho - 1,
                tamanho - 1
            ),
            fill=BEGE,
            outline=VERDE,
            width=4
        )


        inicial = (
            nome[0].upper()
            if nome
            else "L"
        )


        fonte_inicial = buscar_fonte(
            45,
            True
        )


        caixa = draw_avatar.textbbox(
            (
                0,
                0
            ),
            inicial,
            font=fonte_inicial
        )


        largura_texto = (
            caixa[2]
            -
            caixa[0]
        )

        altura_texto = (
            caixa[3]
            -
            caixa[1]
        )


        draw_avatar.text(
            (
                (
                    tamanho
                    -
                    largura_texto
                )
                // 2,

                (
                    tamanho
                    -
                    altura_texto
                )
                // 2
                -
                5
            ),
            inicial,
            font=fonte_inicial,
            fill=VERDE_ESCURO
        )


    # =====================================================
    # BORDA
    # =====================================================

    draw_avatar.ellipse(
        (
            1,
            1,
            tamanho - 2,
            tamanho - 2
        ),
        outline=VERDE,
        width=4
    )


    return avatar


# =========================================================
# DESENHAR ESTRELA
# =========================================================

def desenhar_estrela(
    draw,
    centro_x,
    centro_y,
    raio_externo,
    raio_interno,
    cor
):

    import math


    pontos = []


    for i in range(10):

        angulo = (
            -math.pi / 2
            +
            i
            *
            math.pi
            /
            5
        )


        raio = (
            raio_externo
            if i % 2 == 0
            else raio_interno
        )


        x = (
            centro_x
            +
            raio
            *
            math.cos(
                angulo
            )
        )


        y = (
            centro_y
            +
            raio
            *
            math.sin(
                angulo
            )
        )


        pontos.append(
            (
                x,
                y
            )
        )


    draw.polygon(
        pontos,
        fill=cor
    )


# =========================================================
# ESTRELAS DA AVALIAÇÃO
# =========================================================

def desenhar_avaliacao(
    draw,
    nota,
    y
):

    try:

        nota = float(
            nota or 0
        )

    except (
        TypeError,
        ValueError
    ):

        nota = 0


    nota = max(
        0,
        min(
            nota,
            5
        )
    )


    quantidade = 5

    tamanho = 30

    distancia = 68


    largura_total = (
        distancia
        *
        (
            quantidade - 1
        )
        +
        tamanho
        *
        2
    )


    inicio_x = (
        LARGURA
        -
        largura_total
    ) // 2


    for indice in range(
        quantidade
    ):

        centro_x = (
            inicio_x
            +
            tamanho
            +
            indice
            *
            distancia
        )


        cor = (
            VERDE_ESCURO
            if indice < round(nota)
            else BEGE_ESCURO
        )


        desenhar_estrela(
            draw,
            centro_x,
            y,
            tamanho,
            13,
            cor
        )


# =========================================================
# CARD DE LIVRO CONCLUÍDO
# =========================================================

def gerar_card_livro_concluido(
    livro,
    usuario,
    nota=None
):

    # =====================================================
    # IMAGEM BASE
    # =====================================================

    imagem = Image.new(
        "RGB",
        (
            LARGURA,
            ALTURA
        ),
        FUNDO
    )


    draw = ImageDraw.Draw(
        imagem
    )


    # =====================================================
    # DECORAÇÃO SUPERIOR
    # =====================================================

    draw.ellipse(
        (
            -180,
            -250,
            420,
            350
        ),
        fill="#F1F4EF"
    )


    draw.ellipse(
        (
            780,
            -180,
            1250,
            290
        ),
        fill="#F6F0E9"
    )


    # =====================================================
    # MARCA LIBERIUM
    # =====================================================

    draw.text(
        (
            90,
            95
        ),
        "LIBERIUM",
        font=FONTE_LOGO,
        fill=VERDE_ESCURO
    )


    draw.text(
        (
            92,
            150
        ),
        "sua jornada entre páginas",
        font=FONTE_SUBLOGO,
        fill=VERDE
    )


    # =====================================================
    # TEXTO SUPERIOR
    # =====================================================

    texto_topo = (
        "MINHA JORNADA LITERÁRIA"
    )


    caixa = draw.textbbox(
        (
            0,
            0
        ),
        texto_topo,
        font=FONTE_SECAO
    )


    largura_texto = (
        caixa[2]
        -
        caixa[0]
    )


    draw.text(
        (
            (
                LARGURA
                -
                largura_texto
            )
            // 2,
            255
        ),
        texto_topo,
        font=FONTE_SECAO,
        fill=VERDE
    )


    # =====================================================
    # CAPA DO LIVRO
    # =====================================================

    largura_capa = 480

    altura_capa = 690

    x_capa = (
        LARGURA
        -
        largura_capa
    ) // 2

    y_capa = 350


    # =====================================================
    # SOMBRA
    # =====================================================

    sombra = Image.new(
        "RGBA",
        (
            LARGURA,
            ALTURA
        ),
        (
            0,
            0,
            0,
            0
        )
    )


    draw_sombra = ImageDraw.Draw(
        sombra
    )


    draw_sombra.rounded_rectangle(
        (
            x_capa + 15,
            y_capa + 20,
            x_capa
            +
            largura_capa
            +
            15,
            y_capa
            +
            altura_capa
            +
            20
        ),
        radius=35,
        fill=(
            68,
            43,
            26,
            45
        )
    )


    sombra = sombra.filter(
        ImageFilter.GaussianBlur(
            18
        )
    )


    imagem = Image.alpha_composite(
        imagem.convert("RGBA"),
        sombra
    )


    draw = ImageDraw.Draw(
        imagem
    )


    # =====================================================
    # FUNDO DA CAPA
    # =====================================================

    margem_capa = 28


    draw.rounded_rectangle(
        (
            x_capa
            -
            margem_capa,
            y_capa
            -
            margem_capa,

            x_capa
            +
            largura_capa
            +
            margem_capa,

            y_capa
            +
            altura_capa
            +
            margem_capa
        ),
        radius=40,
        fill=BEGE
    )


    # =====================================================
    # CARREGAR CAPA
    # =====================================================

    capa = carregar_imagem(
        getattr(
            livro,
            "capa",
            None
        )
    )


    if capa:

        capa.thumbnail(
            (
                largura_capa,
                altura_capa
            ),
            Image.Resampling.LANCZOS
        )


        x_real = (
            LARGURA
            -
            capa.width
        ) // 2


        y_real = (
            y_capa
            +
            (
                altura_capa
                -
                capa.height
            )
            // 2
        )


        imagem.paste(
            capa,
            (
                x_real,
                y_real
            ),
            capa
        )


    else:

        draw.rounded_rectangle(
            (
                x_capa,
                y_capa,
                x_capa
                +
                largura_capa,
                y_capa
                +
                altura_capa
            ),
            radius=25,
            fill=VERDE_CLARO
        )


        desenhar_texto_centralizado(
            draw,
            "Livro",
            y_capa + 300,
            FONTE_TITULO,
            VERDE_ESCURO,
            largura_maxima=350
        )


    # =====================================================
    # LEITURA CONCLUÍDA
    # =====================================================

    y_status = (
        y_capa
        +
        altura_capa
        +
        100
    )


    status = (
        "LEITURA CONCLUÍDA"
    )


    caixa = draw.textbbox(
        (
            0,
            0
        ),
        status,
        font=FONTE_SECAO
    )


    largura_status = (
        caixa[2]
        -
        caixa[0]
    )


    draw.text(
        (
            (
                LARGURA
                -
                largura_status
            )
            // 2,
            y_status
        ),
        status,
        font=FONTE_SECAO,
        fill=VERDE
    )


    # =====================================================
    # TÍTULO
    # =====================================================

    titulo = getattr(
        livro,
        "titulo",
        "Livro concluído"
    )


    y_titulo = (
        y_status
        +
        70
    )


    y_depois_titulo, _ = (
        desenhar_texto_centralizado(
            draw,
            titulo,
            y_titulo,
            FONTE_TITULO,
            MARROM,
            largura_maxima=850,
            espacamento=8
        )
    )


    # =====================================================
    # AUTOR
    # =====================================================

    autor = getattr(
        livro,
        "autor",
        ""
    )


    if autor:

        y_autor = (
            y_depois_titulo
            +
            25
        )


        caixa = draw.textbbox(
            (
                0,
                0
            ),
            autor,
            font=FONTE_AUTOR
        )


        largura_autor = (
            caixa[2]
            -
            caixa[0]
        )


        draw.text(
            (
                (
                    LARGURA
                    -
                    largura_autor
                )
                // 2,
                y_autor
            ),
            autor,
            font=FONTE_AUTOR,
            fill=VERDE_ESCURO
        )


    else:

        y_autor = (
            y_depois_titulo
        )


    # =====================================================
    # AVALIAÇÃO
    # =====================================================

    if nota:

        y_estrelas = (
            y_autor
            +
            100
        )


        desenhar_avaliacao(
            draw,
            nota,
            y_estrelas
        )


    # =====================================================
    # CARD DO USUÁRIO
    # =====================================================

    card_x = 90

    card_y = 1570

    card_largura = 900

    card_altura = 220


    draw.rounded_rectangle(
        (
            card_x,
            card_y,
            card_x
            +
            card_largura,
            card_y
            +
            card_altura
        ),
        radius=38,
        fill=BEGE
    )


    # =====================================================
    # AVATAR
    # =====================================================

    nome_usuario = getattr(
        usuario,
        "nome",
        "Leitor"
    )


    foto_usuario = getattr(
        usuario,
        "foto",
        None
    )


    avatar = criar_avatar(
        foto_usuario,
        nome_usuario,
        115
    )


    imagem.paste(
        avatar,
        (
            card_x + 45,
            card_y + 45
        ),
        avatar
    )


    # =====================================================
    # NOME
    # =====================================================

    draw.text(
        (
            card_x + 190,
            card_y + 50
        ),
        nome_usuario,
        font=FONTE_NOME,
        fill=MARROM
    )


    # =====================================================
    # USERNAME
    # =====================================================

    username = getattr(
        usuario,
        "username",
        None
    )


    if username:

        username_texto = (
            f"@{username}"
        )

    else:

        username_texto = (
            "@leitor"
        )


    draw.text(
        (
            card_x + 190,
            card_y + 100
        ),
        username_texto,
        font=FONTE_USERNAME,
        fill=VERDE
    )


    # =====================================================
    # FRASE
    # =====================================================

    frase = (
        "Mais uma história para a minha estante."
    )


    draw.text(
        (
            card_x + 190,
            card_y + 150
        ),
        frase,
        font=FONTE_FRASE,
        fill=MARROM_CLARO
    )


    # =====================================================
    # RODAPÉ
    # =====================================================

    texto_rodape = (
        "Compartilhado pelo Liberium"
    )


    caixa = draw.textbbox(
        (
            0,
            0
        ),
        texto_rodape,
        font=FONTE_RODAPE
    )


    largura_rodape = (
        caixa[2]
        -
        caixa[0]
    )


    draw.text(
        (
            (
                LARGURA
                -
                largura_rodape
            )
            // 2,
            1840
        ),
        texto_rodape,
        font=FONTE_RODAPE,
        fill=VERDE
    )


    # =====================================================
    # SALVAR
    # =====================================================

    livro_id = getattr(
        livro,
        "id",
        "livro"
    )


    usuario_id = getattr(
        usuario,
        "id",
        "usuario"
    )


    nome_arquivo = (
        f"livro_{livro_id}_"
        f"usuario_{usuario_id}.png"
    )


    caminho_saida = os.path.join(
        PASTA_COMPARTILHAMENTOS,
        nome_arquivo
    )


    imagem.convert(
        "RGB"
    ).save(
        caminho_saida,
        "PNG",
        quality=95
    )


    return caminho_saida