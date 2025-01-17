from flask import Blueprint, redirect, render_template, request, url_for, flash
from database.model.user import User
from database.mysql import db
from form.form_register import RegisterForm
from flask_login import login_user

bp = Blueprint(
    "register", __name__, url_prefix="/register"
)

@bp.route("/", methods=["POST", "GET"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if not User.query.filter_by(email=form.email.data).first():
            new_user = User(
                email=form.email.data,
                username=form.username.data,
                password=form.password.data,
            )
            db.session.add(new_user)
            db.session.commit()

            login_user(new_user)

            return redirect(url_for("smart_cultivation_system.get_all_ponds"))
        else:
            flash("You've already signed up with that email, log in instead!")
            return redirect(url_for('login.login'))
        

    return render_template(
        "pages/smart_cultivation_system/register.html", form=form
    )