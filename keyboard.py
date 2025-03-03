import socket
import struct
from pynput.mouse import Controller as MouseController, Listener as MouseListener, Button
from pynput.keyboard import Controller as KeyboardController, Listener as KeyboardListener, Key

mouse = MouseController()
keyboard = KeyboardController()

# Change this to the **host machine's** IP address
HOST_IP = "192.168.1.100"  # Example IP, replace with your actual host IP
PORT = 5005

client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

print("✅ Client is controlling the host's mouse and keyboard...")

def send_data(x, y, click=0, key_code=0, key_action=0):
    """Send mouse position, clicks, and key presses to the host."""
    data = struct.pack("iiHhi", x, y, click, key_code, key_action)  # Fix: Use `Hh` for click & key_code
    client.sendto(data, (HOST_IP, PORT))

def on_move(x, y):
    """Send live mouse movement data to the host."""
    send_data(x, y)

def on_click(x, y, button, pressed):
    """Send mouse click events."""
    click = 1 if button == Button.left else 2 if button == Button.right else 0
    if pressed:
        send_data(x, y, click)

def on_press(key):
    """Send keyboard press event."""
    try:
        if hasattr(key, 'char') and key.char is not None:
            key_code = ord(key.char)  # Get ASCII value of key
        elif key in Key.__dict__.values():  # Special keys (Ctrl, Shift, etc.)
            key_code = list(Key.__dict__.values()).index(key) + 128  # Assign a unique code
        else:
            key_code = 0
    except AttributeError:
        key_code = 0

    send_data(mouse.position[0], mouse.position[1], click=0, key_code=key_code, key_action=1)  # Key Press

def on_release(key):
    """Send keyboard release event."""
    try:
        if hasattr(key, 'char') and key.char is not None:
            key_code = ord(key.char)
        elif key in Key.__dict__.values():
            key_code = list(Key.__dict__.values()).index(key) + 128
        else:
            key_code = 0
    except AttributeError:
        key_code = 0

    send_data(mouse.position[0], mouse.position[1], click=0, key_code=key_code, key_action=0)  # Key Release

# Start listening for mouse and keyboard events
with MouseListener(on_move=on_move, on_click=on_click) as mouse_listener, KeyboardListener(on_press=on_press, on_release=on_release) as keyboard_listener:
    mouse_listener.join()
    keyboard_listener.join()
