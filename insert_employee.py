from flask import Blueprint, jsonify, redirect, render_template, request, url_for, flash
from auth import auth
from rate_limiter import limiter
from database.model.pond import Pond
from database.model.employee import Employee  # Import the Employee model
from database.mysql import db, format_database_error
from form.form_insert import InsertEmployeeForm  # Assuming you have a form for inserting employees
from flask_login import current_user, login_required

bp = Blueprint("insert_employee", __name__, url_prefix="/employee")

@bp.route("/insert/", methods=["POST", "GET"])
@login_required
def insert_employee():
    # Check if user is employee and redirect if needed
    if current_user.role == 'employee':
        flash("Access denied. Only owners can create employees.", "danger")
        return redirect(url_for("smart_cultivation_system.employee_dashboard"))

    form = InsertEmployeeForm()

    # Populate pond options for the current owner only
    user_ponds = Pond.query.filter_by(owner_id=current_user.user_id).all()
    form.ponds.choices = [(pond.pond_id, f'{pond.pond_id} - {pond.pond_name}') for pond in user_ponds]

    if form.validate_on_submit():
        employee_name = form.employee_name.data
        employee_email = form.employee_email.data
        password = form.password.data

        employee = Employee(
            user_id=current_user.user_id,
            employee_name=employee_name,
            employee_email=employee_email,
            password=password,
        )

        try:
            # Assign selected ponds to the employee
            selected_pond_ids = form.ponds.data
            for pond_id in selected_pond_ids:
                pond = Pond.query.get(pond_id)
                if pond and pond.owner_id == current_user.user_id:  # Verify pond ownership
                    employee.ponds.append(pond)

            db.session.add(employee)
            db.session.commit()
            flash(f"Employee {employee_email} created successfully!", "success")
            return redirect(url_for("smart_cultivation_system.owner_dashboard"))

        except Exception as e:
            db.session.rollback()
            error_msg = format_database_error(e)
            flash(f"An error occurred: {error_msg}", "danger")

    return render_template(
        "pages/smart_cultivation_system/insert_employee.html", form=form
    )

@bp.route("/api/insert/", methods=["POST", "GET"])
@limiter.limit("5 per minute")
@auth.login_required()
def insert_employee_api():
    if request.method == "POST":
        employee_name = request.form.get("employee_name")
        employee_email = request.form.get("employee_email")
        password = request.form.get("password")

        if not employee_name or not employee_email or not password:
            return jsonify({"error": "Missing required fields"}), 400

        try:
            employee = Employee(
                user_id=auth.current_user().user_id,
                employee_name=employee_name,
                employee_email=employee_email,
                password=password,
            )
            db.session.add(employee)
            db.session.commit()

            return (
                jsonify(
                    {
                        "status": {
                            "code": 201,
                            "message": "Employee created successfully",
                        },
                        "employee": {
                            "employee_id": employee.employee_id,
                            "employee_name": employee_name,
                            "employee_email": employee_email,
                            "creation_date": employee.creation_date.strftime(
                                "%Y-%m-%d %H:%M:%S"
                            ),
                        },
                    }
                ),
                201,
            )
        except Exception as e:
            db.session.rollback()
            error_msg = format_database_error(e)
            return (
                jsonify(
                    {
                        "status": {"code": 500, "message": error_msg},
                        "data": None,
                    }
                ),
                500,
            )
    else:
        return (
            jsonify(
                {"status": {"code": 405, "message": "Method not allowed"}, "data": None}
            ),
            405,
        )
