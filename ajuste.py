import sqlite3
import os



#ISSO AQUI É PRA QUANDO PRECISAR FAZER ALGUM AJUSTE NO BANCO SEM PRECISAR EXCLUIR O INSTANCE

# =========================================================
# LOCALIZAR BANCO
# =========================================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

CAMINHO_BANCO = os.path.join(
    BASE_DIR,
    "instance",
    "liberium.db"
)


# =========================================================
# VERIFICAR BANCO
# =========================================================

if not os.path.exists(CAMINHO_BANCO):

    print("❌ Banco não encontrado:")
    print(CAMINHO_BANCO)

    exit()


print("Banco encontrado:")
print(CAMINHO_BANCO)
print()


# =========================================================
# CONECTAR
# =========================================================

conexao = sqlite3.connect(
    CAMINHO_BANCO
)

cursor = conexao.cursor()


try:

    # =====================================================
    # DESCOBRIR COLUNAS DE ANOTACOES
    # =====================================================

    cursor.execute(
        "PRAGMA table_info(anotacoes)"
    )

    colunas = {
        linha[1]
        for linha in cursor.fetchall()
    }

    print("Colunas atuais de anotacoes:")

    for coluna in sorted(colunas):
        print(f" - {coluna}")

    print()


    # =====================================================
    # ADICIONAR clube_id
    # =====================================================

    if "clube_id" not in colunas:

        cursor.execute("""
            ALTER TABLE anotacoes
            ADD COLUMN clube_id INTEGER
            REFERENCES clubes(id)
        """)

        print("✅ Coluna clube_id adicionada.")

    else:

        print(
            "ℹ️ clube_id já existe. "
            "Nenhuma alteração necessária."
        )


    # =====================================================
    # ADICIONAR livro_id
    # =====================================================

    if "livro_id" not in colunas:

        cursor.execute("""
            ALTER TABLE anotacoes
            ADD COLUMN livro_id INTEGER
            REFERENCES livros(id)
        """)

        print("✅ Coluna livro_id adicionada.")

    else:

        print(
            "ℹ️ livro_id já existe. "
            "Nenhuma alteração necessária."
        )


    # =====================================================
    # SALVAR
    # =====================================================

    conexao.commit()

    print()
    print("==============================")
    print("BANCO ATUALIZADO COM SUCESSO!")
    print("==============================")


    # =====================================================
    # MOSTRAR RESULTADO FINAL
    # =====================================================

    cursor.execute(
        "PRAGMA table_info(anotacoes)"
    )

    print()
    print("Colunas finais de anotacoes:")

    for linha in cursor.fetchall():

        print(
            f" - {linha[1]} ({linha[2]})"
        )


except Exception as erro:

    conexao.rollback()

    print()
    print("❌ Erro ao atualizar o banco:")
    print(erro)


finally:

    conexao.close()