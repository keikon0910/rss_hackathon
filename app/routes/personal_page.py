from flask import Blueprint, render_template


personal_page_bp = Blueprint(
    'personal_page',
    __name__,
    template_folder='../../templates/personal_page',
    url_prefix=''
)

@personal_page_bp.route('/personal_page')
def personal_page():
    return render_template('personal_page.html')

@personal_page_bp.route('/personal_setting')
def personal_setting():
    return render_template('personal_setting.html')