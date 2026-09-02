import sqlite3
import os


BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

CAMINHO_BANCO = os.path.join(
    BASE_DIR,
    "instance",
    "liberium.db"
)


print("Banco encontrado:")
print(CAMINHO_BANCO)


conn = sqlite3.connect(CAMINHO_BANCO)
cursor = conn.cursor()


# ==========================================
# VERIFICAR SE A TABELA JÁ EXISTE
# ==========================================

cursor.execute("""
    SELECT name
    FROM sqlite_master
    WHERE type = 'table'
    AND name = 'curtidas_discussao'
""")

tabela_existe = cursor.fetchone()


# ==========================================
# CRIAR TABELA
# ==========================================

if not tabela_existe:

    cursor.execute("""
        CREATE TABLE curtidas_discussao (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            usuario_id INTEGER NOT NULL,

            discussao_id INTEGER NOT NULL,

            data_criacao DATETIME,

            CONSTRAINT uq_usuario_curtida_discussao
                UNIQUE (usuario_id, discussao_id),

            FOREIGN KEY (usuario_id)
                REFERENCES usuarios(id),

            FOREIGN KEY (discussao_id)
                REFERENCES discussoes(id)
                ON DELETE CASCADE
        )
    """)

    conn.commit()

    print(
        "\n✅ Tabela curtidas_discussao criada."
    )

else:

    print(
        "\n⚠️ A tabela curtidas_discussao já existe."
    )


# ==========================================
# MOSTRAR COLUNAS
# ==========================================

cursor.execute(
    "PRAGMA table_info(curtidas_discussao)"
)

colunas = cursor.fetchall()


print("\n==============================")
print("BANCO ATUALIZADO COM SUCESSO!")
print("==============================")


print("\nColunas de curtidas_discussao:")

for coluna in colunas:

    print(
        f" - {coluna[1]} ({coluna[2]})"
    )


conn.close()