from flask import Flask, request, jsonify
from ai_models import fetch_user_data, calculate_bmr, calculate_tdee, create_nutrition_plan, generate_plan_with_foods
from firebase_config import db
import pandas as pd
import os
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Bật CORS


@app.route('/calculate-bmr', methods=['POST'])
def calculate_bmr_route():
    user = request.json
    bmr = calculate_bmr(user)
    return jsonify(bmr=bmr)

@app.route('/calculate-tdee', methods=['POST'])
def calculate_tdee_route():
    data = request.json
    user = data['user']
    bmr = data['bmr']
    tdee = calculate_tdee(user, bmr)
    return jsonify(tdee=tdee)

@app.route('/create-nutrition-plan', methods=['POST'])
def create_nutrition_plan_route():
    data = request.json
    user = data['user']
    tdee = data['tdee']
    plan = create_nutrition_plan(user, tdee)
    return jsonify(plan=plan)

@app.route('/generate-plan', methods=['POST'])
def generate_plan_route():
    try:
        data = request.json
        uid = data['uid']
        user = fetch_user_data(uid)

        # Lấy đường dẫn tuyệt đối
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        CSV_PATH = os.path.join(BASE_DIR, "data/NutrientValues.csv")

        nutrient_data = pd.read_csv(CSV_PATH)


        # Generate the plan with foods
        plan = generate_plan_with_foods(user, uid, nutrient_data)

        return jsonify(plan=plan)
    except Exception as e:
        return jsonify(error=str(e)), 500

@app.route('/test-fetch-user/<uid>', methods=['GET'])
def test_fetch_user(uid):
    try:
        user = fetch_user_data(uid)
        return jsonify(user=user)
    except Exception as e:
        return jsonify(error=str(e)), 500

if __name__ == '__main__':
    PORT = int(os.environ.get("PORT", 5000))  # Render sẽ tự cấp PORT
    app.run(host='0.0.0.0', port=PORT)