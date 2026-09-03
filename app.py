import os
from flask import Flask
from flask_login import current_user
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

    app.config[
        'SQLALCHEMY_TRACK_MODIFICATIONS'
    ] = False

    db.init_app(app)
    login_manager.init_app(app)


    # ======================================
    # LOGIN
    # ======================================

    from models import Usuario, Notificacao

    @login_manager.user_loader
    def load_user(user_id):

        return Usuario.query.get(
            int(user_id)
        )


    # ======================================
    # NOTIFICAÇÕES GLOBAIS
    # ======================================

    @app.context_processor
    def notificacoes_globais():

        if not current_user.is_authenticated:

            return {
                "notificacoes_navbar": [],
                "quantidade_notificacoes": 0
            }

        notificacoes_navbar = (
            Notificacao.query
            .filter_by(
                usuario_id=current_user.id,
                lida=False
            )
            .order_by(
                Notificacao.data_criacao.desc()
            )
            .limit(5)
            .all()
        )

        quantidade_notificacoes = (
            Notificacao.query
            .filter_by(
                usuario_id=current_user.id,
                lida=False
            )
            .count()
        )

        return {
            "notificacoes_navbar":
                notificacoes_navbar,

            "quantidade_notificacoes":
                quantidade_notificacoes
        }


    # ======================================
    # BLUEPRINTS
    # ======================================

    from controllers.home_controller import home_bp
    from controllers.books_controller import books_bp
    from controllers.estante_controller import estante_bp
    from controllers.user_controller import user_bp
    from controllers.loja_controller import loja_bp
    from controllers.clubes_controller import clubes_bp
    from controllers.amigos_controller import amigos_bp
    from controllers.admin_controller import admin_bp
    from controllers.notificacoes_controller import notificacoes_bp

    app.register_blueprint(home_bp)
    app.register_blueprint(books_bp)
    app.register_blueprint(estante_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(loja_bp)
    app.register_blueprint(clubes_bp)
    app.register_blueprint(amigos_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(notificacoes_bp)

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
            criar_administrador
        )

        popular_banco()
        popular_colecionaveis()
        criar_administrador()
    app.run(debug=True)