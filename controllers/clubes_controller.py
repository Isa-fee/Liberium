from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required, current_user
from extensions import db
from models import Clube
from werkzeug.utils import secure_filename
import os


clubes_bp = Blueprint(
    'clubes',
    __name__,
    url_prefix='/clubes'
)


@clubes_bp.route('/')
def listar_clubes():

    clubes = Clube.query.all()

    return render_template(
        'clubes.html',
        clubes=clubes
    )


@clubes_bp.route('/criar', methods=['GET', 'POST'])
@login_required
def criar_clube():

    if request.method == 'POST':

        nome = request.form.get('nome')
        descricao = request.form.get('descricao')
        genero = request.form.get('genero')

        # Pega o arquivo enviado pelo formulário
        arquivo_imagem = request.files.get('imagem')

        # Começa sem imagem
        caminho_imagem = None

        # Se o usuário enviou uma imagem
        if arquivo_imagem and arquivo_imagem.filename:

            # Limpa o nome do arquivo
            nome_arquivo = secure_filename(
                arquivo_imagem.filename
            )

            # Pasta onde a imagem será salva
            pasta = os.path.join(
                'static',
                'img',
                'clubes'
            )

            # Cria a pasta caso ela não exista
            os.makedirs(
                pasta,
                exist_ok=True
            )

            # Caminho completo para salvar a imagem
            caminho_completo = os.path.join(
                pasta,
                nome_arquivo
            )

            # Salva a imagem na pasta
            arquivo_imagem.save(
                caminho_completo
            )

            # Caminho que será salvo no banco
            caminho_imagem = os.path.join(
                'img',
                'clubes',
                nome_arquivo
            ).replace('\\', '/')


        # Cria o clube
        novo_clube = Clube(
            nome=nome,
            descricao=descricao,
            genero=genero,
            imagem=caminho_imagem,
            usuario_id=current_user.id,
            quantidade_membros=1
        )

        db.session.add(novo_clube)
        db.session.commit()

        return redirect(
            url_for('clubes.listar_clubes')
        )

    return render_template(
        'criar_clube.html'
    )