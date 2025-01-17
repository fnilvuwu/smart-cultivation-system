from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    SubmitField,
    PasswordField,
    SelectMultipleField,
    FloatField,
    IntegerField,
)
from wtforms.validators import DataRequired, Email, NumberRange


class InsertPondForm(FlaskForm):
    pond_name = StringField("Pond Name", validators=[DataRequired()])
    location = StringField("Location", validators=[DataRequired()])
    # Adding a SelectMultipleField for employees
    employees = SelectMultipleField("Assign Employees", coerce=int)
    submit = SubmitField("Submit")


class InsertEmployeeForm(FlaskForm):
    employee_name = StringField("Employee Name", validators=[DataRequired()])
    employee_email = StringField("Employee Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    ponds = SelectMultipleField("Ponds", coerce=int, validators=[DataRequired()])
    submit = SubmitField("Submit")


class WaterQualityForm(FlaskForm):
    pH = FloatField('pH Level', validators=[DataRequired()])
    turbidity = FloatField('Turbidity', validators=[DataRequired()])
    temperature = FloatField('Temperature', validators=[DataRequired()])
    nitrate = FloatField('Nitrate', validators=[DataRequired()])
    # Adding new fields for ammonia and dissolved oxygen
    ammonia = FloatField('Ammonia Level', validators=[DataRequired()])
    dissolved_oxygen = FloatField('Dissolved Oxygen Level', validators=[DataRequired()])
    submit = SubmitField("Submit Water Quality Data")


class FishDataForm(FlaskForm):
    fish_weight = FloatField(
        "Fish Weight (grams)", validators=[DataRequired(), NumberRange(min=0)]
    )
    fish_height = FloatField(
        "Fish Height (cm)", validators=[DataRequired(), NumberRange(min=0)]
    )
    fish_population = IntegerField(
        "Fish Population", validators=[DataRequired(), NumberRange(min=1)]
    )
    submit = SubmitField("Submit Fish Data")
