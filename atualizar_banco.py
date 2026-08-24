from app import create_app
from extensions import db

app = create_app()

with app.app_context():

    db.session.execute(
        db.text(
            "ALTER TABLE clubes ADD COLUMN livro_id INTEGER"
        )
    )

    db.session.commit()

    print("Coluna livro_id adicionada com sucesso!")