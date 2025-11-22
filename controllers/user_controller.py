from flask import Blueprint, render_template

user_bp = Blueprint('user', __name__, template_folder='../templates/user')

@user_bp.route('/perfil')
def perfil():
    return render_template('user/perfil.html')

@user_bp.route('/login')
def login():
    return render_template('user/login.html')

@user_bp.route('/register')
def register():
    return render_template('user/register.html')
