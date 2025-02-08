from flask import Flask, request, jsonify
from ai_models import fetch_user_data, calculate_bmr, calculate_tdee, create_nutrition_plan, generate_plan_with_foods
from firebase_config import db
import pandas as pd
import os
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Allow CORS for all origins


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
        uid = data.get('uid')

        print(f"Received request for UID: {uid}")  # In UID ra log

        user = fetch_user_data(uid)
        print(f"User data: {user}")  # In dữ liệu user ra log

        # Load nutrient data từ CSV
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        CSV_PATH = os.path.join(BASE_DIR, '..', 'data', 'NutrientValues.csv')
        nutrient_data = pd.read_csv(CSV_PATH)
        print("Loaded nutrient data successfully")  # Xác nhận đã load CSV

        # Tạo kế hoạch dinh dưỡng
        plan = generate_plan_with_foods(user, uid, nutrient_data)
        print("Generated nutrition plan")  # Xác nhận đã tạo kế hoạch

        # Xóa kế hoạch cũ trước khi lưu kế hoạch mới
        user_ref = db.collection('usersdata').document(uid).collection('nutritionPlans')
        old_plans = user_ref.stream()
        for plan_doc in old_plans:
            user_ref.document(plan_doc.id).delete()
        print("Deleted old nutrition plans")  # Xác nhận đã xóa kế hoạch cũ

        # Lưu kế hoạch mới vào Firestore
        for day_plan in plan:
            user_ref.add(day_plan)

        print("Saved new nutrition plan to Firestore")  # Xác nhận đã lưu kế hoạch mới

        return jsonify(success=True, plan=plan)
    except Exception as e:
        print(f"Error in generate-plan: {str(e)}")  # In lỗi ra log
        return jsonify(error=str(e)), 500

@app.route('/test-fetch-user/<uid>', methods=['GET'])
def test_fetch_user(uid):
    try:
        user = fetch_user_data(uid)
        if not user:
            return jsonify(error=f"No user data found for UID: {uid}"), 404
        return jsonify(user=user)
    except Exception as e:
        return jsonify(error=str(e)), 500

@app.route('/api/user-data/<uid>/nutritionPlans', methods=['GET'])
def get_nutrition_plans(uid):
    try:
        # Lấy reference đến nutritionPlans collection trong Firestore
        plans_ref = db.collection('usersdata').document(uid).collection('nutritionPlans')
        docs = plans_ref.stream()

        # Duyệt qua tất cả các document và tạo danh sách
        plans = []
        for doc in docs:
            plans.append(doc.to_dict())

        return jsonify(plans=plans), 200
    except Exception as e:
        print(f"Error fetching nutrition plans: {str(e)}")
        return jsonify(error=f"Failed to fetch nutrition plans: {str(e)}"), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)