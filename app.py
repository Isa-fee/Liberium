from flask import Flask
from controllers.home_controller import home_bp
from controllers.books_controller import books_bp
from controllers.user_controller import user_bp

app = Flask(__name__)

# Registrando os controllers
app.register_blueprint(home_bp)
app.register_blueprint(books_bp)
app.register_blueprint(user_bp)

if __name__ == '__main__':
    app.run(debug=True)
