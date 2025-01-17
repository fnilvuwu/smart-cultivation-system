from flask import Blueprint, redirect, url_for

from flask_login import logout_user

bp = Blueprint(
    "logout", __name__, url_prefix="/logout"
)

@bp.route('/')
def logout():
    logout_user()
    return redirect(url_for('login.user_login'))