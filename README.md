# ContextFlow

ContextFlow is a lightweight, system-wide clipboard manager built in Python using PyQt6 and SQLite. It features single-instance architecture via local sockets, global hotkey toggling, automatic categorization of clips (text, links, code, images), and a clean modern interface with dark and light themes.

## Architecture

ContextFlow runs as a background daemon process. When launched, it checks for an existing instance on a dedicated TCP port (`54123`). If an instance is already running, a trigger signal (`SHOW`) is sent to bring the existing window to the foreground, preventing duplicate processes.

- **`main.py`**: Application entry point, single-instance TCP server, and PyQt event loop coordinator.
- **`ui.py`**: Graphical user interface, list management, quick copy shortcuts (`1-9`), tray icon integration, and theme engine.
- **`daemon.py`**: Background monitoring thread for system clipboard changes.
- **`database.py`**: SQLite data persistence layer for history and favorites management.
- **`toggle.py`**: Lightweight CLI utility that signals the running daemon to toggle window visibility.

## Features

- **System-Wide Hotkey**: Toggle the application window instantly using a custom shortcut.
- **Single-Instance Daemon**: Efficient resource usage with local socket communication.
- **Smart Categorization**: Automatically identifies and tags copied content as Text, Links, Code, or Images.
- **Quick Copy**: Use number keys (`1-9`) to quickly copy items from the visible history or favorites list.
- **Dual Themes**: Built-in support for dark and light UI styles.
- **System Tray Integration**: Runs quietly in the background with tray menu controls.

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/gri3ex/ContextFlow.git
   cd ContextFlow

2. **Create and activate a virtual environment:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate

3. **Install dependencies:**
    ```bash
    pip install -r requirements.txt

## Usage

ContextFlow is designed to run as a background daemon accompanied by a toggle script for hotkey activation. The application workflow relies on starting the main background process and configuring system-level triggers to interface with it via local sockets.

Integration into the desktop environment involves setting up the background daemon to launch automatically during system startup, and mapping a global shortcut (such as `Ctrl + Shift + Space`) to execute the toggle script, allowing the user to seamlessly bring up or hide the clipboard manager from anywhere in the operating system.

### Background Startup Configuration
To ensure the daemon runs automatically when your desktop session starts, create a standard desktop entry file within your user configuration directory at `~/.config/autostart/contextflow.desktop`. This configuration file specifies the execution path using your virtual environment's Python interpreter pointing directly to the main daemon script:

```ini
[Desktop Entry]
Type=Application
Exec=/path/to/your/project/venv/bin/python /path/to/your/project/main.py
Hidden=false
NoDisplay=false
X-GNOME-Autostart-enabled=true
Name=ContextFlow
Comment=Clipboard manager background daemon
```

Global Shortcut Integration
To bind a system-wide hotkey that opens or hides the application window instantly:

1. Open your desktop environment's system settings and navigate to the keyboard shortcuts section (typically found under **Settings** -> **Keyboard** -> **Custom Shortcuts**).
2. Create a new custom command with an identifier such as `ContextFlow Toggle`.
3. Set the target command path to execute your toggle utility through the project's virtual environment python interpreter:
   ```bash
   /path/to/your/project/venv/bin/python /path/to/your/project/toggle.py

Assign the key combination Ctrl + Shift + Space to the shortcut and save the configuration.

