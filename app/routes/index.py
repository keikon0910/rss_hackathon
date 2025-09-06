from flask import Blueprint, render_template
import os

index_bp = Blueprint(
    'index',
    __name__,
    template_folder='../../templates/index'  # Blueprint 用にサブフォルダを指定
)

@index_bp.route('/')
def home():
    return render_template('index.html')  # ← ここではファイル名だけでOK

@index_bp.route('/login', methods=['GET', 'POST'])
def login():
    return render_template('login.html')

@index_bp.route('/registration', methods=['GET', 'POST'])
def registration():
    return render_template('registration.html')
