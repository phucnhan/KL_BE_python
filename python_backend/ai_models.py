import numpy as np
from firebase_config import db
import pandas as pd

def fetch_user_data(uid):
    user_ref = db.collection('usersdata').document(uid)
    user_doc = user_ref.get()
    if user_doc.exists:
        return user_doc.to_dict()
    else:
        raise ValueError("User not found")

def calculate_bmr(user):
    if user['gender'] == 'male':
        return 88.362 + (13.397 * user['weight']) + (4.799 * user['height']) - (5.677 * user['age'])
    else:
        return 447.593 + (9.247 * user['weight']) + (3.098 * user['height']) - (4.330 * user['age'])

def calculate_tdee(user, bmr):
    activity_factor = {
        'Sedentary': 1.2,
        'Light': 1.375,
        'Moderate': 1.55,
        'High': 1.725,
        'Athlete': 1.9
    }
    return bmr * activity_factor[user['activityLevel']]

def map_food_to_nutrients(selected_foods, nutrient_data):
    nutrient_data.columns = [col.strip() for col in nutrient_data.columns]
    filtered_data = nutrient_data[nutrient_data['Main food description'].isin(selected_foods)]
    return filtered_data[['Main food description', 'Energy (kcal)', 'Protein (g)', 'Carbohydrate (g)', 'Total Fat (g)']]

def generate_plan_with_foods(user, uid, nutrient_data):
    days = {
        'Recommended': 90,
        'fast': 30,
        'slow': 180
    }
    plan_days = days[user['selectedOption']]
    bmr = calculate_bmr(user)
    tdee = calculate_tdee(user, bmr)

    selected_foods = user['selectedFoods']['Carbs'] + user['selectedFoods']['Proteins'] + user['selectedFoods']['Fats']
    food_nutrients = map_food_to_nutrients(selected_foods, nutrient_data)

    plan_list = []
    for day in range(plan_days):
        daily_variation = np.random.uniform(-0.05, 0.05)
        calories = round(tdee * (1 + daily_variation))
        protein = round(user['weight'] * 2.2 * (1 + daily_variation))
        fat = round(calories * 0.25 / 9 * (1 + daily_variation))
        carbs = round((calories - (protein * 4 + fat * 9)) / 4 * (1 + daily_variation))

        daily_foods = []
        remaining_calories = calories

        for _, food in food_nutrients.iterrows():
            if remaining_calories <= 0:
                break
            portion = min(remaining_calories, food['Energy (kcal)'])
            daily_foods.append({
                'food': food['Main food description'],
                'portion': round(portion / food['Energy (kcal)'] * 100, 2)
            })
            remaining_calories -= portion

        plan_list.append({
            'day': day + 1,
            'calories': calories,
            'protein': protein,
            'fat': fat,
            'carbs': carbs,
            'foods': daily_foods
        })

    plan_ref = db.collection('usersdata').document(uid).collection('nutritionPlans')
    for day_plan in plan_list:
        plan_ref.add(day_plan)
def create_nutrition_plan(user, tdee):
    if user['goal'] == 'lose weight':
        goal_calories = tdee - 500
    elif user['goal'] == 'gain muscle':
        goal_calories = tdee + 500
    else:
        goal_calories = tdee

    protein = user['weight'] * 2.2  # 2.2g protein per kg body weight
    fat = goal_calories * 0.25 / 9  # 25% calories from fat
    carbs = (goal_calories - (protein * 4) - (fat * 9)) / 4  # Remaining calories from carbs

    return {
        'calories': round(goal_calories),
        'protein': round(protein),
        'fat': round(fat),
        'carbs': round(carbs)
    }

    return plan_list
