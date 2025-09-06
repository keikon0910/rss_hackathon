from flask import Blueprint, render_template

persponal_page_bp = Blueprint('personal_page', __name__, url_prefix='/', template_folder='../templates')


@persponal_page_bp.route('/personal_page')
def personal_page():
    return render_template('personal_page/personal_page.html')

@persponal_page_bp.route('/personal_page/personal_settings')
def personal_settings():
    return render_template('personal_page/personal_settings.html')  