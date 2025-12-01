from flask import Flask
from extensions import db   # IMPORTA AQUI AGORA!

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'chave-super-secreta'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///liberium.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    from controllers.home_controller import home_bp
    from controllers.books_controller import books_bp
    from controllers.user_controller import user_bp

    app.register_blueprint(home_bp)
    app.register_blueprint(books_bp)
    app.register_blueprint(user_bp)

    return app

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        from models import Usuario, Livro
        db.create_all()

    app.run(debug=True)
