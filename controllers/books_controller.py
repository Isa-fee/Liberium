from flask import Blueprint, render_template

books_bp = Blueprint('books', __name__, template_folder='../templates/books')

@books_bp.route('/books')
def books():
    return render_template('books/books.html')
