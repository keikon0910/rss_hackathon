from flask import Blueprint, render_template
from flask import request, redirect, url_for, flash
from werkzeug.security import generate_password_hash

import psycopg2
conn = psycopg2.connect(
    dbname="posts_db_rkcz",
    user="posts_db_rkcz_user",
    password="rPcuE4VPsn79TPngWJd8ZAQrDF1ktI7F",
    host="dpg-d2top2p5pdvs739pct1g-a.oregon-postgres.render.com",
    port="5432"
)

index_bp = Blueprint(
    'index',
    __name__,
    template_folder='../../templates/index'  
)


@index_bp.route('/')
def index():
    return render_template('index.html')  

@index_bp.route('/login', methods=['GET', 'POST'])
def login():
    return render_template('login.html')

@index_bp.route('/registration', methods=['GET', 'POST'])
def registration():
    
    return render_template('registration.html')
