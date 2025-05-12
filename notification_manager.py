from plyer import notification
import os
import platform
import pygame  # Add pygame for sound effects


class NotificationManager:
  def __init__(self):
    self.app_name = "Water Reminder"
    self.icon_path = self.get_icon_path()

    # Initialize pygame mixer for sounds
    try:
      pygame.mixer.init()
      self.sounds = self.load_sounds()
    except Exception as e:
      print(f"Error initializing sound system: {e}")
      self.sounds = {}

  def get_icon_path(self):
    """Get the appropriate icon path based on the operating system"""
    base_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "images", "water_icon.png")
    if os.path.exists(base_path):
      return base_path
    return None

  def load_sounds(self):
    """Load sound files"""
    sounds_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sounds")
    sounds = {}

    # Create sounds directory if it doesn't exist
    if not os.path.exists(sounds_dir):
      try:
        os.makedirs(sounds_dir)
        print(f"Created sounds directory at {sounds_dir}")
      except Exception as e:
        print(f"Failed to create sounds directory: {e}")

    sound_files = {
      "water_drop": "reminder.wav",
      "success": "success.wav",
      "reminder": "water_drop.wav"
    }

    for name, filename in sound_files.items():
      path = os.path.join(sounds_dir, filename)
      if os.path.exists(path):
        try:
          sounds[name] = path
        except Exception as e:
          print(f"Failed to load sound {path}: {e}")
      else:
        print(f"Sound file not found: {path}")

    return sounds

  def play_sound(self, sound_name):
    """Play a sound by name"""
    if not self.sounds:
      print("No sounds available")
      return False

    if sound_name in self.sounds:
      try:
        sound = pygame.mixer.Sound(self.sounds[sound_name])
        sound.play()
        return True
      except Exception as e:
        print(f"Failed to play sound {sound_name}: {e}")
    else:
      print(f"Sound '{sound_name}' not found. Available sounds: {list(self.sounds.keys())}")
    return False

  def send_notification(self, title, message, sound=None):
    """Send a desktop notification with optional sound"""
    try:
      # Play sound if specified
      if sound and self.sounds:
        self.play_sound(sound)

      notification.notify(
        title=title,
        message=message,
        app_name=self.app_name,
        app_icon=self.icon_path,
        timeout=10  # seconds
      )
      return True
    except Exception as e:
      print(f"Failed to send notification: {e}")
      return False
      return False