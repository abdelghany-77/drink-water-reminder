import os
import sys
import platform

def add_to_startup():
  """Add the app to the system's startup programs"""
  try:
    system = platform.system()
    script_path = os.path.abspath(sys.argv[0])
    app_dir = os.path.dirname(script_path)
    main_script = os.path.join(app_dir, "main.py")

    if system == "Windows":
      import winreg

      # Update the Windows batch file creation in add_to_startup() function
      bat_path = os.path.join(app_dir, "start_water_reminder.bat")
      with open(bat_path, 'w') as bat_file:
        bat_file.write(f'''@echo off
      cd /d "{app_dir}"
      start /min "" pythonw "{main_script}" --minimized
      exit
      ''')

      # Add to registry
      key = winreg.OpenKey(
        winreg.HKEY_CURRENT_USER,
        r"Software\Microsoft\Windows\CurrentVersion\Run",
        0, winreg.KEY_SET_VALUE
      )
      winreg.SetValueEx(
        key,
        "WaterReminder",
        0,
        winreg.REG_SZ,
        bat_path
      )
      return True, "Added to Windows startup programs"

    elif system == "Darwin":  # macOS
      # Create startup agent
      plist_path = os.path.expanduser("~/Library/LaunchAgents/com.user.waterreminder.plist")
      plist_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.user.waterreminder</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/python3</string>
        <string>{main_script}</string>
        <string>--minimized</string>
    </array>
    <key>EnvironmentVariables</key>
    <dict>
        <key>AUTO_STARTED</key>
        <string>1</string>
    </dict>
    <key>RunAtLoad</key>
    <true/>
</dict>
</plist>'''
      with open(plist_path, 'w') as plist_file:
        plist_file.write(plist_content)

      # Load the agent
      os.system(f"launchctl load {plist_path}")
      return True, "Added to macOS startup programs"

    elif system == "Linux":
      # Create desktop entry
      autostart_dir = os.path.expanduser("~/.config/autostart")
      if not os.path.exists(autostart_dir):
        os.makedirs(autostart_dir)

      desktop_path = os.path.join(autostart_dir, "waterreminder.desktop")
      desktop_content = f'''[Desktop Entry]
Type=Application
Name=Water Reminder
Exec=env AUTO_STARTED=1 /usr/bin/python3 {main_script} --minimized
Hidden=false
NoDisplay=false
X-GNOME-Autostart-enabled=true
'''
      with open(desktop_path, 'w') as desktop_file:
        desktop_file.write(desktop_content)

      # Make executable
      os.chmod(desktop_path, 0o755)
      return True, "Added to Linux startup programs"

    else:
      return False, f"Unsupported operating system: {system}"

  except Exception as e:
    return False, f"Error adding to startup: {str(e)}"


def remove_from_startup():
  """Remove the app from the system's startup programs"""
  try:
    system = platform.system()

    if system == "Windows":
      import winreg

      # Remove from registry
      key = winreg.OpenKey(
        winreg.HKEY_CURRENT_USER,
        r"Software\Microsoft\Windows\CurrentVersion\Run",
        0, winreg.KEY_SET_VALUE
      )

      try:
        winreg.DeleteValue(key, "WaterReminder")
        return True, "Removed from Windows startup programs"
      except:
        return False, "App was not in startup programs"

    elif system == "Darwin":  # macOS
      # Unload and remove plist
      plist_path = os.path.expanduser("~/Library/LaunchAgents/com.user.waterreminder.plist")
      if os.path.exists(plist_path):
        os.system(f"launchctl unload {plist_path}")
        os.remove(plist_path)
        return True, "Removed from macOS startup programs"
      else:
        return False, "App was not in startup programs"

    elif system == "Linux":
      # Remove desktop entry
      desktop_path = os.path.expanduser("~/.config/autostart/waterreminder.desktop")
      if os.path.exists(desktop_path):
        os.remove(desktop_path)
        return True, "Removed from Linux startup programs"
      else:
        return False, "App was not in startup programs"

    else:
      return False, f"Unsupported operating system: {system}"

  except Exception as e:
    return False, f"Error removing from startup: {str(e)}"


def is_in_startup():
  """Check if the app is configured to run on startup"""
  system = platform.system()

  if system == "Windows":
    import winreg
    try:
      key = winreg.OpenKey(
        winreg.HKEY_CURRENT_USER,
        r"Software\Microsoft\Windows\CurrentVersion\Run",
        0, winreg.KEY_READ
      )
      winreg.QueryValueEx(key, "WaterReminder")
      return True
    except:
      return False

  elif system == "Darwin":  # macOS
    plist_path = os.path.expanduser("~/Library/LaunchAgents/com.user.waterreminder.plist")
    return os.path.exists(plist_path)

  elif system == "Linux":
    desktop_path = os.path.expanduser("~/.config/autostart/waterreminder.desktop")
    return os.path.exists(desktop_path)

  return False