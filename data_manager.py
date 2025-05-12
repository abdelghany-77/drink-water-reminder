import json
import os
from datetime import datetime
class DataManager:
  def __init__(self, filename="user_data.json"):
    self.filename = filename

    # Get username from environment or default to provided value
    username = os.environ.get('USERNAME', 'abdelghany-77')

    # Get last login from environment or default to provided value
    last_login = os.environ.get('LAST_LOGIN', '2025-05-11 16:54:02')

    self.default_data = {
      "weight": 70,
      "weight_unit": "kg",
      "activity_level": "moderate",
      "reminder_interval": 60,
      "daily_target": 2000,
      "current_intake": 0,
      "last_reset_date": datetime.now().strftime("%Y-%m-%d"),
      "reminder_active": False,
      "sound_enabled": True,
      "start_minimized": False,
      "custom_reminders": [],
      "history": {},  # Track daily intake history
      "user_info": {
        "username": username,
        "last_login": last_login
      }
    }

  def load_data(self):
    """Load user data from the JSON file"""
    if os.path.exists(self.filename):
      try:
        with open(self.filename, "r") as f:
          data = json.load(f)

          # Update last login time
          if "user_info" not in data:
            data["user_info"] = {}

          data["user_info"]["last_login"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

          # Check if date has changed since last use
          current_date = datetime.now().strftime("%Y-%m-%d")
          if current_date != data.get("last_reset_date", ""):
            # Save yesterday's data to history before resetting
            self.archive_daily_data(data)

            # Reset daily intake
            data["current_intake"] = 0
            data["last_reset_date"] = current_date

          return data
      except Exception as e:
        print(f"Error loading data: {e}")

    # Return default data if file doesn't exist or can't be loaded
    default = self.default_data.copy()
    default["user_info"]["last_login"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return default

  def save_data(self, data):
    """Save user data to the JSON file"""
    try:
      # Ensure the history is updated
      data = self.update_history(data)

      with open(self.filename, "w") as f:
        json.dump(data, f, indent=2)
      return True
    except Exception as e:
      print(f"Error saving data: {e}")
      return False

  def archive_daily_data(self, data):
    """Archive the previous day's data to history"""
    if "last_reset_date" in data and data["last_reset_date"]:
      prev_date = data["last_reset_date"]
      if "history" not in data:
        data["history"] = {}

      # Store the full data for that day
      data["history"][prev_date] = {
        "intake": data["current_intake"],
        "target": data["daily_target"],
        "percentage": round((data["current_intake"] / data["daily_target"]) * 100 if data["daily_target"] > 0 else 0, 1)
      }

  def update_history(self, data):
    """Update the history with today's intake"""
    today = datetime.now().strftime("%Y-%m-%d")
    if "history" not in data:
      data["history"] = {}

    # Update today's entry (without replacing the full entry if it exists)
    if today not in data["history"]:
      data["history"][today] = {}

    data["history"][today] = {
      "intake": data["current_intake"],
      "target": data["daily_target"],
      "percentage": round((data["current_intake"] / data["daily_target"]) * 100 if data["daily_target"] > 0 else 0, 1)
    }

    return data

  def get_weekly_stats(self, data):
    """Get water intake statistics for the last 7 days"""
    if "history" not in data:
      return []

    # Sort history by date (most recent first)
    sorted_dates = sorted(data["history"].keys(), reverse=True)

    # Get last 7 days with data
    recent_days = sorted_dates[:7]

    stats = []
    for date in sorted(recent_days):  # Sort chronologically for display
      if date in data["history"]:
        entry = data["history"][date]
        stats.append({
          "date": date,
          "intake": entry.get("intake", 0),
          "target": entry.get("target", data["daily_target"]),
          "percentage": entry.get("percentage", 0)
        })

    return stats

  def export_history_to_csv(self, data, filename="water_history.csv"):
    """Export drinking history to a CSV file"""
    try:
      if "history" not in data or not data["history"]:
        return False, "No history data to export"

      import csv
      with open(filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        # Write header
        writer.writerow(['Date', 'Water Intake (ml)', 'Daily Target (ml)', 'Percentage'])

        # Sort dates
        sorted_dates = sorted(data["history"].keys())

        # Write data
        for date in sorted_dates:
          entry = data["history"][date]
          writer.writerow([
            date,
            entry.get("intake", 0),
            entry.get("target", 0),
            entry.get("percentage", 0)
          ])

      return True, f"History exported to {filename}"
    except Exception as e:
      return False, f"Error exporting history: {e}"

  def is_dehydrated(self, data):
    """Check if user is chronically below water targets"""
    if "history" not in data or len(data["history"]) < 3:
      return False

    # Check the last 3 days
    sorted_dates = sorted(data["history"].keys(), reverse=True)
    recent_days = sorted_dates[:3]

    below_target_count = 0
    for date in recent_days:
      entry = data["history"][date]
      if entry.get("percentage", 0) < 80:  # Below 80% of target
        below_target_count += 1

    # If 2 or more days were below 80% of target
    return below_target_count >= 2