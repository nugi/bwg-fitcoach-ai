"""Public Nutrition and Food API integration using USDA FoodData Central."""

import json
import os
import urllib.parse
import urllib.request
from typing import Any


def lookup_food_nutrition(food_name: str, max_results: int = 2) -> list[dict[str, Any]]:
    """Look up real macronutrient and caloric data for any food item using the USDA FoodData Central public API.

    Args:
        food_name: The name of the food or ingredient to search for (e.g., 'chicken breast', 'greek yogurt', 'rolled oats').
        max_results: Maximum number of matching food items to return (default: 2).

    Returns:
        A list of food items with description, brand/origin, serving info, and macronutrients (calories, protein, carbs, fat).
    """
    api_key = os.environ.get("USDA_API_KEY", "DEMO_KEY")
    encoded_query = urllib.parse.quote(food_name.strip())
    url = f"https://api.nal.usda.gov/fdc/v1/foods/search?query={encoded_query}&pageSize={max_results}&api_key={api_key}"

    req = urllib.request.Request(url, headers={"User-Agent": "FitCoachAI/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        return [{"error": f"Failed to fetch nutrition data from USDA API: {e}"}]

    results = []
    for food in data.get("foods", []):
        nutrients = {}
        for n in food.get("foodNutrients", []):
            name = n.get("nutrientName", "").lower()
            val = n.get("value")
            unit = n.get("unitName", "")
            if "energy" in name and unit.upper() == "KCAL":
                nutrients["calories_kcal"] = val
            elif "protein" in name and "protein_g" not in nutrients:
                nutrients["protein_g"] = val
            elif "carbohydrate" in name and "carbs_g" not in nutrients:
                nutrients["carbs_g"] = val
            elif ("total lipid" in name or "fat" in name) and "fat_g" not in nutrients:
                nutrients["fat_g"] = val

        results.append({
            "description": food.get("description"),
            "brand": food.get("brandOwner") or food.get("brandName") or "Generic / Whole Food",
            "serving_size": f"{food.get('servingSize', 100)} {food.get('servingSizeUnit', 'g')}",
            "nutrients": nutrients,
        })

    return results
