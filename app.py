import os
from flask import Flask
from extensions import db, login_manager
from dotenv import load_dotenv
from utils.insignias import criar_insignias

load_dotenv()

def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.getenv(
        "SECRET_KEY",
        "chave-desenvolvimento"
    )
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
        "DATABASE_URL",
        "sqlite:///liberium.db"
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    login_manager.init_app(app)

    from models import Usuario

    @login_manager.user_loader
    def load_user(user_id):
        return Usuario.query.get(int(user_id))

    from controllers.home_controller import home_bp
    from controllers.books_controller import books_bp
    from controllers.estante_controller import estante_bp
    from controllers.user_controller import user_bp
    from controllers.loja_controller import loja_bp
    from controllers.clubes_controller import clubes_bp
    from controllers.amigos_controller import amigos_bp

    app.register_blueprint(home_bp)
    app.register_blueprint(books_bp)
    app.register_blueprint(estante_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(loja_bp)
    app.register_blueprint(clubes_bp)
    app.register_blueprint(amigos_bp)

    return app


if __name__ == '__main__':
    app = create_app()

    with app.app_context():

        # db.drop_all()
        db.create_all()

        criar_insignias()

        from popular_banco import (
            popular_banco,
            popular_colecionaveis,
            popular_usuarios_teste,
            popular_amizades_teste,
            criar_administrador
        )

        popular_banco()
        popular_colecionaveis()
        popular_usuarios_teste()
        popular_amizades_teste()
        criar_administrador()
    app.run(debug=True)