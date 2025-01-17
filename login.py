from flask import Blueprint, jsonify, redirect, render_template, request, url_for, flash
from database.model.user import User
from database.model.employee import Employee
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, LoginManager, login_required, current_user, logout_user
from form.form_login import LoginForm
import json

bp = Blueprint("login", __name__, url_prefix="/login")

@bp.route("/", methods=["GET"])
def login():
    return redirect(url_for("login.user_login"))

@bp.route("/user_login", methods=["GET", "POST"])
def user_login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for("smart_cultivation_system.owner_dashboard"))
        
        flash("Invalid email or password", "danger")
        return redirect(url_for("login.user_login"))

    return render_template("pages/smart_cultivation_system/login_user.html", form=form)

@bp.route("/employee_login", methods=["GET", "POST"])
def employee_login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        employee = Employee.query.filter_by(employee_email=email).first()
        if employee and employee.check_password(password):
            print(f"Employee role: {employee.role}")
            login_user(employee)
            return redirect(url_for("smart_cultivation_system.employee_dashboard"))
        
        flash("Invalid email or password", "danger")
        return redirect(url_for("login.employee_login"))

    return render_template("pages/smart_cultivation_system/login_employee.html", form=form)
