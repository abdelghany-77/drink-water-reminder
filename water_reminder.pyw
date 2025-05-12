import os
import sys
import subprocess
from datetime import datetime

# Record the startup info
with open("startup_log.txt", "a") as log:
  log.write(f"Application started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

# Get the script directory
script_dir = os.path.dirname(os.path.abspath(__file__))

# Set environment variables
os.environ['USERNAME'] = 'abdelghany-77'
os.environ['LAST_LOGIN'] = '2025-05-11 16:54:02'

# Launch the main script with no console
try:
  # Check for any command line arguments to pass through
  args = sys.argv[1:] if len(sys.argv) > 1 else []

  # Start the main application
  pythonw = sys.executable.replace('python.exe', 'pythonw.exe')
  if not os.path.exists(pythonw):
    pythonw = sys.executable

  subprocess.Popen([pythonw, os.path.join(script_dir, "main.py")] + args,
                   creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0)
except Exception as e:
  with open("error_log.txt", "a") as error_log:
    error_log.write(f"Error launching app: {e}\n")