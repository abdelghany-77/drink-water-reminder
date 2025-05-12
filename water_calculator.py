def calculate_water_intake(weight, weight_unit, activity_level):
  """
    Calculate the recommended daily water intake based on weight and activity level.

    Parameters:
    - weight: The user's weight
    - weight_unit: "kg" or "lbs"
    - activity_level: "sedentary", "light", "moderate", "active", or "very active"

    Returns: Recommended daily water intake in ml
    """
  # Convert to kg if needed
  if weight_unit == "lbs":
    weight = weight * 0.453592

  # Base calculation: 30-35ml per kg of body weight
  base_intake = weight * 30

  # Adjust for activity level
  activity_multipliers = {
    "sedentary": 1.0,
    "light": 1.1,
    "moderate": 1.2,
    "active": 1.3,
    "very active": 1.4
  }

  multiplier = activity_multipliers.get(activity_level, 1.0)
  total_intake = base_intake * multiplier

  # Round to nearest 50ml
  return round(total_intake / 50) * 50