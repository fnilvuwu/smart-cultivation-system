from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired


class InsertTrackerForm(FlaskForm):
    name = StringField("Nama", validators=[DataRequired()])
    description = StringField("Deskripsi")
    asset_img_url = StringField("Foto Aset")
    tracker_img_url = StringField("Foto Tracker")
    submit = SubmitField("Submit")
