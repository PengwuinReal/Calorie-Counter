import os
import requests
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("SPOONACULAR_API_KEY")
BASE_URL = "https://api.spoonacular.com"

def get_nutrition(food_name):
    # Step 1: Search for recipe
    search_url = f"{BASE_URL}/recipes/complexSearch"
    search_params = {
        "query": food_name,
        "number": 1,
        "apiKey": API_KEY
    }

    search_response = requests.get(search_url, params=search_params)
    if search_response.status_code != 200:
        print(str(search_response.status_code))
        return {"error": "API request failed."}

    search_data = search_response.json()
    if not search_data["results"]:
        return {"error": "Food not found."}

    recipe = search_data["results"][0]
    recipe_id = recipe["id"]

    # Step 2: Get full info with nutrition
    info_url = f"{BASE_URL}/recipes/{recipe_id}/information"
    info_params = {
        "includeNutrition": True,
        "apiKey": API_KEY
    }

    info_response = requests.get(info_url, params=info_params)
    if info_response.status_code != 200:
        return {"error": "Failed to retrieve detailed nutrition info."}

    info_data = info_response.json()
    nutrients = info_data.get("nutrition", {}).get("nutrients", [])

    def get_nutrient(name):
        for n in nutrients:
            if n["name"].lower() == name.lower():
                return n["amount"]
        return "N/A"

    calories = get_nutrient("Calories")
    protein = get_nutrient("Protein")
    fat = get_nutrient("Fat")
    carbs = get_nutrient("Carbohydrates")

    return {
        "title": info_data.get("title", food_name),
        "calories": calories,
        "protein": protein,
        "fat": fat,
        "carbs": carbs,
        "summary": info_data.get("summary", "No summary available."),
        "image": info_data.get("image", ""),
        "source": info_data.get("sourceUrl", ""),
        "timestamp": info_data.get("timestamp", "")
    }
