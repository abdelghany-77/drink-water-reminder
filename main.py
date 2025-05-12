import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
import sys
from datetime import datetime
import threading
import time
import platform
import pygame

from data_manager import DataManager
from water_calculator import calculate_water_intake
from notification_manager import NotificationManager
from reminder_scheduler import ReminderScheduler
from startup_manager import add_to_startup, remove_from_startup, is_in_startup
from system_tray import SystemTray
if sys.platform == 'win32':
  import ctypes
  # Hide console window
  ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)

class WaterReminderApp:
  def __init__(self, root):
    self.root = root
    self.root.title("Water Reminder")
    self.root.geometry("600x550")
    self.root.resizable(False, False)

    # Current Date and Time (UTC)
    current_time = "2025-05-11 16:47:15"  # Your provided time
    current_user = "abdelghany-77"  # Your provided username

    # Set app icon
    self.icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "images", "water_icon.png")
    try:
      self.root.iconphoto(False, tk.PhotoImage(file=self.icon_path))
    except Exception as e:
      print(f"Could not load icon: {e}")

    # Initialize pygame for sounds
    pygame.init()

    # Initialize components
    self.data_manager = DataManager()
    self.notification_manager = NotificationManager()
    self.reminder_scheduler = ReminderScheduler(self.notification_manager)
    self.user_data = self.data_manager.load_data()

    # Update user info
    if "user_info" not in self.user_data:
      self.user_data["user_info"] = {}
    self.user_data["user_info"]["username"] = current_user
    self.user_data["user_info"]["last_login"] = current_time

    self.reminder_active = False
    self.reminder_thread = None

    # Set up UI after data is loaded
    self.setup_ui()

    # Load and schedule custom reminders
    if "custom_reminders" in self.user_data:
      self.reminder_scheduler.load_reminders(self.user_data["custom_reminders"])

    # Start reminder if already active
    if self.user_data.get("reminder_active", False):
      self.toggle_reminder()

    # Set up system tray - must be done before withdrawing window
    if os.path.exists(self.icon_path):
      self.system_tray = SystemTray(root, self, self.icon_path)

    # IMPORTANT: Start minimized by default
    self.root.withdraw()
    self.is_visible = False

    # Set up system sleep/resume handler
    self.handle_system_resume()

    # Save initial user data
    self.save_user_data()

  def load_user_data(self):
    if os.path.exists("user_data.json"):
      try:
        with open("user_data.json", "r") as f:
          return json.load(f)
      except Exception as e:
        print(f"Error loading user data: {e}")
    return {
      "weight": 70,
      "weight_unit": "kg",
      "activity_level": "moderate",
      "reminder_interval": 60,
      "daily_target": 2000,
      "current_intake": 0,
      "last_reset_date": datetime.now().strftime("%Y-%m-%d"),
      "reminder_active": False,
      "sound_enabled": True,
      "custom_reminders": []
    }

  def save_user_data(self):
    self.user_data["custom_reminders"] = self.reminder_scheduler.to_list()
    self.data_manager.save_data(self.user_data)

    try:
      with open("user_data.json", "w") as f:
        json.dump(self.user_data, f)
    except Exception as e:
      print(f"Error saving user data: {e}")
      messagebox.showerror("Error", f"Could not save your settings: {e}")

  def setup_ui(self):
    notebook = ttk.Notebook(self.root)
    notebook.pack(fill="both", expand=True, padx=10, pady=10)

    # Dashboard tab
    dashboard_frame = ttk.Frame(notebook)
    notebook.add(dashboard_frame, text="Dashboard")

    # Settings tab
    settings_frame = ttk.Frame(notebook)
    notebook.add(settings_frame, text="Settings")

    # Reminders tab (new)
    reminders_frame = ttk.Frame(notebook)
    notebook.add(reminders_frame, text="Custom Reminders")

    self.setup_dashboard(dashboard_frame)
    self.setup_settings(settings_frame)
    self.setup_reminders_tab(reminders_frame)

  def setup_dashboard(self, parent):
    # Current date display
    date_label = ttk.Label(
      parent,
      text=f"Today: {datetime.now().strftime('%Y-%m-%d')}",
      font=("Arial", 12)
    )
    date_label.grid(row=0, column=0, columnspan=2, pady=10, sticky="w")

    # Water target display
    target_frame = ttk.LabelFrame(parent, text="Daily Target")
    target_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

    self.target_label = ttk.Label(
      target_frame,
      text=f"{self.user_data['daily_target']} ml",
      font=("Arial", 24)
    )
    self.target_label.pack(pady=20)

    # Current intake display
    intake_frame = ttk.LabelFrame(parent, text="Current Intake")
    intake_frame.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")

    self.intake_label = ttk.Label(
      intake_frame,
      text=f"{self.user_data['current_intake']} ml",
      font=("Arial", 24)
    )
    self.intake_label.pack(pady=20)

    # Progress bar
    progress_frame = ttk.LabelFrame(parent, text="Today's Progress")
    progress_frame.grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")

    self.progress_var = tk.DoubleVar()
    self.progress = ttk.Progressbar(
      progress_frame,
      variable=self.progress_var,
      maximum=100,
      length=400
    )
    self.progress.pack(pady=20)
    self.update_progress()

    # Add water buttons
    buttons_frame = ttk.Frame(parent)
    buttons_frame.grid(row=3, column=0, columnspan=2, pady=20)

    amounts = [100, 200, 300, 500]
    for i, amount in enumerate(amounts):
      btn = ttk.Button(
        buttons_frame,
        text=f"+ {amount} ml",
        command=lambda a=amount: self.add_water(a)
      )
      btn.grid(row=0, column=i, padx=10)

    # Reminder control
    reminder_frame = ttk.Frame(parent)
    reminder_frame.grid(row=4, column=0, columnspan=2, pady=10)

    self.reminder_btn_text = tk.StringVar()
    self.reminder_btn_text.set("Start Reminders")

    self.reminder_btn = ttk.Button(
      reminder_frame,
      textvariable=self.reminder_btn_text,
      command=self.toggle_reminder
    )
    self.reminder_btn.pack()

    self.status_label = ttk.Label(reminder_frame, text="Reminders inactive")
    self.status_label.pack(pady=5)

    # Sound toggle
    self.sound_var = tk.BooleanVar(value=self.user_data.get("sound_enabled", True))
    sound_check = ttk.Checkbutton(
      reminder_frame,
      text="Enable Sound Alerts",
      variable=self.sound_var,
      command=self.toggle_sound
    )
    sound_check.pack(pady=5)

    # Reset button
    reset_btn = ttk.Button(
      parent,
      text="Reset Today's Progress",
      command=self.reset_progress
    )
    reset_btn.grid(row=5, column=0, columnspan=2, pady=20)

  def setup_settings(self, parent):
    # Weight settings
    weight_frame = ttk.LabelFrame(parent, text="Personal Information")
    weight_frame.pack(fill="x", padx=10, pady=10)

    ttk.Label(weight_frame, text="Weight:").grid(row=0, column=0, padx=5, pady=10, sticky="w")

    self.weight_var = tk.StringVar(value=str(self.user_data["weight"]))
    weight_entry = ttk.Entry(weight_frame, width=10, textvariable=self.weight_var)
    weight_entry.grid(row=0, column=1, padx=5, pady=10)

    self.weight_unit_var = tk.StringVar(value=self.user_data["weight_unit"])
    weight_unit = ttk.Combobox(
      weight_frame,
      values=["kg", "lbs"],
      textvariable=self.weight_unit_var,
      width=5,
      state="readonly"
    )
    weight_unit.grid(row=0, column=2, padx=5, pady=10)

    # Activity level
    ttk.Label(weight_frame, text="Activity Level:").grid(row=1, column=0, padx=5, pady=10, sticky="w")

    self.activity_var = tk.StringVar(value=self.user_data["activity_level"])
    activity = ttk.Combobox(
      weight_frame,
      values=["sedentary", "light", "moderate", "active", "very active"],
      textvariable=self.activity_var,
      width=15,
      state="readonly"
    )
    activity.grid(row=1, column=1, columnspan=2, padx=5, pady=10)

    # Reminder settings
    reminder_frame = ttk.LabelFrame(parent, text="Reminder Settings")
    reminder_frame.pack(fill="x", padx=10, pady=10)

    ttk.Label(reminder_frame, text="Reminder Interval (minutes):").grid(row=0, column=0, padx=5, pady=10, sticky="w")

    self.interval_var = tk.StringVar(value=str(self.user_data["reminder_interval"]))
    interval_entry = ttk.Entry(reminder_frame, width=10, textvariable=self.interval_var)
    interval_entry.grid(row=0, column=1, padx=5, pady=10)

    # Sound settings frame
    sound_frame = ttk.LabelFrame(parent, text="Sound Settings")
    sound_frame.pack(fill="x", padx=10, pady=10)

    # Test sound buttons
    ttk.Button(
      sound_frame,
      text="Test Reminder Sound",
      command=lambda: self.notification_manager.play_sound("reminder")
    ).grid(row=0, column=0, padx=5, pady=10)

    ttk.Button(
      sound_frame,
      text="Test Success Sound",
      command=lambda: self.notification_manager.play_sound("success")
    ).grid(row=0, column=1, padx=5, pady=10)

    ttk.Button(
      sound_frame,
      text="Test Water Drop Sound",
      command=lambda: self.notification_manager.play_sound("water_drop")
    ).grid(row=0, column=2, padx=5, pady=10)

    # Startup settings
    startup_frame = ttk.LabelFrame(parent, text="Startup Settings")
    startup_frame.pack(fill="x", padx=10, pady=10)

    self.startup_var = tk.BooleanVar(value=is_in_startup())
    startup_check = ttk.Checkbutton(
      startup_frame,
      text="Start application when computer boots",
      variable=self.startup_var,
      command=self.toggle_startup
    )
    startup_check.pack(pady=10)

    # Start minimized option
    self.minimized_var = tk.BooleanVar(value=self.user_data.get("start_minimized", False))
    minimized_check = ttk.Checkbutton(
      startup_frame,
      text="Start minimized to system tray",
      variable=self.minimized_var,
      command=lambda: self.update_user_data_field("start_minimized", self.minimized_var.get())
    )
    minimized_check.pack(pady=5)

    # Save settings button
    save_btn = ttk.Button(
      parent,
      text="Save and Calculate Recommended Intake",
      command=self.save_settings
    )
    save_btn.pack(pady=20)

    # Display current recommendation
    self.recommendation_label = ttk.Label(
      parent,
      text=f"Current recommended intake: {self.user_data['daily_target']} ml",
      font=("Arial", 12)
    )
    self.recommendation_label.pack(pady=10)

  def setup_reminders_tab(self, parent):
    # Frame for adding new reminders
    add_frame = ttk.LabelFrame(parent, text="Add New Reminder")
    add_frame.pack(fill="x", padx=10, pady=10)

    ttk.Label(add_frame, text="Hour (24-hour format):").grid(row=0, column=0, padx=5, pady=10, sticky="w")

    self.hour_var = tk.StringVar()
    hour_combo = ttk.Combobox(
      add_frame,
      textvariable=self.hour_var,
      values=[f"{i:02d}" for i in range(24)],
      width=5,
      state="readonly"
    )
    hour_combo.grid(row=0, column=1, padx=5, pady=10)
    hour_combo.set("08")  # Default to 8 AM

    ttk.Label(add_frame, text="Minute:").grid(row=0, column=2, padx=5, pady=10, sticky="w")

    self.minute_var = tk.StringVar()
    minute_combo = ttk.Combobox(
      add_frame,
      textvariable=self.minute_var,
      values=[f"{i:02d}" for i in range(0, 60, 5)],  # Every 5 minutes
      width=5,
      state="readonly"
    )
    minute_combo.grid(row=0, column=3, padx=5, pady=10)
    minute_combo.set("00")  # Default to XX:00

    add_btn = ttk.Button(
      add_frame,
      text="Add Reminder",
      command=self.add_custom_reminder
    )
    add_btn.grid(row=0, column=4, padx=10, pady=10)

    # Frame for listing existing reminders
    list_frame = ttk.LabelFrame(parent, text="Your Custom Reminders")
    list_frame.pack(fill="both", expand=True, padx=10, pady=10)

    # Create a treeview for reminders
    columns = ("time", "action")
    self.reminders_tree = ttk.Treeview(list_frame, columns=columns, show="headings")

    # Set column headings
    self.reminders_tree.heading("time", text="Reminder Time")
    self.reminders_tree.heading("action", text="Action")

    # Set column widths
    self.reminders_tree.column("time", width=150)
    self.reminders_tree.column("action", width=100)

    # Add scrollbar
    scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.reminders_tree.yview)
    self.reminders_tree.configure(yscrollcommand=scrollbar.set)

    # Pack the widgets
    self.reminders_tree.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    # Load existing reminders into the tree
    self.refresh_reminders_list()

    # Activate all reminders button
    activate_btn = ttk.Button(
      parent,
      text="Activate Custom Reminders",
      command=self.activate_custom_reminders
    )
    activate_btn.pack(pady=10)

    # Stop custom reminders button
    stop_btn = ttk.Button(
      parent,
      text="Stop Custom Reminders",
      command=lambda: self.reminder_scheduler.stop_reminders()
    )
    stop_btn.pack(pady=5)

  def add_custom_reminder(self):
    try:
      hour = int(self.hour_var.get())
      minute = int(self.minute_var.get())

      if 0 <= hour < 24 and 0 <= minute < 60:
        # Add reminder
        reminder_id = self.reminder_scheduler.add_reminder(hour, minute)
        self.save_user_data()
        self.refresh_reminders_list()

        # Show confirmation
        messagebox.showinfo(
          "Reminder Added",
          f"Reminder set for {hour:02d}:{minute:02d}"
        )
      else:
        messagebox.showerror("Invalid Time", "Please enter a valid time (0-23 hours, 0-59 minutes)")
    except ValueError:
      messagebox.showerror("Invalid Input", "Please enter valid numbers for hour and minute")

  def refresh_reminders_list(self):
    # Clear existing items
    for item in self.reminders_tree.get_children():
      self.reminders_tree.delete(item)

    # Add reminders to the tree
    for hour, minute, reminder_id in self.reminder_scheduler.get_all_reminders():
      item_id = self.reminders_tree.insert(
        "",
        "end",
        values=(f"{hour:02d}:{minute:02d}", ""),
        tags=(reminder_id,)
      )

      # Add a delete button
      self.reminders_tree.set(item_id, "action", "Delete")

    # Add button click binding
    self.reminders_tree.bind("<ButtonRelease-1>", self.on_reminder_tree_click)

  def on_reminder_tree_click(self, event):
    # Get the item that was clicked
    region = self.reminders_tree.identify_region(event.x, event.y)
    column = self.reminders_tree.identify_column(event.x)

    if region == "cell" and column == "#2":  # Action column
      item_id = self.reminders_tree.identify_row(event.y)
      if item_id:
        tags = self.reminders_tree.item(item_id, "tags")
        if tags:
          reminder_id = tags[0]

          # Confirm deletion
          if messagebox.askyesno("Delete Reminder", "Are you sure you want to delete this reminder?"):
            self.reminder_scheduler.remove_reminder(reminder_id)
            self.save_user_data()
            self.refresh_reminders_list()

  def activate_custom_reminders(self):
    if not self.reminder_scheduler.get_all_reminders():
      messagebox.showinfo("No Reminders", "You don't have any custom reminders set up yet.")
      return

    self.reminder_scheduler.schedule_reminders()
    messagebox.showinfo(
      "Reminders Activated",
      "Your custom reminders have been activated!"
    )

  def toggle_sound(self):
    self.user_data["sound_enabled"] = self.sound_var.get()
    self.save_user_data()

  def toggle_startup(self):
    if self.startup_var.get():
      success, message = add_to_startup()
      if not success:
        self.startup_var.set(False)
        messagebox.showerror("Error", message)
      else:
        messagebox.showinfo("Success", message)
    else:
      success, message = remove_from_startup()
      if not success:
        self.startup_var.set(True)
        messagebox.showerror("Error", message)
      else:
        messagebox.showinfo("Success", message)

  def update_user_data_field(self, field, value):
    """Update a single field in user_data and save"""
    self.user_data[field] = value
    self.save_user_data()

  def save_settings(self):
    try:
      weight = float(self.weight_var.get())
      interval = int(self.interval_var.get())

      if weight <= 0 or interval <= 0:
        messagebox.showerror("Invalid Input", "Weight and interval must be positive numbers")
        return

      self.user_data["weight"] = weight
      self.user_data["weight_unit"] = self.weight_unit_var.get()
      self.user_data["activity_level"] = self.activity_var.get()
      self.user_data["reminder_interval"] = interval

      # Calculate recommended intake
      daily_target = calculate_water_intake(
        weight,
        self.weight_unit_var.get(),
        self.activity_var.get()
      )
      self.user_data["daily_target"] = daily_target

      self.save_user_data()
      self.update_ui()

      messagebox.showinfo(
        "Settings Saved",
        f"Your settings have been saved.\nRecommended daily water intake: {daily_target} ml"
      )
    except ValueError:
      messagebox.showerror("Invalid Input", "Please enter valid numbers for weight and interval")

  def add_water(self, amount):
    # Check if date has changed
    current_date = datetime.now().strftime("%Y-%m-%d")
    if current_date != self.user_data["last_reset_date"]:
      self.user_data["current_intake"] = 0
      self.user_data["last_reset_date"] = current_date

    self.user_data["current_intake"] += amount
    self.save_user_data()
    self.update_ui()

    # Play water drop sound
    if self.user_data.get("sound_enabled", True):
      self.notification_manager.play_sound("water_drop")

    # Show congratulation if target reached
    if self.user_data["current_intake"] >= self.user_data["daily_target"] and \
      self.user_data["current_intake"] - amount < self.user_data["daily_target"]:
      messagebox.showinfo("Congratulations!", "You've reached your daily water intake goal!")

      # Play success sound
      if self.user_data.get("sound_enabled", True):
        self.notification_manager.play_sound("success")

  def reset_progress(self):
    if messagebox.askyesno("Reset Progress", "Are you sure you want to reset today's progress?"):
      self.user_data["current_intake"] = 0
      self.user_data["last_reset_date"] = datetime.now().strftime("%Y-%m-%d")
      self.save_user_data()
      self.update_ui()

  def update_ui(self):
    self.target_label.config(text=f"{self.user_data['daily_target']} ml")
    self.intake_label.config(text=f"{self.user_data['current_intake']} ml")
    self.recommendation_label.config(text=f"Current recommended intake: {self.user_data['daily_target']} ml")
    self.update_progress()

  def update_progress(self):
    if self.user_data["daily_target"] > 0:
      progress = (self.user_data["current_intake"] / self.user_data["daily_target"]) * 100
      progress = min(progress, 100)  # Cap at 100%
    else:
      progress = 0
    self.progress_var.set(progress)

  def toggle_reminder(self):
    if self.reminder_active:
      self.reminder_active = False
      self.reminder_btn_text.set("Start Reminders")
      self.status_label.config(text="Reminders inactive")
      self.user_data["reminder_active"] = False
      self.save_user_data()
    else:
      self.reminder_active = True
      self.reminder_btn_text.set("Stop Reminders")
      self.status_label.config(text="Reminders active")
      self.user_data["reminder_active"] = True
      self.save_user_data()

      if self.reminder_thread is None or not self.reminder_thread.is_alive():
        self.reminder_thread = threading.Thread(target=self.reminder_loop, daemon=True)
        self.reminder_thread.start()

  def reminder_loop(self):
    while self.reminder_active:
      # Sleep for the specified interval (in minutes)
      for _ in range(self.user_data["reminder_interval"] * 60):
        time.sleep(1)
        if not self.reminder_active:
          return

      # Show notification
      sound = "reminder" if self.user_data.get("sound_enabled", True) else None
      self.notification_manager.send_notification(
        "Water Reminder",
        "Time to drink water! Stay hydrated.",
        sound=sound
      )

  def handle_system_resume(self):
    """Reset timers when system wakes from sleep"""
    last_time = time.time()

    def check_time():
      nonlocal last_time
      while True:
        time.sleep(5)  # Check every 5 seconds
        current_time = time.time()

        # If more than 60 seconds have passed (system was likely asleep)
        if current_time - last_time > 60:
          # Reset reminder timers
          if self.reminder_active:
            if self.reminder_thread is not None and not self.reminder_thread.is_alive():
              self.reminder_thread = threading.Thread(target=self.reminder_loop, daemon=True)
              self.reminder_thread.start()

        last_time = current_time

    # Start the time checking thread
    time_thread = threading.Thread(target=check_time, daemon=True)
    time_thread.daemon = True
    time_thread.start()


if __name__ == "__main__":
  root = tk.Tk()
  app = WaterReminderApp(root)
  root.mainloop()