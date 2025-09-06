from flask import Blueprint, render_template

subfunction_bp = Blueprint(
    'subfunction',
    __name__,
    template_folder='../../templates/subfunction',
    url_prefix=''
)


@subfunction_bp.route('/DM')
def DM():
    return render_template('DM.html')

@subfunction_bp.route('/DM_personal')
def DM_personal():
    return render_template('DM_personal.html')

@subfunction_bp.route('/notification')
def notification():
    return render_template('notification.html')