import sys
import socket
import os
import threading
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QObject, pyqtSignal
from database import init_db, save_clip
from daemon import ClipboardListener
from ui import ContextFlowWindow

PORT = 54123  # unique port for ContextFlow single-instance check

class SignalBridge(QObject):
    show_signal = pyqtSignal()

def check_single_instance():
    # try to connect to existing instance
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect(('127.0.0.1', PORT))
        s.send(b'SHOW')
        s.close()
        return True # already running, signal sent
    except (ConnectionRefusedError, OSError):
        s.close()
        return False # not running, we are the first

def start_socket_server(bridge):
    # listen for activation signals from hotkey
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        server.bind(('127.0.0.1', PORT))
        server.listen(1)
    except Exception:
        return

    while True:
        try:
            conn, _ = server.accept()
            data = conn.recv(1024)
            if data == b'SHOW':
                # safely emit signal to main thread
                bridge.show_signal.emit()
            conn.close()
        except Exception:
            break

def main():
    init_db()
    app = QApplication(sys.argv)
    
    # if already running, just trigger show via socket and exit
    if check_single_instance():
        print("ContextFlow is already running. Brought window to front.")
        sys.exit(0)
        
    window = ContextFlowWindow()
    
    # bridge for safe cross-thread GUI invocation
    bridge = SignalBridge()
    bridge.show_signal.connect(window.toggle_window)
    
    # background listener thread for clipboard
    listener = ClipboardListener(app.clipboard())
    
    def handle_new_clip(content, category):
        save_clip(content, category)
        window.clip_added.emit(content, category)

    listener.new_clip.connect(handle_new_clip)
    listener.start()
    
    # start socket server in background to catch hotkey calls
    server_thread = threading.Thread(target=start_socket_server, args=(bridge,), daemon=True)
    server_thread.start()
    
    print("ContextFlow daemon started.")
    sys.exit(app.exec())

if __name__ == "__main__":
    main()