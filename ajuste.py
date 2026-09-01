from app import create_app
from extensions import db


app = create_app()


with app.app_context():

    try:

        db.session.execute(
            db.text(
                """
                ALTER TABLE discussoes
                ADD COLUMN discussao_pai_id INTEGER
                REFERENCES discussoes(id)
                """
            )
        )

        db.session.commit()

        print(
            "\nColuna discussao_pai_id criada com sucesso!"
        )

    except Exception as erro:

        db.session.rollback()

        print(
            "\nErro ao atualizar o banco:"
        )

        print(
            erro
        )