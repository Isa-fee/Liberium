from app import create_app
from extensions import db

# Importa todas as models para o SQLAlchemy conhecê-las
import models


app = create_app()


with app.app_context():

    db.create_all()

    print("Banco atualizado com sucesso!")

    print("\nTabelas existentes:")

    for tabela in db.metadata.tables:
        print(f" - {tabela}")