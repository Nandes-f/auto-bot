# Screen Automation Tool

A Python-based automation tool that helps manage Screen sessions with customizable settings and system tray integration.

## Features

- System tray integration for easy access
- Customizable session duration and action intervals
- Automatic actions to maintain session activity
- Settings dialog for easy configuration
- Startup integration
- Session countdown timer
- Clean session finalization

## Requirements

- Python 3.x
- PyQt5
- pyautogui
- Windows OS

## Installation

1. Clone this repository or download the source code
2. Install the required dependencies:
```bash
pip install PyQt5 pyautogui
```

## Usage

1. Run the application:
```bash
python app.py
```

2. The application will start in the system tray
3. Double-click the tray icon to open the control panel
4. Configure your settings:
   - Session duration (in minutes)
   - Action interval (in seconds)
5. Click "Start" to begin the automation session

## Features in Detail

### Control Panel
- Start/Stop button
- Status indicator
- Remaining time display
- Settings access

### System Tray
- Quick access to all features
- Status monitoring
- Session control
- Easy exit option

### Settings
- Customize session duration (1-9999 minutes)
- Adjust action interval (5-120 seconds)

## License

This project is open source and available under the MIT License.

## Contributing

Feel free to submit issues and enhancement requests! 
