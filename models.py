from extensions import db
from flask_login import UserMixin

class Usuario(UserMixin, db.Model):
    __tablename__ = "usuarios"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    senha = db.Column(db.String(200), nullable=False)



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