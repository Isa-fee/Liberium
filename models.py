from datetime import date, datetime

from flask_login import UserMixin

from extensions import db

# usuario
class Usuario(UserMixin, db.Model):
    __tablename__ = "usuarios"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    nome = db.Column(
        db.String(120),
        nullable=False
    )

    email = db.Column(
        db.String(150),
        unique=True,
        nullable=False
    )

    senha = db.Column(
        db.String(200),
        nullable=False
    )

    foto = db.Column(
        db.String(255),
        nullable=True
    )

    # Gamificação
    xp = db.Column(
        db.Integer,
        default=20
    )

    nivel = db.Column(
        db.String(50),
        default="Leitor Iniciante"
    )

    libelulas = db.Column(
        db.Integer,
        default=5
    )

    # Tipo de usuário:
    # leitor | autor | administrador
    tipo = db.Column(
        db.String(20),
        nullable=False,
        default="leitor"
    )


# AMIZADE
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

#LIVRO
class Livro(db.Model):
    __tablename__ = "livros"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    titulo = db.Column(
        db.String(255),
        nullable=False
    )

    autor = db.Column(
        db.String(255)
    )

    descricao = db.Column(
        db.Text
    )

    capa = db.Column(
        db.String(500)
    )

    genero = db.Column(
        db.String(100)
    )

    editora = db.Column(
        db.String(150)
    )

    paginas = db.Column(
        db.Integer
    )

    ano = db.Column(
        db.String(20)
    )

    idioma = db.Column(
        db.String(50)
    )

    avaliacao = db.Column(
        db.Float
    )

    destaque = db.Column(
        db.Boolean,
        default=False
    )

    google_id = db.Column(
        db.String(100),
        unique=True,
        nullable=True
    )

    origem = db.Column(
        db.String(30),
        default="local"
    )

#ESTANTE
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

    posicao = db.Column(
        db.Integer,
        nullable=False,
        default=0
    )

    progresso = db.Column(
        db.Integer,
        default=0
    )

    pagina_atual = db.Column(
        db.Integer,
        default=0
    )

    data_leitura = db.Column(
        db.Date,
        nullable=True
    )

    nota = db.Column(
        db.Integer,
        nullable=True
    )

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


# INSÍGNIAS
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

    imagem = db.Column(
        db.String(150),
        nullable=False
    )



# INSÍGNIAS DO USUÁRIO
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



# ITEM COLECIONÁVEL
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

    # decoracao | boneco
    tipo = db.Column(
        db.String(30),
        nullable=False
    )

    preco = db.Column(
        db.Integer,
        nullable=False
    )

    imagem = db.Column(
        db.String(255),
        nullable=False
    )

    ativo = db.Column(
        db.Boolean,
        default=True,
        nullable=False
    )


# COLEÇÃO DO USUÁRIO
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


# DECORAÇÃO DA ESTANTE
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


# META DE LEITURA
class MetaLeitura(db.Model):
    __tablename__ = "metas_leitura"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

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


# ATIVIDADE
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


# CLUBE
class Clube(db.Model):
    __tablename__ = "clubes"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    nome = db.Column(
        db.String(100),
        nullable=False
    )

    descricao = db.Column(
        db.Text,
        nullable=True
    )

    genero = db.Column(
        db.String(100),
        nullable=True
    )

    # False = público
    # True = privado
    privado = db.Column(
        db.Boolean,
        nullable=False,
        default=False
    )

    imagem = db.Column(
        db.String(255),
        nullable=True
    )

    # Criador do clube
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

    quantidade_membros = db.Column(
        db.Integer,
        nullable=False,
        default=1
    )

    data_criacao = db.Column(
        db.DateTime,
        nullable=False,
        default=db.func.now()
    )

    # Relacionamentos
    usuario = db.relationship(
        "Usuario",
        foreign_keys=[usuario_id],
        backref="clubes_criados"
    )

    livro = db.relationship(
        "Livro",
        foreign_keys=[livro_id],
        backref="clubes"
    )

# MEMBRO DO CLUBE
class MembroClube(db.Model):
    __tablename__ = "membros_clube"

    __table_args__ = (
        db.UniqueConstraint(
            "clube_id",
            "usuario_id",
            name="uq_membro_clube_usuario"
        ),
    )

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    clube_id = db.Column(
        db.Integer,
        db.ForeignKey("clubes.id"),
        nullable=False
    )

    usuario_id = db.Column(
        db.Integer,
        db.ForeignKey("usuarios.id"),
        nullable=False
    )

    paginas_lidas = db.Column(
        db.Integer,
        default=0,
        nullable=False
    )

    progresso_percentual = db.Column(
        db.Integer,
        default=0,
        nullable=False
    )

    total_atualizacoes = db.Column(
        db.Integer,
        default=0,
        nullable=False
    )

    data_entrada = db.Column(
        db.Date,
        default=date.today,
        nullable=False
    )

    clube = db.relationship(
        "Clube",
        backref=db.backref(
            "membros",
            lazy=True,
            cascade="all, delete-orphan"
        )
    )

    usuario = db.relationship(
        "Usuario",
        backref="clubes_participando"
    )


# CONVITE PARA CLUBE
class ConviteClube(db.Model):
    __tablename__ = "convites_clube"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    clube_id = db.Column(
        db.Integer,
        db.ForeignKey("clubes.id"),
        nullable=False
    )

    remetente_id = db.Column(
        db.Integer,
        db.ForeignKey("usuarios.id"),
        nullable=False
    )

    destinatario_id = db.Column(
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

    clube = db.relationship(
        "Clube",
        backref="convites"
    )

    remetente = db.relationship(
        "Usuario",
        foreign_keys=[remetente_id],
        backref="convites_clube_enviados"
    )

    destinatario = db.relationship(
        "Usuario",
        foreign_keys=[destinatario_id],
        backref="convites_clube_recebidos"
    )

# DISCUSSÃO DO CLUBE
class Discussao(db.Model):
    __tablename__ = "discussoes"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    titulo = db.Column(
        db.String(150),
        nullable=True
    )

    conteudo = db.Column(
        db.Text,
        nullable=False
    )

    data_criacao = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    clube_id = db.Column(
        db.Integer,
        db.ForeignKey("clubes.id"),
        nullable=False
    )

    usuario_id = db.Column(
        db.Integer,
        db.ForeignKey("usuarios.id"),
        nullable=False
    )

    usuario = db.relationship(
        "Usuario",
        backref="discussoes"
    )

    clube = db.relationship(
        "Clube",
        backref=db.backref(
            "discussoes",
            lazy=True,
            cascade="all, delete-orphan"
        )
    )


# ELOGIO DA ESTANTE
class ElogioEstante(db.Model):
    __tablename__ = "elogios_estante"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    autor_id = db.Column(
        db.Integer,
        db.ForeignKey("usuarios.id"),
        nullable=False
    )

    destinatario_id = db.Column(
        db.Integer,
        db.ForeignKey("usuarios.id"),
        nullable=False
    )

    mensagem = db.Column(
        db.String(300),
        nullable=False
    )

    data = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    autor = db.relationship(
        "Usuario",
        foreign_keys=[autor_id]
    )

    destinatario = db.relationship(
        "Usuario",
        foreign_keys=[destinatario_id]
    )


# SOLICITAÇÃO DE LIVRO
class SolicitacaoLivro(db.Model):
    __tablename__ = "solicitacoes_livros"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    titulo = db.Column(
        db.String(255),
        nullable=False
    )

    autor = db.Column(
        db.String(255),
        nullable=False
    )

    descricao = db.Column(
        db.Text,
        nullable=True
    )

    capa = db.Column(
        db.String(500),
        nullable=True
    )

    genero = db.Column(
        db.String(100),
        nullable=True
    )

    editora = db.Column(
        db.String(150),
        nullable=True
    )

    paginas = db.Column(
        db.Integer,
        nullable=True
    )

    ano = db.Column(
        db.String(20),
        nullable=True
    )

    idioma = db.Column(
        db.String(50),
        nullable=True
    )

    isbn = db.Column(
        db.String(30),
        nullable=True
    )

    solicitante_id = db.Column(
        db.Integer,
        db.ForeignKey("usuarios.id"),
        nullable=False
    )

    # pendente | aprovado | recusado
    status = db.Column(
        db.String(20),
        nullable=False,
        default="pendente"
    )

    data_solicitacao = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow
    )

    solicitante = db.relationship(
        "Usuario",
        backref="solicitacoes_livros"
    )
class Notificacao(db.Model):
    __tablename__ = "notificacoes"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    usuario_id = db.Column(
        db.Integer,
        db.ForeignKey("usuarios.id"),
        nullable=False
    )

    # amizade | clube | meta | conquista | comentario | elogio
    tipo = db.Column(
        db.String(30),
        nullable=False
    )

    titulo = db.Column(
        db.String(150),
        nullable=False
    )

    mensagem = db.Column(
        db.String(300),
        nullable=False
    )

    # Página para onde o usuário será levado ao clicar
    link = db.Column(
        db.String(300),
        nullable=True
    )

    lida = db.Column(
        db.Boolean,
        nullable=False,
        default=False
    )

    data_criacao = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow
    )

    usuario = db.relationship(
        "Usuario",
        backref=db.backref(
            "notificacoes",
            lazy=True,
            cascade="all, delete-orphan"
        )
    )