import threading
import time
from datetime import datetime, timedelta


class ReminderScheduler:
  def __init__(self, notification_manager):
    self.notification_manager = notification_manager
    self.custom_reminders = []  # List of (hour, minute, reminder_id) tuples
    self.scheduled_reminders = {}  # Dictionary of active reminders
    self.stop_flag = threading.Event()
    self.scheduler_thread = None

  def add_reminder(self, hour, minute, reminder_id=None):
    """Add a new custom reminder time"""
    if reminder_id is None:
      reminder_id = f"reminder_{len(self.custom_reminders)}"

    # Check for duplicate time
    for h, m, _ in self.custom_reminders:
      if h == hour and m == minute:
        return None  # Don't add duplicates

    self.custom_reminders.append((hour, minute, reminder_id))
    self.custom_reminders.sort()  # Sort by time
    return reminder_id

  def remove_reminder(self, reminder_id):
    """Remove a custom reminder by ID"""
    for i, (hour, minute, rid) in enumerate(self.custom_reminders):
      if rid == reminder_id:
        self.custom_reminders.pop(i)
        return True
    return False

  def get_next_occurrence(self, hour, minute):
    """Get the next occurrence of a given time"""
    now = datetime.now()
    target_time = now.replace(hour=hour, minute=minute, second=0, microsecond=0)

    if target_time <= now:
      # If the time has already passed today, schedule for tomorrow
      target_time += timedelta(days=1)

    return target_time

  def schedule_reminders(self):
    """Schedule all custom reminders"""
    self.stop_flag.clear()

    if not self.custom_reminders:
      return False

    if self.scheduler_thread and self.scheduler_thread.is_alive():
      return True  # Already running

    def reminder_thread():
      while not self.stop_flag.is_set():
        now = datetime.now()

        for hour, minute, reminder_id in self.custom_reminders:
          next_time = self.get_next_occurrence(hour, minute)
          seconds_to_wait = (next_time - now).total_seconds()

          if 0 <= seconds_to_wait < 60:  # If reminder is due within the next minute
            time.sleep(seconds_to_wait)
            if not self.stop_flag.is_set():
              self.notification_manager.send_notification(
                "Water Reminder",
                f"It's {hour:02d}:{minute:02d}! Time to drink water!",
                sound="reminder"
              )

        # Sleep for a bit to avoid busy waiting
        time.sleep(30)

    self.scheduler_thread = threading.Thread(target=reminder_thread, daemon=True)
    self.scheduler_thread.start()
    return True

  def stop_reminders(self):
    """Stop all scheduled reminders"""
    self.stop_flag.set()
    if self.scheduler_thread and self.scheduler_thread.is_alive():
      self.scheduler_thread.join(1.0)  # Wait for thread to end with timeout
    self.scheduler_thread = None
    return True

  def get_all_reminders(self):
    """Get all custom reminders"""
    return self.custom_reminders

  def load_reminders(self, reminders_list):
    """Load reminders from a list"""
    self.custom_reminders = []
    for reminder in reminders_list:
      if len(reminder) >= 2:  # At minimum, we need hour and minute
        hour = reminder[0]
        minute = reminder[1]
        reminder_id = reminder[2] if len(reminder) > 2 else None
        self.add_reminder(hour, minute, reminder_id)

  def to_list(self):
    """Convert reminders to a list for storage"""
    return self.custom_reminders