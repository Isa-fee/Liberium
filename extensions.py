from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()

login_manager = LoginManager()
login_manager.login_view = "user_bp.login"
login_manager.login_message = "Faça login para acessar esta página."
login_manager.login_message_category = "warning"