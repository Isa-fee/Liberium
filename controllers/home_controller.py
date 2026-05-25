from flask import Blueprint, render_template
from flask_login import login_required
import requests

home_bp = Blueprint('home', __name__, template_folder='../templates')


@home_bp.route('/')
def index():
    return render_template('home/index.html')


@home_bp.route('/home')
@login_required
def home():

    url = "https://www.googleapis.com/books/v1/volumes?q=harry+potter&maxResults=8"

    resposta = requests.get(url).json()

    livros = []

    for item in resposta.get("items", []):

        info = item.get("volumeInfo", {})

        livros.append({
            "titulo": info.get("title"),
            "capa": info.get("imageLinks", {}).get("thumbnail"),
            "id": item.get("id"),
            "origem": "google"
        })
    print(livros)

    return render_template("home/home.html", livros=livros)


@home_bp.route("/sobre")
def sobre():
    return render_template("home/sobre.html")