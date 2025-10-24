from flask import Flask, request, render_template, flash, redirect, url_for, make_response

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')
   
@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/books')
def books():
    return render_template('books.html')

@app.route('/sobre')
def sobre():
    return render_template('sobre.html')

if __name__ == '__main__':
    app.run(debug=True)