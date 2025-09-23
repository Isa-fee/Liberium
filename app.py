from flask import Flask, request, render_template, flash, redirect, url_for, make_response

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

    
