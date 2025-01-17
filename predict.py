from flask import Blueprint, render_template, request, redirect, url_for, flash
import pickle
import os
import numpy as np
from cache import cache

bp = Blueprint("predict", __name__, url_prefix="/predict")

# Load the models
model_paths = {
    'length': 'best_model_fish_length_(cm).pkl',
    'weight': 'best_model_fish_weight_(g).pkl',
    'quality': 'best_model_water_quality_score.pkl'
}

models = {}
for key, path in model_paths.items():
    if os.path.exists(path):
        with open(path, 'rb') as model_file:
            models[key] = pickle.load(model_file)
    else:
        print(f"Warning: Model file '{path}' not found. {key} predictions will be unavailable.")
        models[key] = None


def get_water_quality_category(fish_health_condition_factor):
    """
    Determine the water quality category based on fish health condition factor.
    """
    if fish_health_condition_factor < 0.8:
        return 'poor'
    elif 0.8 <= fish_health_condition_factor < 1.0:
        return 'fair'
    elif 1.0 <= fish_health_condition_factor < 1.2:
        return 'normal'
    elif 1.2 <= fish_health_condition_factor < 1.4:
        return 'good'
    else:
        return 'excellent'


def predict_water_quality(temperature, turbidity, dissolved_oxygen, ph, ammonia, nitrate):
    """
    Predict the water quality category based on fish health condition factor,
    which is derived from fish length, weight, and water quality models.
    """

    # Prepare input data for prediction
    input_data = [[temperature, turbidity, dissolved_oxygen, ph, ammonia, nitrate]]

    # Make predictions using the models
    fish_length = (
        models['length'].predict(input_data)[0] if models['length'] else None
    )
    fish_weight = (
        models['weight'].predict(input_data)[0] if models['weight'] else None
    )
    water_quality = (
        models['quality'].predict(input_data)[0] if models['quality'] else None
    )

    # If predictions are available, calculate the fish condition factor
    if isinstance(fish_length, (np.float32, float)) and isinstance(fish_weight, (np.float32, float)):
        fish_condition_factor = (100 * fish_weight) / (fish_length ** 3)
    else:
        fish_condition_factor = None

    # Determine water quality category based on the fish health condition factor
    if isinstance(fish_condition_factor, (np.float32, float)):
        water_quality_category = get_water_quality_category(fish_condition_factor)
    else:
        water_quality_category = "Cannot determine"

    return {
        'length': fish_length,
        'weight': fish_weight,
        'quality': water_quality,
        'quality_category': water_quality_category,
        'fish_condition_factor': fish_condition_factor
    }


def get_quality_grade(temperature, turbidity, dissolved_oxygen, ph, ammonia, nitrate):
    """
    Get the water quality grade category based on parameters for database storage.
    This method is used to determine the 'quality_grade' field in the database.
    """
    predictions = predict_water_quality(temperature, turbidity, dissolved_oxygen, ph, ammonia, nitrate)
    return predictions['quality_category']


@bp.route('/', methods=['GET', 'POST'])
def predict():
    if request.method == 'POST':
        try:
            # Parse input data
            temperature = float(request.form['temperature'])
            turbidity = float(request.form['turbidity'])
            dissolved_oxygen = float(request.form['dissolved_oxygen'])
            ph = float(request.form['ph'])
            ammonia = float(request.form['ammonia'])
            nitrate = float(request.form['nitrate'])

            # Validate the input values
            if not (20 <= temperature <= 35):
                raise ValueError("Temperature must be between 20 and 35°C")
            if not (0 <= turbidity <= 100):
                raise ValueError("Turbidity must be between 0 and 100 NTU")
            if not (0 <= dissolved_oxygen <= 20):
                raise ValueError("Dissolved Oxygen must be between 0 and 20 mg/L")
            if not (1 <= ph <= 14):
                raise ValueError("pH must be between 1 and 14")
            if not (0 <= ammonia <= 1):
                raise ValueError("Ammonia must be between 0 and 1 mg/L")
            if not (1 <= nitrate <= 100):
                raise ValueError("Nitrate must be between 1 and 100 mg/L")

            # Call the predict_water_quality function
            predictions = predict_water_quality(
                temperature, turbidity, dissolved_oxygen, ph, ammonia, nitrate
            )

            return render_template(
                'pages/smart_cultivation_system/predict.html',
                predictions=predictions
            )
        except ValueError as e:
            flash(str(e))
            return redirect(url_for('predict.predict'))

    # Render empty form for GET requests
    return render_template('pages/smart_cultivation_system/predict.html', predictions=None)
