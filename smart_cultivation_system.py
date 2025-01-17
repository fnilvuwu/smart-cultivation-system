from flask import (
    Blueprint,
    jsonify,
    redirect,
    render_template,
    request,
    url_for,
    flash,
    send_file,
)
from flask_login import (
    login_user,
    LoginManager,
    login_required,
    current_user,
    logout_user,
    AnonymousUserMixin,
)
from database.model.pond import (
    Pond,
    WaterQuality,
    FishData,
    FishPondMetrics,
)  # Import all models from pond.py
from database.model.employee import Employee
from database.model.user import User
from database.model.association_tables import employee_ponds


from werkzeug.security import generate_password_hash, check_password_hash
from database.mysql import db, format_database_error
from form.form_insert import WaterQualityForm, FishDataForm

WaterQualityForm
import json
from utils.report_generator import generate_excel_report, generate_pdf_report
from datetime import datetime

bp = Blueprint(
    "smart_cultivation_system", __name__, url_prefix="/smart_cultivation_system"
)


def water_quality_to_dict(waterQuality):
    """Convert water quality instance to dictionary with default values"""
    return {
        "date": waterQuality.date.strftime("%Y-%m-%d"),
        "pH": float(waterQuality.pH) if waterQuality.pH is not None else 0,
        "turbidity": (
            float(waterQuality.turbidity) if waterQuality.turbidity is not None else 0
        ),
        "temperature": (
            float(waterQuality.temperature)
            if waterQuality.temperature is not None
            else 0
        ),
        "ammonia": (
            float(waterQuality.ammonia) if waterQuality.ammonia is not None else 0
        ),
        "dissolved_oxygen": (
            float(waterQuality.dissolved_oxygen)
            if waterQuality.dissolved_oxygen is not None
            else 0
        ),
    }


@bp.route("/owner_dashboard")
@login_required
def owner_dashboard():
    # Check if user is employee and redirect if needed
    if current_user.role == "employee":
        flash("Access denied. Employee access only.", "danger")
        return redirect(url_for("smart_cultivation_system.employee_dashboard"))

    user_id = current_user.user_id

    # Query ponds associated with the owner
    ponds = Pond.query.filter_by(owner_id=user_id).all()

    # Query employees associated with the owner
    employees = Employee.query.filter_by(user_id=user_id).all()

    return render_template(
        "pages/smart_cultivation_system/index_owner.html",
        ponds=ponds,
        employees=employees,
    )


@bp.route("/employee_dashboard")
@login_required
def employee_dashboard():
    # Check if user is owner and redirect if needed
    if current_user.role == "user":
        flash("Access denied. Owner access only.", "danger")
        return redirect(url_for("smart_cultivation_system.owner_dashboard"))

    # Get ponds assigned to this employee
    assigned_ponds = current_user.ponds

    return render_template(
        "pages/smart_cultivation_system/index_employee.html", ponds=assigned_ponds
    )


@bp.route("/pond/<int:pond_id>")
@login_required
def smart_cultivation_system_pond(pond_id):
    pond = get_pond_by_id(pond_id)

    if pond is None:
        return "Pond not found", 404

    waterQualities = get_water_quality_by_pond_id(pond_id)
    fishData = get_fish_data_by_pond_id(pond_id)
    metrics = get_metrics_by_pond_id(pond_id)
    owner = User.query.get(pond.owner_id)
    employees = pond.employees
    water_form = WaterQualityForm()
    fish_form = FishDataForm()

    # Debug print
    print("Number of water qualities:", len(waterQualities))

    # Ensure we have at least one water quality record
    latestWaterQualities = (
        water_quality_to_dict(waterQualities[-1])
        if waterQualities
        else {
            "date": "",
            "pH": 7.0,  # Default neutral pH
            "turbidity": 0.0,
            "temperature": 25.0,  # Default room temperature
        }
    )

    # Sort water qualities by date
    sorted_water_qualities = sorted(waterQualities, key=lambda x: x.date)

    historicalWaterQualities = {
        "dates": [w.date.strftime("%Y-%m-%d %H:%M:%S") for w in sorted_water_qualities],
        "ph": [float(w.pH) if w.pH is not None else 0 for w in sorted_water_qualities],
        "turbidity": [
            float(w.turbidity) if w.turbidity is not None else 0
            for w in sorted_water_qualities
        ],
        "temperature": [
            float(w.temperature) if w.temperature is not None else 0
            for w in sorted_water_qualities
        ],
        "nitrate": [
            float(w.nitrate) if w.nitrate is not None else 0
            for w in sorted_water_qualities
        ],
    }

    # Debug print
    print("Latest water qualities:", latestWaterQualities)
    print("Historical water qualities:", historicalWaterQualities)

    template_data = {
        "pond": pond,
        "waterQualities": waterQualities,
        "fishData": fishData,
        "metrics": metrics,
        "owner": owner,
        "employees": employees,
        "latestWaterQualities": json.dumps(latestWaterQualities),
        "historicalWaterQualities": json.dumps(historicalWaterQualities),
        "water_form": water_form,
        "fish_form": fish_form,
    }

    return render_template(
        (
            "pages/smart_cultivation_system/pond_employee.html"
            if current_user.role == "employee"
            else "pages/smart_cultivation_system/pond_owner.html"
        ),
        **template_data,
    )


@bp.route("/employee/<int:employee_id>")
@login_required
def employee_details(employee_id):
    employee = Employee.query.filter_by(employee_id=employee_id).first_or_404()

    # Check if current user is the owner of this employee
    if employee.user_id != current_user.user_id:
        flash("You don't have permission to view this employee.", "danger")
        return redirect(url_for("smart_cultivation_system.owner_dashboard"))

    # Get all ponds assigned to this employee
    assigned_ponds = employee.ponds

    return render_template(
        "pages/smart_cultivation_system/employees.html",
        employee=employee,
        ponds=assigned_ponds,
    )


def get_pond_by_id(pond_id):
    return Pond.query.filter_by(pond_id=pond_id).first()


def get_water_quality_by_pond_id(pond_id):
    return WaterQuality.query.filter_by(pond_id=pond_id).all()


def get_fish_data_by_pond_id(pond_id):
    return FishData.query.filter_by(pond_id=pond_id).all()


def get_metrics_by_pond_id(pond_id):
    return FishPondMetrics.query.filter_by(pond_id=pond_id).all()


# Route to add water quality data
@bp.route("/<int:pond_id>/add_water_quality", methods=["POST"])
@login_required
def add_water_quality(pond_id):
    water_form = WaterQualityForm()

    ph = request.form.get("pH")
    turbidity = request.form.get("turbidity")
    temperature = request.form.get("temperature")
    nitrate = request.form.get("nitrate")
    ammonia = request.form.get("ammonia")
    dissolved_oxygen = request.form.get("dissolved_oxygen")

    print(
        f"Received data - pH: {ph}, turbidity: {turbidity}, temp: {temperature}, nitrate: {nitrate}, ammonia: {ammonia}, dissolved_oxygen: {dissolved_oxygen}"
    )
    print(f"Current user employee_id: {current_user.employee_id}")

    if not (
        ph and turbidity and temperature and nitrate and ammonia and dissolved_oxygen
    ):
        flash("All fields are required.", "danger")
        return redirect(
            url_for(
                "smart_cultivation_system.pond_details",
                water_form=water_form,
                pond_id=pond_id,
            )
        )

    try:
        water_quality = WaterQuality(
            pond_id=pond_id,
            pH=float(ph),
            turbidity=float(turbidity),
            temperature=float(temperature),
            nitrate=float(nitrate),
            ammonia=float(ammonia),
            dissolved_oxygen=float(dissolved_oxygen),
            employee_id=current_user.employee_id,
        )
        print(f"Created WaterQuality object: {vars(water_quality)}")

        db.session.add(water_quality)
        db.session.commit()
        print("Successfully added water quality data")
        flash("Water quality data added successfully!", "success")
    except Exception as e:
        print(f"Error adding water quality: {str(e)}")
        db.session.rollback()
        flash(f"Error: {str(e)}", "danger")

    return redirect(
        url_for(
            "smart_cultivation_system.smart_cultivation_system_pond", pond_id=pond_id
        )
    )


# Route to add fish data
@bp.route("/<int:pond_id>/add_fish_data", methods=["POST"])
@login_required
def add_fish_data(pond_id):
    fish_form = FishDataForm()

    fish_weight = request.form.get("fish_weight")
    fish_height = request.form.get("fish_height")
    fish_population = request.form.get("fish_population")

    if not (fish_weight and fish_height and fish_population):
        flash("All fields are required.", "danger")
        return redirect(
            url_for("smart_cultivation_system.pond_details", pond_id=pond_id)
        )

    try:
        fish_data = FishData(
            pond_id=pond_id,
            fish_weight=float(fish_weight),
            fish_height=float(fish_height),
            fish_population=int(fish_population),
            employee_id=current_user.employee_id,
        )

        db.session.add(fish_data)
        db.session.commit()
        flash("Fish data added successfully!", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error adding fish data: {str(e)}", "danger")

    return redirect(
        url_for(
            "smart_cultivation_system.smart_cultivation_system_pond", pond_id=pond_id
        )
    )


# Get water quality data by ID
@bp.route("/water_quality/<int:id>", methods=["GET"])
@login_required
def get_water_quality(id):
    water_quality = WaterQuality.query.get_or_404(id)
    return jsonify(
        {
            "pH": water_quality.pH,
            "turbidity": water_quality.turbidity,
            "temperature": water_quality.temperature,
            "nitrate": water_quality.nitrate,
            "ammonia": water_quality.ammonia,
            "dissolved_oxygen": water_quality.dissolved_oxygen,
        }
    )


# Update water quality data
@bp.route("/water_quality/<int:id>/update", methods=["GET", "POST"])
@login_required
def update_water_quality(id):
    water_quality = WaterQuality.query.filter_by(water_quality_id=id).first_or_404()

    if request.method == "GET":
        return jsonify(
            {
                "pH": water_quality.pH,
                "turbidity": water_quality.turbidity,
                "temperature": water_quality.temperature,
                "nitrate": water_quality.nitrate,
                "ammonia": water_quality.ammonia,
                "dissolved_oxygen": water_quality.dissolved_oxygen,
            }
        )

    try:
        water_quality.pH = float(request.form.get("ph"))
        water_quality.turbidity = float(request.form.get("turbidity"))
        water_quality.temperature = float(request.form.get("temperature"))
        water_quality.nitrate = float(request.form.get("nitrate"))
        water_quality.ammonia = float(request.form.get("ammonia"))
        water_quality.dissolved_oxygen = float(request.form.get("dissolved_oxygen"))

        db.session.commit()
        flash("Water quality data updated successfully!", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error updating water quality data: {str(e)}", "danger")

    return redirect(
        url_for(
            "smart_cultivation_system.smart_cultivation_system_pond",
            pond_id=water_quality.pond_id,
        )
    )


# Delete water quality data
@bp.route("/water_quality/<int:id>/delete", methods=["POST"])
@login_required
def delete_water_quality(id):
    print(f"Attempting to delete water quality with ID: {id}")  # Debug print
    water_quality = WaterQuality.query.filter_by(water_quality_id=id).first_or_404()
    pond_id = water_quality.pond_id

    try:
        db.session.delete(water_quality)
        db.session.commit()
        flash("Water quality data deleted successfully!", "success")
    except Exception as e:
        db.session.rollback()
        print(f"Error deleting water quality: {str(e)}")  # Debug print
        flash(f"Error deleting water quality data: {str(e)}", "danger")

    return redirect(
        url_for(
            "smart_cultivation_system.smart_cultivation_system_pond", pond_id=pond_id
        )
    )


# Get fish data by ID
@bp.route("/fish_data/<int:id>", methods=["GET"])
@login_required
def get_fish_data(id):
    fish_data = FishData.query.filter_by(fish_data_id=id).first_or_404()
    return jsonify(
        {
            "fish_weight": fish_data.fish_weight,
            "fish_height": fish_data.fish_height,
            "fish_population": fish_data.fish_population,
        }
    )


# Update fish data
@bp.route("/fish_data/<int:id>/update", methods=["POST"])
@login_required
def update_fish_data(id):
    fish_data = FishData.query.filter_by(fish_data_id=id).first_or_404()

    try:
        fish_data.fish_weight = float(request.form.get("fish_weight"))
        fish_data.fish_height = float(request.form.get("fish_height"))
        fish_data.fish_population = int(request.form.get("fish_population"))

        db.session.commit()
        flash("Fish data updated successfully!", "success")
    except Exception as e:
        db.session.rollback()
        print(f"Error updating fish data: {str(e)}")  # Debug print
        flash(f"Error updating fish data: {str(e)}", "danger")

    return redirect(
        url_for(
            "smart_cultivation_system.smart_cultivation_system_pond",
            pond_id=fish_data.pond_id,
        )
    )


# Delete fish data
@bp.route("/fish_data/<int:id>/delete", methods=["POST"])
@login_required
def delete_fish_data(id):
    fish_data = FishData.query.filter_by(fish_data_id=id).first_or_404()
    pond_id = fish_data.pond_id

    try:
        db.session.delete(fish_data)
        db.session.commit()
        flash("Fish data deleted successfully!", "success")
    except Exception as e:
        db.session.rollback()
        print(f"Error deleting fish data: {str(e)}")  # Debug print
        flash(f"Error deleting fish data: {str(e)}", "danger")

    return redirect(
        url_for(
            "smart_cultivation_system.smart_cultivation_system_pond", pond_id=pond_id
        )
    )


@bp.route("/employee/<int:id>/update", methods=["GET", "POST"])
@login_required
def update_employee(id):
    employee = Employee.query.filter_by(employee_id=id).first_or_404()

    # Check if current user is the owner of this employee
    if employee.user_id != current_user.user_id:
        flash("You don't have permission to edit this employee.", "danger")
        return redirect(url_for("smart_cultivation_system.owner_dashboard"))

    if request.method == "GET":
        # Get all ponds owned by the current user
        user_ponds = Pond.query.filter_by(owner_id=current_user.user_id).all()
        # Get the IDs of ponds assigned to this employee
        assigned_pond_ids = [pond.pond_id for pond in employee.ponds]

        return jsonify(
            {
                "employee_name": employee.employee_name,
                "employee_email": employee.employee_email,
                "assigned_ponds": assigned_pond_ids,
                "available_ponds": [
                    {"id": pond.pond_id, "name": pond.pond_name} for pond in user_ponds
                ],
            }
        )

    try:
        employee.employee_name = request.form.get("employee_name")
        employee.employee_email = request.form.get("employee_email")

        # Update password only if provided
        new_password = request.form.get("password")
        if new_password:
            employee.password_hash = generate_password_hash(new_password)

        # Update pond assignments
        selected_pond_ids = request.form.getlist("ponds")
        employee.ponds = []  # Clear existing assignments
        for pond_id in selected_pond_ids:
            pond = Pond.query.get(pond_id)
            if pond and pond.owner_id == current_user.user_id:
                employee.ponds.append(pond)

        db.session.commit()
        flash("Employee updated successfully!", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error updating employee: {str(e)}", "danger")

    return redirect(url_for("smart_cultivation_system.owner_dashboard"))


@bp.route("/employee/<int:id>/delete", methods=["POST"])
@login_required
def delete_employee(id):
    employee = Employee.query.filter_by(employee_id=id).first_or_404()

    # Check if current user is the owner of this employee
    if employee.user_id != current_user.user_id:
        flash("You don't have permission to delete this employee.", "danger")
        return redirect(url_for("smart_cultivation_system.owner_dashboard"))

    try:
        db.session.delete(employee)
        db.session.commit()
        flash("Employee deleted successfully!", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error deleting employee: {str(e)}", "danger")

    return redirect(url_for("smart_cultivation_system.owner_dashboard"))


@bp.route("/pond/<int:pond_id>/report/excel")
@login_required
def download_excel_report(pond_id):
    pond = get_pond_by_id(pond_id)
    if pond is None:
        flash("Pond not found", "danger")
        return redirect(url_for("smart_cultivation_system.owner_dashboard"))

    waterQualities = get_water_quality_by_pond_id(pond_id)
    fishData = get_fish_data_by_pond_id(pond_id)
    metrics = get_metrics_by_pond_id(pond_id)

    # Get latest water quality data from the template format
    latest_water_quality = (
        water_quality_to_dict(waterQualities[-1])
        if waterQualities
        else {
            "date": "",
            "pH": 7.0,
            "turbidity": 0.0,
            "temperature": 25.0,
        }
    )

    output = generate_excel_report(
        pond, waterQualities, fishData, metrics, latest_water_quality
    )

    return send_file(
        output,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        as_attachment=True,
        download_name=f'pond_{pond_id}_report_{datetime.now().strftime("%Y%m%d")}.xlsx',
    )


@bp.route("/pond/<int:pond_id>/report/pdf")
@login_required
def download_pdf_report(pond_id):
    pond = get_pond_by_id(pond_id)
    if pond is None:
        flash("Pond not found", "danger")
        return redirect(url_for("smart_cultivation_system.owner_dashboard"))

    waterQualities = get_water_quality_by_pond_id(pond_id)
    fishData = get_fish_data_by_pond_id(pond_id)
    metrics = get_metrics_by_pond_id(pond_id)

    # Get latest water quality data from the template format
    latest_water_quality = (
        water_quality_to_dict(waterQualities[-1])
        if waterQualities
        else {
            "date": "",
            "pH": 7.0,
            "turbidity": 0.0,
            "temperature": 25.0,
        }
    )

    output = generate_pdf_report(
        pond, waterQualities, fishData, metrics, latest_water_quality
    )

    return send_file(
        output,
        mimetype="application/pdf",
        as_attachment=True,
        download_name=f'pond_{pond_id}_report_{datetime.now().strftime("%Y%m%d")}.pdf',
    )


@bp.route("/dashboard")
@login_required
def dashboard():
    # Redirect based on user role after authentication
    if current_user.role == "user":
        return redirect(url_for("smart_cultivation_system.owner_dashboard"))
    elif current_user.role == "employee":
        return redirect(url_for("smart_cultivation_system.employee_dashboard"))
    else:
        print(current_user.role)
        flash("Access denied.", "danger")
        return redirect(url_for("login.login"))  # Redirect to login if role is not recognized