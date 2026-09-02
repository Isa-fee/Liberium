import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

CAMINHO_BANCO = os.path.join(
    BASE_DIR,
    "instance",
    "liberium.db"
)

print("Banco encontrado:")
print(CAMINHO_BANCO)

conn = sqlite3.connect(CAMINHO_BANCO)
cursor = conn.cursor()

# Verifica as colunas atuais da tabela estante
cursor.execute("PRAGMA table_info(estante)")
colunas = [coluna[1] for coluna in cursor.fetchall()]

print("\nColunas atuais de estante:")

for coluna in colunas:
    print(" -", coluna)

# Adiciona favorito somente se ainda não existir
if "favorito" not in colunas:

    cursor.execute("""
        ALTER TABLE estante
        ADD COLUMN favorito BOOLEAN
        NOT NULL DEFAULT 0
    """)

    conn.commit()

    print("\n✅ Coluna favorito adicionada.")

else:
    print("\n⚠️ A coluna favorito já existe.")

# Confere o resultado
cursor.execute("PRAGMA table_info(estante)")
colunas_finais = cursor.fetchall()

print("\n==============================")
print("BANCO ATUALIZADO COM SUCESSO!")
print("==============================")

print("\nColunas finais de estante:")

for coluna in colunas_finais:
    print(
        f" - {coluna[1]} ({coluna[2]})"
    )

conn.close()