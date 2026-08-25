from app import create_app
from extensions import db

# Importa as models para o SQLAlchemy conhecê-las
from models import MembroClube


app = create_app()


with app.app_context():

    db.create_all()

    print("Banco atualizado com sucesso!")