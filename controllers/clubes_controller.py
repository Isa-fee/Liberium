from flask import Blueprint, render_template

clubes_bp = Blueprint('clubes', __name__, url_prefix='/clubes')


@clubes_bp.route('/')
def listar_clubes():
    return render_template('clubes.html')