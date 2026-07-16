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
    id = db.Column(
        db.Integer,
        primary_key=True
    )
    usuario_id = db.Column(
        db.Integer,
        db.ForeignKey("usuarios.id")
    )
    livro_id = db.Column(
        db.Integer,
        db.ForeignKey("livros.id")
    )
    status = db.Column(
        db.String(30)
    )

    usuario = db.relationship("Usuario", backref="estante")

    livro = db.relationship("Livro", backref="usuarios_estante")