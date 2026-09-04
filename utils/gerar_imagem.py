import os
import io
import textwrap
import urllib.request

from PIL import (
    Image,
    ImageDraw,
    ImageFont,
    ImageFilter,
    ImageOps
)


# =========================================================
# CAMINHOS
# =========================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
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

PASTA_ELEMENTOS = os.path.join(
    PASTA_COMPARTILHAMENTOS,
    "elementos"
)

os.makedirs(
    PASTA_COMPARTILHAMENTOS,
    exist_ok=True
)


# =========================================================
# TAMANHO DO STORY
# =========================================================

LARGURA = 1080
ALTURA = 1920


# =========================================================
# CORES
# =========================================================

FUNDO = "#FBFCF3"

VERDE = "#82997D"
VERDE_ESCURO = "#64775B"
VERDE_CLARO = "#A8B9A1"

MARROM = "#71442D"
MARROM_ESCURO = "#583521"

BEGE = "#E8E5D7"

BRANCO = "#FFFFFF"
PRETO = "#252525"


# =========================================================
# FONTES
# =========================================================

PASTA_FONTES_WINDOWS = "C:/Windows/Fonts"


def encontrar_fonte(nomes):

    for nome in nomes:

        caminho = os.path.join(
            PASTA_FONTES_WINDOWS,
            nome
        )

        if os.path.exists(caminho):
            return caminho

    return None


FONTE_SERIF = encontrar_fonte([
    "georgia.ttf",
    "times.ttf"
])

FONTE_SERIF_BOLD = encontrar_fonte([
    "georgiab.ttf",
    "timesbd.ttf"
])

FONTE_SANS = encontrar_fonte([
    "arial.ttf",
    "calibri.ttf"
])

FONTE_SANS_BOLD = encontrar_fonte([
    "arialbd.ttf",
    "calibrib.ttf"
])


def fonte(caminho, tamanho):

    if caminho and os.path.exists(caminho):

        return ImageFont.truetype(
            caminho,
            tamanho
        )

    return ImageFont.load_default()


# =========================================================
# FUNÇÕES AUXILIARES
# =========================================================

def abrir_png(nome):

    caminho = os.path.join(
        PASTA_ELEMENTOS,
        nome
    )

    if not os.path.exists(caminho):
        return None

    return Image.open(
        caminho
    ).convert("RGBA")


def redimensionar_proporcional(
    imagem,
    largura=None,
    altura=None
):

    if not largura and not altura:
        return imagem

    proporcao = (
        imagem.width
        /
        imagem.height
    )

    if largura and not altura:

        altura = int(
            largura
            /
            proporcao
        )

    elif altura and not largura:

        largura = int(
            altura
            *
            proporcao
        )

    return imagem.resize(
        (
            int(largura),
            int(altura)
        ),
        Image.Resampling.LANCZOS
    )


def adicionar_elemento(
    base,
    nome,
    x,
    y,
    largura=None,
    altura=None,
    opacidade=255
):

    elemento = abrir_png(nome)

    if elemento is None:
        return

    elemento = redimensionar_proporcional(
        elemento,
        largura,
        altura
    )

    if opacidade < 255:

        alpha = elemento.getchannel("A")

        alpha = alpha.point(
            lambda p:
                int(
                    p
                    *
                    opacidade
                    /
                    255
                )
        )

        elemento.putalpha(alpha)

    base.alpha_composite(
        elemento,
        (
            int(x),
            int(y)
        )
    )


# =========================================================
# CARREGAR IMAGEM LOCAL OU URL
# =========================================================

def carregar_imagem(origem):

    if not origem:
        return None

    try:

        # -------------------------------------------------
        # URL
        # -------------------------------------------------

        if origem.startswith(
            ("http://", "https://")
        ):

            requisicao = urllib.request.Request(
                origem,
                headers={
                    "User-Agent": "Mozilla/5.0"
                }
            )

            with urllib.request.urlopen(
                requisicao,
                timeout=10
            ) as resposta:

                dados = resposta.read()

            return Image.open(
                io.BytesIO(dados)
            ).convert("RGBA")


        # -------------------------------------------------
        # ARQUIVO LOCAL
        # -------------------------------------------------

        caminho = origem.replace(
            "\\",
            "/"
        )

        if caminho.startswith("/static/"):
            caminho = caminho[8:]

        elif caminho.startswith("static/"):
            caminho = caminho[7:]

        caminho_completo = os.path.join(
            STATIC_DIR,
            caminho
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
# CROP PROPORCIONAL
# =========================================================

def ajustar_imagem_cover(
    imagem,
    largura,
    altura
):

    return ImageOps.fit(
        imagem,
        (
            largura,
            altura
        ),
        method=Image.Resampling.LANCZOS,
        centering=(0.5, 0.5)
    )


# =========================================================
# FOTO CIRCULAR
# =========================================================

def criar_foto_circular(
    imagem,
    tamanho
):

    imagem = ajustar_imagem_cover(
        imagem,
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

    resultado = Image.new(
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

    resultado.paste(
        imagem,
        (0, 0),
        mascara
    )

    return resultado


# =========================================================
# TEXTO CENTRALIZADO
# =========================================================

def texto_centralizado(
    draw,
    texto,
    y,
    fonte_texto,
    cor,
    largura=LARGURA
):

    bbox = draw.textbbox(
        (0, 0),
        texto,
        font=fonte_texto
    )

    largura_texto = (
        bbox[2]
        -
        bbox[0]
    )

    x = (
        largura
        -
        largura_texto
    ) // 2

    draw.text(
        (
            x,
            y
        ),
        texto,
        font=fonte_texto,
        fill=cor
    )


# =========================================================
# QUEBRA DE TEXTO CENTRALIZADA
# =========================================================

def texto_multilinha_centralizado(
    draw,
    texto,
    y,
    fonte_texto,
    cor,
    largura_maxima,
    espacamento=8
):

    palavras = texto.split()

    linhas = []
    linha_atual = ""

    for palavra in palavras:

        teste = (
            linha_atual
            +
            " "
            +
            palavra
        ).strip()

        bbox = draw.textbbox(
            (0, 0),
            teste,
            font=fonte_texto
        )

        largura_teste = (
            bbox[2]
            -
            bbox[0]
        )

        if (
            largura_teste
            <= largura_maxima
        ):

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

    altura_total = 0

    for linha in linhas:

        bbox = draw.textbbox(
            (0, 0),
            linha,
            font=fonte_texto
        )

        largura_linha = (
            bbox[2]
            -
            bbox[0]
        )

        altura_linha = (
            bbox[3]
            -
            bbox[1]
        )

        x = (
            LARGURA
            -
            largura_linha
        ) // 2

        draw.text(
            (
                x,
                y
            ),
            linha,
            font=fonte_texto,
            fill=cor
        )

        y += (
            altura_linha
            +
            espacamento
        )

        altura_total += (
            altura_linha
            +
            espacamento
        )

    return y


# =========================================================
# SOMBRA DA CAPA
# =========================================================

def adicionar_sombra_capa(
    base,
    x,
    y,
    largura,
    altura
):

    sombra = Image.new(
        "RGBA",
        base.size,
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
            x + 10,
            y + 15,
            x + largura + 10,
            y + altura + 15
        ),
        radius=15,
        fill=(
            50,
            45,
            35,
            90
        )
    )

    sombra = sombra.filter(
        ImageFilter.GaussianBlur(
            22
        )
    )

    base.alpha_composite(
        sombra
    )


# =========================================================
# CHECK
# =========================================================

def desenhar_check(
    draw,
    centro_x,
    centro_y
):

    raio = 24

    draw.ellipse(
        (
            centro_x - raio,
            centro_y - raio,
            centro_x + raio,
            centro_y + raio
        ),
        fill=VERDE
    )

    draw.line(
        (
            centro_x - 11,
            centro_y,
            centro_x - 2,
            centro_y + 10
        ),
        fill=BRANCO,
        width=5
    )

    draw.line(
        (
            centro_x - 2,
            centro_y + 10,
            centro_x + 14,
            centro_y - 10
        ),
        fill=BRANCO,
        width=5
    )


# =========================================================
# ESTRELAS
# =========================================================

def pontos_estrela(
    centro_x,
    centro_y,
    raio_externo,
    raio_interno
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
            math.cos(angulo)
            *
            raio
        )

        y = (
            centro_y
            +
            math.sin(angulo)
            *
            raio
        )

        pontos.append(
            (
                x,
                y
            )
        )

    return pontos


def desenhar_estrelas(
    draw,
    nota,
    y
):

    try:
        nota = int(
            round(
                float(nota)
            )
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

    tamanho = 34
    distancia = 78

    largura_total = (
        distancia
        *
        4
    )

    inicio_x = (
        LARGURA
        -
        largura_total
    ) // 2

    for i in range(5):

        centro_x = (
            inicio_x
            +
            i
            *
            distancia
        )

        pontos = pontos_estrela(
            centro_x,
            y,
            tamanho,
            tamanho * 0.45
        )

        if i < nota:

            draw.polygon(
                pontos,
                fill=VERDE_ESCURO
            )

        else:

            draw.polygon(
                pontos,
                outline=VERDE_CLARO,
                width=3
            )


# =========================================================
# CARD DO USUÁRIO
# =========================================================

def desenhar_card_usuario(
    imagem,
    draw,
    usuario,
    mensagem,
    frase
):

    x = 155
    y = 1570

    largura = 770
    altura = 160


    # -----------------------------------------------------
    # FUNDO TRANSLÚCIDO
    # -----------------------------------------------------

    camada = Image.new(
        "RGBA",
        imagem.size,
        (
            0,
            0,
            0,
            0
        )
    )

    draw_camada = ImageDraw.Draw(
        camada
    )

    draw_camada.rounded_rectangle(
        (
            x,
            y,
            x + largura,
            y + altura
        ),
        radius=38,
        fill=(
            255,
            255,
            255,
            185
        )
    )

    imagem.alpha_composite(
        camada
    )


    # -----------------------------------------------------
    # FOTO
    # -----------------------------------------------------

    tamanho_foto = 105

    foto = carregar_imagem(
        getattr(
            usuario,
            "foto",
            None
        )
    )

    foto_x = x + 35
    foto_y = y + 27


    if foto:

        foto = criar_foto_circular(
            foto,
            tamanho_foto
        )

        imagem.alpha_composite(
            foto,
            (
                foto_x,
                foto_y
            )
        )

    else:

        draw.ellipse(
            (
                foto_x,
                foto_y,
                foto_x + tamanho_foto,
                foto_y + tamanho_foto
            ),
            fill="#F6F3EA",
            outline=VERDE,
            width=4
        )

        inicial = (
            usuario.nome[0].upper()
            if usuario.nome
            else "L"
        )

        fonte_inicial = fonte(
            FONTE_SERIF_BOLD,
            42
        )

        bbox = draw.textbbox(
            (0, 0),
            inicial,
            font=fonte_inicial
        )

        draw.text(
            (
                foto_x
                +
                (
                    tamanho_foto
                    -
                    (
                        bbox[2]
                        -
                        bbox[0]
                    )
                )
                / 2,

                foto_y
                +
                (
                    tamanho_foto
                    -
                    (
                        bbox[3]
                        -
                        bbox[1]
                    )
                )
                / 2
                -
                7
            ),
            inicial,
            font=fonte_inicial,
            fill=MARROM
        )


    # -----------------------------------------------------
    # NOME
    # -----------------------------------------------------

    nome = (
        usuario.nome
        or "Leitor"
    )

    draw.text(
        (
            x + 165,
            y + 30
        ),
        nome.upper(),
        font=fonte(
            FONTE_SERIF_BOLD,
            27
        ),
        fill=MARROM
    )


    # -----------------------------------------------------
    # USERNAME
    # -----------------------------------------------------

    username = getattr(
        usuario,
        "username",
        None
    )

    if username:

        draw.text(
            (
                x + 165,
                y + 67
            ),
            f"@{username}",
            font=fonte(
                FONTE_SANS,
                20
            ),
            fill=VERDE
        )


    # -----------------------------------------------------
    # LINHA
    # -----------------------------------------------------

    draw.line(
        (
            x + 165,
            y + 99,
            x + largura - 45,
            y + 99
        ),
        fill="#D8D8C9",
        width=2
    )


    # -----------------------------------------------------
    # MENSAGEM
    # -----------------------------------------------------

    mensagem = (
        mensagem
        or
        frase
    )

    if len(mensagem) > 70:

        mensagem = (
            mensagem[:67]
            +
            "..."
        )

    draw.text(
        (
            x + 165,
            y + 113
        ),
        mensagem,
        font=fonte(
            FONTE_SANS,
            23
        ),
        fill=PRETO
    )


# =========================================================
# FUNÇÃO PRINCIPAL
# =========================================================

def gerar_card_livro_concluido(
    usuario,
    livro,
    nota=None,
    mensagem=None,
    frase="Mais uma história para a minha estante."
):

    # =====================================================
    # FUNDO
    # =====================================================

    imagem = Image.new(
        "RGBA",
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
    # TEXTURA VERDE
    # =====================================================

    textura = abrir_png(
        "textura_verde.png"
    )

    if textura:

        textura = redimensionar_proporcional(
            textura,
            largura=690
        )

        imagem.alpha_composite(
            textura,
            (
                0,
                ALTURA
                -
                textura.height
            )
        )


    # =====================================================
    # RAMO SUPERIOR
    # =====================================================

    adicionar_elemento(
        imagem,
        "ramo_superior.png",
        0,
        0,
        largura=260
    )


    # =====================================================
    # RAMO INFERIOR
    # =====================================================

    ramo_inferior = abrir_png(
        "ramo_inferior.png"
    )

    if ramo_inferior:

        ramo_inferior = (
            redimensionar_proporcional(
                ramo_inferior,
                largura=300
            )
        )

        imagem.alpha_composite(
            ramo_inferior,
            (
                LARGURA
                -
                ramo_inferior.width,
                ALTURA
                -
                ramo_inferior.height
            )
        )


    # =====================================================
    # LOGO
    # =====================================================

    logo = abrir_png(
        "logo_compartilhamento.png"
    )

    if logo:

        logo = redimensionar_proporcional(
            logo,
            largura=370
        )

        imagem.alpha_composite(
            logo,
            (
                (
                    LARGURA
                    -
                    logo.width
                )
                // 2,
                55
            )
        )


    # =====================================================
    # CAPA
    # =====================================================

    capa = carregar_imagem(
        getattr(
            livro,
            "capa",
            None
        )
    )

    largura_capa = 470
    altura_capa = 680

    x_capa = (
        LARGURA
        -
        largura_capa
    ) // 2

    y_capa = 300


    if capa:

        capa = ajustar_imagem_cover(
            capa,
            largura_capa,
            altura_capa
        )

        adicionar_sombra_capa(
            imagem,
            x_capa,
            y_capa,
            largura_capa,
            altura_capa
        )

        imagem.alpha_composite(
            capa,
            (
                x_capa,
                y_capa
            )
        )

    else:

        draw.rounded_rectangle(
            (
                x_capa,
                y_capa,
                x_capa + largura_capa,
                y_capa + altura_capa
            ),
            radius=15,
            fill="#EDEBDD"
        )

        texto_centralizado(
            draw,
            "Sem capa",
            y_capa + 310,
            fonte(
                FONTE_SERIF,
                36
            ),
            VERDE
        )


    # =====================================================
    # SELO DA LIBÉLULA
    # =====================================================

    adicionar_elemento(
        imagem,
        "selo_libelula.png",
        x_capa + largura_capa - 80,
        y_capa + altura_capa - 105,
        largura=170
    )


    # =====================================================
    # LEITURA CONCLUÍDA
    # =====================================================

    y_status = 1060

    fonte_status = fonte(
        FONTE_SANS,
        42
    )

    texto_status = (
        "LEITURA CONCLUÍDA!"
    )

    bbox_status = draw.textbbox(
        (0, 0),
        texto_status,
        font=fonte_status
    )

    largura_status = (
        bbox_status[2]
        -
        bbox_status[0]
    )

    largura_grupo = (
        55
        +
        largura_status
    )

    x_grupo = (
        LARGURA
        -
        largura_grupo
    ) // 2


    desenhar_check(
        draw,
        x_grupo + 20,
        y_status + 25
    )


    draw.text(
        (
            x_grupo + 55,
            y_status
        ),
        texto_status,
        font=fonte_status,
        fill=VERDE
    )


    # =====================================================
    # TÍTULO
    # =====================================================

    titulo = (
        getattr(
            livro,
            "titulo",
            None
        )
        or
        "Livro concluído"
    )

    y_titulo = 1175

    y_final_titulo = (
        texto_multilinha_centralizado(
            draw,
            titulo,
            y_titulo,
            fonte(
                FONTE_SERIF_BOLD,
                55
            ),
            MARROM,
            largura_maxima=820,
            espacamento=7
        )
    )


    # =====================================================
    # AUTOR
    # =====================================================

    autor = (
        getattr(
            livro,
            "autor",
            None
        )
        or
        ""
    )

    y_autor = (
        y_final_titulo
        +
        15
    )

    texto_centralizado(
        draw,
        autor,
        y_autor,
        fonte(
            FONTE_SANS,
            40
        ),
        VERDE
    )


    # =====================================================
    # ESTRELAS
    # =====================================================

    y_estrelas = (
        y_autor
        +
        105
    )

    desenhar_estrelas(
        draw,
        nota,
        y_estrelas
    )


    # =====================================================
    # CARD DO USUÁRIO
    # =====================================================

    desenhar_card_usuario(
    imagem,
    draw,
    usuario,
    mensagem,
    frase
    )


    # =====================================================
    # RODAPÉ
    # =====================================================

    texto_centralizado(
        draw,
        "Compartilhado através do Liberium",
        1810,
        fonte(
            FONTE_SANS,
            28
        ),
        VERDE
    )


    # =====================================================
    # SALVAR
    # =====================================================

    usuario_id = getattr(
        usuario,
        "id",
        "usuario"
    )

    livro_id = getattr(
        livro,
        "id",
        "livro"
    )

    nome_arquivo = (
        f"livro_{livro_id}_"
        f"usuario_{usuario_id}.png"
    )

    caminho_saida = os.path.join(
        PASTA_COMPARTILHAMENTOS,
        nome_arquivo
    )

    imagem = imagem.convert(
        "RGB"
    )

    imagem.save(
        caminho_saida,
        "PNG",
        optimize=True
    )

    print(
        "Imagem criada em:",
        caminho_saida
    )

    return caminho_saida


# =========================================================
# TESTE DIRETO DO ARQUIVO
# =========================================================

if __name__ == "__main__":

    print(
        "gerar_imagem.py carregado com sucesso."
    )