from flask import Blueprint, render_template
from flask_login import login_required
from models import Livro
from extensions import db
import requests

home_bp = Blueprint(
    'home',
    __name__,
    template_folder='../templates'
)


@home_bp.route('/')
def index():
    return render_template('home/index.html')


@home_bp.route('/home')
@login_required
def home():
    livros = Livro.query.filter_by(
        destaque=True
    ).limit(8).all()

    return render_template(
        "home/home.html",
        livros=livros
    )

@home_bp.route("/sobre")
def sobre():
    return render_template("home/sobre.html")