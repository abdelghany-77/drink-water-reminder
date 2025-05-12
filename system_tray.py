import os
import sys
import tkinter as tk
from PIL import Image, ImageTk

# For Windows and Linux
try:
  import pystray
  from pystray import MenuItem as item

  HAS_PYSTRAY = True
except ImportError:
  HAS_PYSTRAY = False
  print("pystray package not found. System tray functionality will be disabled.")
  print("Install it with: pip install pystray")


class SystemTray:
  def __init__(self, root, app, icon_path):
    self.root = root
    self.app = app
    self.icon_path = icon_path
    self.tray_icon = None
    self.tray_thread = None

    # Make window withdraw instead of destroy on close
    self.root.protocol("WM_DELETE_WINDOW", self.hide_window)

    # Remove from taskbar (Windows specific)
    self.make_window_invisible_in_taskbar()

    # Initial visibility
    self.is_visible = True

    if HAS_PYSTRAY and os.path.exists(icon_path):
      self.setup_tray()
    else:
      print(f"System tray disabled. Icon path exists: {os.path.exists(icon_path)}")
      # Keep window visible if no tray support
      self.is_visible = True
      self.show_window()

  def make_window_invisible_in_taskbar(self):
    """Make the window not appear in the taskbar"""
    try:
      # For Windows
      if sys.platform == "win32":
        # This makes the window not appear in taskbar
        self.root.attributes("-toolwindow", True)

        # This makes it a "system tray only" application
        GWL_EXSTYLE = -20
        WS_EX_APPWINDOW = 0x00040000
        WS_EX_TOOLWINDOW = 0x00000080

        try:
          import ctypes
          hwnd = ctypes.windll.user32.GetParent(self.root.winfo_id())
          style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
          style = style & ~WS_EX_APPWINDOW
          style = style | WS_EX_TOOLWINDOW
          ctypes.windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, style)
        except Exception as e:
          print(f"Could not remove from taskbar: {e}")

      # For Linux
      elif sys.platform.startswith('linux'):
        self.root.attributes("-type", "splash")
        # This only works on some window managers, might need more specific handling

      # For macOS
      elif sys.platform == "darwin":
        self.root.createcommand('::tk::mac::ReopenApplication', self.show_window)
        self.root.createcommand('::tk::mac::Quit', self.exit_app)
        # NSApplicationActivationPolicyAccessory = 1
        # This requires PyObjC which is a larger dependency
    except Exception as e:
      print(f"Error configuring window: {e}")

  def setup_tray(self):
    """Set up the system tray icon and menu"""
    try:
      image = Image.open(self.icon_path)

      # Create menu items
      menu = (
        item('Show', self.show_window),
        item('Hide', self.hide_window),
        item('Add Water', self.add_water_menu),
        item('Toggle Reminders', self.toggle_reminders),
        item('Exit', self.exit_app)
      )

      # Create tray icon
      self.tray_icon = pystray.Icon("WaterReminder", image, "Water Reminder", menu)

      # Start the icon in a separate thread
      import threading
      self.tray_thread = threading.Thread(target=self.tray_icon.run)
      self.tray_thread.daemon = True
      self.tray_thread.start()

      print("System tray icon initialized successfully")
    except Exception as e:
      print(f"Error setting up system tray: {e}")

  def add_water_menu(self):
    """Show submenu for adding water"""
    try:
      from pystray import Menu, MenuItem as item

      # Create water amount menu
      amounts = [100, 200, 300, 500]
      water_menu = Menu(
        *[item(f"{amount} ml", lambda _, a=amount: self.add_water(a)) for amount in amounts]
      )

      return water_menu
    except Exception as e:
      print(f"Error creating water menu: {e}")
      # Fallback to 200ml
      self.add_water(200)

  def add_water(self, amount):
    """Add water from system tray"""
    try:
      self.app.add_water(amount)
      # Show notification
      self.app.notification_manager.send_notification(
        "Water Added",
        f"Added {amount} ml of water!",
        sound="water_drop" if self.app.user_data.get("sound_enabled", True) else None
      )
    except Exception as e:
      print(f"Error adding water from tray: {e}")

  def toggle_reminders(self):
    """Toggle reminders from system tray"""
    try:
      self.app.toggle_reminder()
    except Exception as e:
      print(f"Error toggling reminders from tray: {e}")

  def show_window(self):
    """Show the main window"""
    self.is_visible = True
    self.root.deiconify()
    self.root.lift()
    self.root.focus_force()

    # Ensure it's on top temporarily (helps with focus issues)
    self.root.attributes('-topmost', True)
    self.root.update()
    self.root.attributes('-topmost', False)

  def hide_window(self):
    """Hide the main window"""
    self.is_visible = False
    self.root.withdraw()

  def exit_app(self):
    """Properly exit the application"""
    try:
      if self.tray_icon:
        self.tray_icon.stop()

      self.root.destroy()
      sys.exit(0)
    except Exception as e:
      print(f"Error during exit: {e}")
      # Force exit if normal exit fails
      os._exit(0)

  def toggle_window(self):
    """Toggle window visibility"""
    if self.is_visible:
      self.hide_window()
    else:
      self.show_window()