from flask import Blueprint, render_template

subfunction_bp = Blueprint('subfunction',__name__,url_prefix='/subfunction',template_folder='../templates' )

@subfunction_bp.route('/DM')
def DM():
    return render_template('subfunction/DM.html')

@subfunction_bp.route('/DM_personal')
def DM_personal():
    return render_template('subfunction/DM_personal.html')

@subfunction_bp.route('/notification')
def notification():
    return render_template('subfunction/notification.html')