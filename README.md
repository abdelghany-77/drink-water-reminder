# Water Reminder Desktop Application
![water_icon](https://github.com/user-attachments/assets/978fa175-58b8-4e48-acd4-f8d953368c56)

## Overview

Water Reminder is a desktop application built with Python that helps you stay hydrated throughout the day. It provides personalized water intake recommendations, customizable reminders, and tracks daily water consumption in a simple, easy-to-use interface.

**Latest Version:** 1.0.0 (Released: 2025-05-12)

## Features

- **Personalized Water Intake Calculation**: Recommends your optimal daily water intake based on weight and activity level
- **Customizable Reminders**: Set both interval-based and time-specific reminders
- **Sound Alerts**: Audio notifications when it's time to drink water
- **Progress Tracking**: Visual display of your daily hydration progress
- **System Tray Integration**: Runs in the background with quick access from the system tray
- **Auto-startup**: Optionally starts with your computer

## Screenshots
![Screenshot 2025-05-12 164907](https://github.com/user-attachments/assets/3063bbd7-764b-4fc4-93e0-3ec31153cfd8)
![Screenshot 2025-05-12 164846](https://github.com/user-attachments/assets/9bc08c0f-6430-4e91-b8f2-7d87efee2db6)
![Screenshot 2025-05-12 164930](https://github.com/user-attachments/assets/1ea0aa96-395a-4e67-9d30-89d2d56eafd3)

### Prerequisites
- Python 3.7 or higher
- Pip package manager

### Dependencies
The application requires the following Python libraries:
```
pygame
plyer
pillow
pystray
```

### Quick Install

1. Clone the repository:
```bash
git clone https://github.com/abdelghany-77/water-reminder.git
cd water-reminder
```

2. Run the application:
```bash
python main.py
```

### Initial Setup
1. When you first launch the app, go to the Settings tab
2. Enter your weight and select your activity level
3. The app will calculate your recommended daily water intake
4. Adjust reminder settings as needed
5. Click "Save and Calculate Recommended Intake"

### Daily Use
1. Use the "+" buttons on the Dashboard to log your water intake
2. The progress bar shows your progress toward your daily goal
3. Click "Start Reminders" to activate notifications
4. You can minimize the app to the system tray with the close button

### Custom Reminders
1. Go to the "Custom Reminders" tab to set specific reminder times
2. Click "Add Reminder" after selecting the desired time
3. Click "Activate Custom Reminders" to enable time-based notifications

## Building from Source

To build the application as a standalone executable:

1. Install PyInstaller:
```bash
pip install pyinstaller
```

2. Build the application:
```bash
pyinstaller --name "Water Reminder" --icon=images/water_icon.ico --windowed --add-data "images;images" --add-data "sounds;sounds" main.py
```
## Acknowledgments

- Sound effects from [Freesound.org](https://freesound.org)
- Icons from [Flaticon](https://www.flaticon.com)


**Stay hydrated! 💧**
