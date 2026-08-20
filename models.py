from extensions import db
from flask_login import UserMixin
from datetime import date


class Usuario(UserMixin, db.Model):
    __tablename__ = "usuarios"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    senha = db.Column(db.String(200), nullable=False)
    foto = db.Column(db.String(255), nullable=True)
    # GAMIFICAÇÃO

    xp = db.Column(db.Integer, default=20)

    nivel = db.Column(
        db.String(50),
        default="Leitor Iniciante"
    )

    libelulas = db.Column(
        db.Integer,
        default=5
    )

class Amizade(db.Model):
    __tablename__ = "amizades"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    usuario_id = db.Column(
        db.Integer,
        db.ForeignKey("usuarios.id"),
        nullable=False
    )

    amigo_id = db.Column(
        db.Integer,
        db.ForeignKey("usuarios.id"),
        nullable=False
    )

    # pendente | aceita | recusada
    status = db.Column(
        db.String(20),
        nullable=False,
        default="pendente"
    )

    data_criacao = db.Column(
        db.DateTime,
        nullable=False,
        default=db.func.now()
    )

    usuario = db.relationship(
        "Usuario",
        foreign_keys=[usuario_id],
        backref="solicitacoes_enviadas"
    )

    amigo = db.relationship(
        "Usuario",
        foreign_keys=[amigo_id],
        backref="solicitacoes_recebidas"
    )

class Livro(db.Model):
    __tablename__ = "livros"

    id = db.Column(db.Integer, primary_key=True)

    titulo = db.Column(db.String(255), nullable=False)
    autor = db.Column(db.String(255))
    descricao = db.Column(db.Text)
    capa = db.Column(db.String(500))
    genero = db.Column(db.String(100))
    editora = db.Column(db.String(150))
    paginas = db.Column(db.Integer)
    ano = db.Column(db.String(20))
    idioma = db.Column(db.String(50))
    avaliacao = db.Column(db.Float)
    destaque = db.Column(db.Boolean, default=False)


class Estante(db.Model):
    __tablename__ = "estante"

    __table_args__ = (
        db.UniqueConstraint(
            "usuario_id",
            "livro_id",
            name="uq_usuario_livro"
        ),
    )

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    usuario_id = db.Column(
        db.Integer,
        db.ForeignKey("usuarios.id"),
        nullable=False
    )

    livro_id = db.Column(
        db.Integer,
        db.ForeignKey("livros.id"),
        nullable=False
    )

    # quero ler | lendo | lido
    status = db.Column(
        db.String(20),
        nullable=False,
        default="quero ler"
    )
    # posição do livro dentro da prateleira
    posicao = db.Column(
        db.Integer,
        nullable=False,
        default=0
    )

    # porcentagem de leitura
    progresso = db.Column(
        db.Integer,
        default=0
    )

    pagina_atual = db.Column(
    db.Integer,
    default=0)

    # quando terminou a leitura
    data_leitura = db.Column(
        db.Date,
        nullable=True
    )

    # nota de 1 a 5 estrelas
    nota = db.Column(
        db.Integer,
        nullable=True
    )

    # resenha do usuário
    resenha = db.Column(
        db.Text,
        nullable=True
    )

    livro = db.relationship(
        "Livro",
        backref="estantes"
    )

    usuario = db.relationship(
        "Usuario",
        backref="estantes"
    )

class Insignia(db.Model):
    __tablename__ = "insignias"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    nome = db.Column(
        db.String(100),
        nullable=False
    )

    descricao = db.Column(
        db.String(255),
        nullable=False
    )

    imagem = db.Column(db.String(150), nullable=False)

class UsuarioInsignia(db.Model):
    __tablename__ = "usuario_insignias"

    __table_args__ = (
        db.UniqueConstraint(
            "usuario_id",
            "insignia_id",
            name="uq_usuario_insignia"
        ),
    )

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    usuario_id = db.Column(
        db.Integer,
        db.ForeignKey("usuarios.id"),
        nullable=False
    )

    insignia_id = db.Column(
        db.Integer,
        db.ForeignKey("insignias.id"),
        nullable=False
    )


    usuario = db.relationship(
        "Usuario",
        backref="conquistas"
    )

    insignia = db.relationship(
        "Insignia"
    )

class ItemColecionavel(db.Model):
    __tablename__ = "itens_colecionaveis"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    nome = db.Column(
        db.String(120),
        nullable=False
    )

    descricao = db.Column(
        db.String(255),
        nullable=True
    )

    # decoracao ou boneco
    tipo = db.Column(
        db.String(30),
        nullable=False
    )

    preco = db.Column(
        db.Integer,
        nullable=False
    )

    # caminho da imagem dentro de static/
    imagem = db.Column(
        db.String(255),
        nullable=False
    )

    # permite retirar um item da loja sem apagá-lo
    ativo = db.Column(
        db.Boolean,
        default=True,
        nullable=False
    )

class UsuarioColecionavel(db.Model):
    __tablename__ = "usuarios_colecionaveis"

    __table_args__ = (
        db.UniqueConstraint(
            "usuario_id",
            "item_id",
            name="uq_usuario_item_colecionavel"
        ),
    )

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    usuario_id = db.Column(
        db.Integer,
        db.ForeignKey("usuarios.id"),
        nullable=False
    )

    item_id = db.Column(
        db.Integer,
        db.ForeignKey("itens_colecionaveis.id"),
        nullable=False
    )

    data_aquisicao = db.Column(
        db.Date,
        nullable=False,
        default=date.today
    )

    usuario = db.relationship(
        "Usuario",
        backref="colecao"
    )

    item = db.relationship(
        "ItemColecionavel",
        backref="proprietarios"
    )

class DecoracaoEstante(db.Model):
    __tablename__ = "decoracoes_estante"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    usuario_id = db.Column(
        db.Integer,
        db.ForeignKey("usuarios.id"),
        nullable=False
    )

    usuario_item_id = db.Column(
        db.Integer,
        db.ForeignKey("usuarios_colecionaveis.id"),
        nullable=False
    )

    # lendo | lidos | quero ler
    prateleira = db.Column(
        db.String(30),
        nullable=False
    )

    # posição dentro da prateleira
    posicao = db.Column(
        db.Integer,
        nullable=False,
        default=0
    )

    usuario = db.relationship(
        "Usuario",
        backref="decoracoes_estante"
    )

    usuario_item = db.relationship(
        "UsuarioColecionavel",
        backref=db.backref(
            "decoracao_estante",
            uselist=False
        )
    )


class MetaLeitura(db.Model):
    __tablename__ = "metas_leitura"

    id = db.Column(db.Integer, primary_key=True)

    usuario_id = db.Column(
        db.Integer,
        db.ForeignKey("usuarios.id"),
        nullable=False
    )

    quantidade = db.Column(
        db.Integer,
        nullable=False
    )

    progresso = db.Column(
        db.Integer,
        default=0
    )

    mes = db.Column(
        db.Integer,
        nullable=False
    )

    ano = db.Column(
        db.Integer,
        nullable=False
    )

    data_inicio = db.Column(
        db.Date,
        nullable=False,
        default=date.today
    )

    data_fim = db.Column(
    db.Date,
    nullable=False
    )

    concluida = db.Column(
        db.Boolean,
        default=False
    )

    recompensa_recebida = db.Column(
        db.Boolean,
        default=False
    )

    usuario = db.relationship(
        "Usuario",
        backref="metas_leitura"
    )

class Atividade(db.Model):
    __tablename__ = "atividades"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    usuario_id = db.Column(
        db.Integer,
        db.ForeignKey("usuarios.id"),
        nullable=False
    )

    livro_id = db.Column(
        db.Integer,
        db.ForeignKey("livros.id"),
        nullable=True
    )

    tipo = db.Column(
        db.String(50),
        nullable=False
    )

    mensagem = db.Column(
        db.String(255),
        nullable=False
    )

    data_criacao = db.Column(
        db.DateTime,
        nullable=False,
        default=db.func.now()
    )

    usuario = db.relationship(
        "Usuario",
        backref="atividades"
    )

    livro = db.relationship(
        "Livro",
        backref="atividades"
    )

class Clube(db.Model):
    __tablename__ = "clubes"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    nome = db.Column(
        db.String(120),
        nullable=False
    )

    descricao = db.Column(
        db.Text,
        nullable=False
    )

    genero = db.Column(
        db.String(100),
        nullable=False
    )

    imagem = db.Column(
        db.String(255),
        nullable=True
    )

    usuario_id = db.Column(
        db.Integer,
        db.ForeignKey("usuarios.id"),
        nullable=False
    )

    quantidade_membros = db.Column(
        db.Integer,
        default=1,
        nullable=False
    )

    data_criacao = db.Column(
        db.Date,
        default=date.today,
        nullable=False
    )

    usuario = db.relationship(
        "Usuario",
        backref="clubes_criados"
    )