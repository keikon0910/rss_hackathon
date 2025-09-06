from flask import Blueprint, render_template

index_bp = Blueprint('index',__name__,url_prefix='/',template_folder='../templates' )



@index_bp.route('/')
def home():
    return render_template('index/index.html')

@index_bp.route('/login', methods=['GET', 'POST'])
def login():
    return render_template('index/login.html')

@index_bp.route('/registration', methods=['GET', 'POST'])
def registration():
    return render_template('index/registration.html')