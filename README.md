# Liberium – Estante Virtual Gamificada

O **Liberium** é uma aplicação web criada para incentivar o hábito da leitura de forma leve, divertida e interativa. A plataforma funciona como uma estante virtual gamificada, onde os usuários podem registrar livros, acompanhar metas, ganhar recompensas, subir de nível e disputar posições no ranking com amigos.

---

## Tecnologias Utilizadas

- Python
- Flask
- Flask-Login
- Flask-SQLAlchemy
- SQLite
- HTML5
- CSS3
- JavaScript
- Jinja2

---

## Funcionalidades

### Gerenciamento de Livros
- Adicionar, editar e excluir livros.
- Categorizar livros como *lido*, *lendo* ou *quero ler*.
- Visualização organizada na estante virtual.

### Sistema de Gamificação
- Progressão por níveis.
- Metas mensais configuráveis.
- Recompensas em pontos.
- Badges e conquistas (em desenvolvimento).

### Ranking com Amigos
- Comparação de desempenho entre usuários.
- Pontuação baseada em leitura e metas cumpridas.

### Perfil do Usuário
- Foto, nome e descrição personalizáveis.
- Estatísticas de leitura.

### Autenticação
- Cadastro e login com senha criptografada.
- Sistema de sessão com Flask-Login.

---

## Identidade Visual

O Liberium possui uma identidade visual com inspiração natural, acolhedora e minimalista, remetendo à sensação de calmaria e foco que a leitura proporciona.

### Paleta de Cores

```css
:root {
  /* Paleta principal do Liberium */
  --verde-oliva: #879d84;      /* tom suave e natural — pode ser usado em botões e destaques */
  --branco-floral: #f5f5f5;    /* fundo principal */
  --marrom-cafe: #442b1a;      /* títulos, textos importantes e detalhes */
  --verde-musgo: #36503c;      /* contraste elegante, ótimo para cabeçalhos e rodapés */
}

---

## Como executar o projeto (Windows)

### 1. Clone e abra o repositório

```bash
git clone https://github.com/Isa-fee/Liberium.git
cd Liberium
```

### 2. Crie um ambiente virtual

No Prompt de Comando (CMD):

```bash
python -m venv env
```

### 3. Ative o ambiente virtual

No CMD:

```bash
.\env\scripts\activate
```

### 4. Instale as dependências

```bash
pip install -r requirements.txt
```

### 5. Execute a aplicação

```bash
python app.py
```

### 6. Acesse no navegador

```
http://127.0.0.1:5000
```

---
